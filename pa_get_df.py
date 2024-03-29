'''Get PurpleAir sensor data from PurpleAir and ThingSpeak API's for bounding box and date range. Add
   calculated AI to the data.
 
Args:
   start_time: (str)
      date and time of first measurement in the format "YYYY-MM-DD H:M:S"
   end_time: (str) 
      date and time of last measurement in the format "YYYY_MM_DD H:M:S"
   bbox: float (4)
      bounding box coordinates in the format lat1 lon1 lat2 lon2 for the SE and NW corners respectively
   interval: (str)
      The average data interval in minutes. minimum is two minutes

Returns:
   dfs: (dict, Pandas dataframe)

Notes:
   Description of operation:
      PurpleAir API is queried for a list of sensors within the bounding box.
      PurpleAir API is queried a second time for the ThingSpeak keys for each of the sensors
      ThingSpeak API is queried for the sensor historical readings.
      Returns dictionary of Pandas Data frame(s) of sensor readings for sensors within the bounding box during the provided start and end times.

   Todo: 
      rename variables consistently with names that are more appropriate to function
      exception handling
      Status and error logging
      add option to store data in local time vs UTC
      filter apparent bad sensor readings 
      Get both sensors data and exclude based on confidence
'''
 
 #James S. Lucas 20201222

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import config
import pandas as pd
import os
from time import sleep
import math
from collections import defaultdict
import ast
import io


def get_sensor_indexes(bbox, filename):
   '''Gets list of sensor indexes (aka ID's) from the PurpleAir API for sensors located within a bounding box.

      Args:
         bbox (list, float)
            bounding box coordinates in the format lat1 lon1 lat2 lon2 for the SE and NW corners respectively

      Returns:
         (List, List, str)
   '''
   metadata_path = config.root_path + os.path.sep + config.metadata_folder 
   metadata_filename = filename + " " + ' '.join(bbox) + ".txt"
   metadata_full_path = metadata_path + os.path.sep + metadata_filename
   root_url = "https://api.purpleair.com/v1/sensors"
   params = {
      'fields': "name,latitude,longitude,primary_id_a,primary_key_a,primary_id_b,primary_key_b,location_type",
      'nwlng': bbox[0],
      'selat': bbox[1],
      'selng': bbox[2],
      'nwlat': bbox[3]
      }
   url_template = root_url + "?fields={fields}&nwlng={nwlng}&nwlat={nwlat}&selng={selng}&selat={selat}"
   url = url_template.format(**params)
   try:
      sensor_ids = []
      header = {"X-API-Key":config.purpleair_read_key}
      #response will be a list of lists in the format 
      # [[sensor_id_1, sensor_name_1, location_type], [sensor_id_2, sensor_name_2, location_type]]
      response = requests.get(url, headers=header)
      if response.status_code == 200:
         sensors_data = json.loads(response.text)
         for sensor_list in sensors_data['data']:
            # if sensor_location is outside (0)
            if sensor_list[8] == 0:
               sensor_ids.append(sensor_list)
         print(" ")
         print(len(sensor_ids))
         print(" ")
         #print(sensor_ids)
         #print(" ")
         with open(metadata_full_path, 'w') as f:
            f.write(str(sensor_ids))
         return sensor_ids
      else:
         print("error no 200 response.")
   except Exception as e:
      print(e)


def date_range(start_time, end_time, intv):
   '''Used to break up the overall date range into a list of start and end times to comply with the imposed record limit
      for each ThingSpeak request.

      Args:
         start_time: (datetime)
         end_time: (datetime)
         intv: (int)
      
      Yields:
         (datetime)
   '''
   diff = (end_time  - start_time ) / intv
   for i in range(intv):
      yield (start_time + diff * i).strftime("%Y%m%d")
   yield end_time.strftime("%Y%m%d")


def calc_aqi(PM2_5):
   '''Calculates AQI value from provided raw particle density value.

      Args:
         PM2_5: (float)
            Raw particle density measurement
      
      Returns:
         Calculated AQI value: (int)
      
      Notes:
         Function takes the 24-hour rolling average PM2.5 value and calculates
         "AQI". "AQI" in quotes as this is not an official methodology. AQI is 
         24 hour midnight-midnight average. May change to NowCast or other
         methodology in the future.
   '''
   # Truncate to one decimal place.
   # There shouldn't be any NaN values as they have been filtered out but just in case.
   try:
      if (PM2_5 < 0) or math.isnan(PM2_5):
         PM2_5 = 0
   except TypeError as e:
         PM2_5 = 0
   PM2_5 = int(PM2_5 * 10) / 10.0
   #AQI breakpoints [0,    1,     2,    3    ]
   #                [Ilow, Ihigh, Clow, Chigh]
   pm25_aqi = {
      'good': [0, 50, 0, 12],
      'moderate': [51, 100, 12.1, 35.4],
      'sensitive': [101, 150, 35.5, 55.4],
      'unhealthy': [151, 200, 55.5, 150.4],
      'very': [201, 300, 150.5, 250.4],
      'hazardous': [301, 500, 250.5, 500.4],
      'beyond_aqi': [301, 500, 250.5, 500.4]
      }
   try:
      if (0.0 <= PM2_5 <= 12.0):
         aqi_cat = 'good'
      elif (12.1 <= PM2_5 <= 35.4):
         aqi_cat = 'moderate'
      elif (35.5 <= PM2_5 <= 55.4):
         aqi_cat = 'sensitive'
      elif (55.5 <= PM2_5 <= 150.4):
         aqi_cat = 'unhealthy'
      elif (150.5 <= PM2_5 <= 250.4):
         aqi_cat = 'very'
      elif (250.5 <= PM2_5 <= 500.4):
         aqi_cat = 'hazardous'
      elif (PM2_5 >= 500.5):
         aqi_cat = 'beyond_aqi'
      else:
         print(" ")
         print(f"PM2_5: {PM2_5}")
      Ihigh = pm25_aqi.get(aqi_cat)[1]
      Ilow = pm25_aqi.get(aqi_cat)[0]
      Chigh = pm25_aqi.get(aqi_cat)[3]
      Clow = pm25_aqi.get(aqi_cat)[2]
      Ipm25 = int(round(
         ((Ihigh - Ilow) / (Chigh - Clow) * (PM2_5 - Clow) + Ilow)
         ))
      return Ipm25
   except Exception as e:
      pass
      print(f"error in calc_aqi() function: {e}")
 

def get_ts_data(sensor_ids, start_time, end_time, interval, channel):
   '''Gets sensor readings from the ThingSpeak API.

      Args:
         sensor_ids: (list, str)
         start_time: (datetime)
         end_time: (datetime)
         interval: (int)

      Returns:
         (Pandas dataframe)
   '''
   import sys
   session = requests.Session()
   retry = Retry(connect=3, backoff_factor=0.5)
   adapter = HTTPAdapter(max_retries=retry)
   session.mount('http://', adapter)
   session.mount('https://', adapter)
   url_params = defaultdict(dict)
   df_a = None
   df_b = None
   delta = end_time - start_time
   rows = delta.days * 24 * 60 / int(interval)
   intv = int(math.ceil(rows / 7800))
   if intv < 1:
      intv = 1
   data_range = list(date_range(start_time, end_time, intv)) 
   num_sensors = len(sensor_ids)
   request_num = 0
   root_url = 'https://api.thingspeak.com/channels/{ts_channel}/feeds.csv?api_key={api_key}&start={start}%2000:00:00&end={end}%2023:59:59&average={average}'
   for idx, sensor in enumerate(sensor_ids):
      sensor_name = sensor[1]
      lat = sensor[2]
      lon = sensor[3]
      for t in range(0, intv):
         request_num += 1
         start_time = data_range[t]
         end_time = data_range[t+1]
         if channel == 'a' or channel == 'ab':
            url_params['a']['ts_channel'] = sensor[4]
            url_params['a']['api_key'] = sensor[5]
            url_params['a']['start'] = start_time
            url_params['a']['end'] = end_time
            url_params['a']['average'] = interval
         if channel == 'b' or channel == 'ab':
            url_params['b']['ts_channel'] = sensor[6]
            url_params['b']['api_key'] = sensor[7]
            url_params['b']['start'] = start_time
            url_params['b']['end'] = end_time
            url_params['b']['average'] = interval
         for key, params in url_params.items():
            url = root_url.format(**params)
            print(f"{request_num}{key} of {num_sensors * intv} : {url}")
            if key == 'a':
               if df_a is None:
                  response = session.get(url)
                  url_data = response.content
                  df_a = pd.read_csv(io.StringIO(url_data.decode('utf-8')))
                  df_a.insert(0, 'Sensor', sensor_name)
                  df_a.insert(0, 'Lat', lat)
                  df_a.insert(0, 'Lon', lon)
               elif df_a is not None:
                  response = session.get(url)
                  url_data = response.content
                  df_a_s = pd.read_csv(io.StringIO(url_data.decode('utf-8')))
                  df_a_s.insert(0, 'Sensor', sensor_name)
                  df_a_s.insert(0, 'Lat', lat)
                  df_a_s.insert(0, 'Lon', lon)
                  df_a = pd.concat([df_a, df_a_s])
            if key == 'b':
               if df_b is None:
                  response = session.get(url)
                  url_data = response.content
                  df_b = pd.read_csv(io.StringIO(url_data.decode('utf-8')))
                  df_b.insert(0, 'Sensor', sensor_name)
                  df_b.insert(0, 'Lat', lat)
                  df_b.insert(0, 'Lon', lon)
               elif df_b is not None:
                  response = session.get(url)
                  url_data = response.content
                  df_b_s = pd.read_csv(io.StringIO(url_data.decode('utf-8')))
                  df_b_s.insert(0, 'Sensor', sensor_name)
                  df_b_s.insert(0, 'Lat', lat)
                  df_b_s.insert(0, 'Lon', lon)
                  df_b = pd.concat([df_b, df_b_s])
   mapping = {
      'created_at': 'created_at',
      'entry_id': 'entry_id',
      'field1': 'PM1.0_CF1_ug/m3',
      'field2': 'PM2.5_CF1_ug/m3',
      'field3': 'PM10.0_CF1_ug/m3',
      'field4': 'UptimeMinutes',
      'field5': 'RSSI_dbm',
      'field6': 'Temperature_F',
      'field7': 'Humidity_%',
      'field8': 'PM2.5_ATM_ug/m3'
      }
   if df_a is not None:
      df_a = df_a.rename(columns=mapping)
      df_a['created_at'] = pd.to_datetime(df_a['created_at'])
      df_a = df_a[df_a['PM2.5_ATM_ug/m3'].notnull()]

      # Calculate AQI
      df_AQI = df_a[['created_at', 'PM2.5_ATM_ug/m3']].copy()
      df_AQI['created_at'] = pd.to_datetime(df_AQI['created_at'])
      df_AQI['Ipm25'] = df_AQI.apply(
            lambda x: calc_aqi(x['PM2.5_ATM_ug/m3']),
            axis=1
            )
      df_a['Ipm25'] = df_AQI['Ipm25']
      #Need to improve data quality tests in the future
      df_a = df_a[df_a['Ipm25'] <= 1200]
   if df_b is not None:
      df_b = df_b.rename(columns=mapping)
      df_b['created_at'] = pd.to_datetime(df_b['created_at'])
      df_b = df_b[df_b['PM2.5_ATM_ug/m3'].notnull()]

      # Calculate AQI
      df_AQI = df_b[['created_at', 'PM2.5_ATM_ug/m3']].copy()
      df_AQI['created_at'] = pd.to_datetime(df_AQI['created_at'])
      df_AQI['Ipm25'] = df_AQI.apply(
            lambda x: calc_aqi(x['PM2.5_ATM_ug/m3']),
            axis=1
            )
      df_b['Ipm25'] = df_AQI['Ipm25']
      #Need to improve data quality tests in the future
      df_b = df_b[df_b['Ipm25'] <= 1200]

   dfs = {}
   if df_a is not None:
      dfs['a'] = df_a
   if df_b is not None:
      dfs['b'] = df_b
   return dfs


def pa_get_df(start_time, end_time, bbox, interval, channel, metadata, filename="indices"):
   '''Main entry point. Executes the various functions.
      
      Args:
         start_time: (datetime)
         end_time: (datetime)
         bbox: (list, float)
         intv: (int)
      
      Returns:
         (Pandas dataframe)
   '''
   import sys

   if not metadata:
      sensor_ids = get_sensor_indexes(bbox, filename)
   elif metadata:
      metadata_path = config.root_path + os.path.sep + config.metadata_folder 
      items = os.listdir(metadata_path)
      file_list = [name for name in items if name.endswith(".txt")]
      for n, fileName in enumerate(file_list, 1):
         sys.stdout.write("[%d] %s\n\r" % (n, fileName))
      choice = int(input("Select data file[1-%s]: " % n))
      metadata_full_path = metadata_path + os.path.sep + file_list[choice-1]
      with open(metadata_full_path, 'r') as f:
         sensor_ids = ast.literal_eval(f.read())
   dfs = get_ts_data(sensor_ids, start_time, end_time, interval, channel)
   return dfs


if __name__ == "__main__":
   import argparse
   from datetime import datetime
   import os
   import config

   root_path = config.root_path + os.path.sep
   data_path = root_path + config.data_folder


   def valid_date(s):
      try:
         return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
      except ValueError:
         msg = "Not a valid date: '{0}'.".format(s)
         raise argparse.ArgumentTypeError(msg)


   def get_arguments():
      parser = argparse.ArgumentParser(
      description='get PurpleAir PA-II sensor data from ThingSpeak.',
      prog='pa_get_df',
      usage='%(prog)s [-b <bbox>], [-o <output>], [-i <interval>], [-s <start>], [-e <end>], [-c <channel>], [-md]',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      )
      g=parser.add_argument_group(title='arguments',
            description='''    -b, --bbox    optional.  bounding box coordinates, format  SE lon lat NW lon lat. omit SE and NW.
      -f  --filename                        optional.  output filename prefix.
      -i  --interval                        optional.  data average interval. minutes.
      -s  --startdate                       optional.  start date. format "YYYY-MM-DD HH:MM:SS" include quotes. 
      -e  --enddate                         optional.  end date. format "YYYY-MM-DD HH:MM:SS" include quotes.
      -c  --channel                         optional.  channel.
          --md                              optional.  use stored sensor metadata        ''')
      g.add_argument('-b', '--bbox',
                     type=float,
                     nargs = 4,
                     default = [-117.5298, 33.7180, -117.4166, 33.8188],
                     dest='bbox',
                     help=argparse.SUPPRESS)
      g.add_argument('-f', '--filename',
                     type=str,
                     default = 'no_name',
                     dest='filename',
                     help=argparse.SUPPRESS)
      g.add_argument('-i', '--interval',
                     type=str,
                     default = '10',
                     dest='interval',
                     help=argparse.SUPPRESS)
      g.add_argument('-s', '--startdate', 
                     type=valid_date,
                     help=argparse.SUPPRESS)
      g.add_argument('-e', '--enddate', 
                     type=valid_date,
                     help=argparse.SUPPRESS)
      g.add_argument('-c', '--channel',
                     type=str,
                     default = 'a',
                     choices = ['a', 'b', 'ab'],
                     dest='channel',
                     help=argparse.SUPPRESS)
      g.add_argument('--md', action='store_true',
                     dest='metadata',
                     help=argparse.SUPPRESS)
      args = parser.parse_args()
      return(args)

   args = get_arguments()

   bbox = args.bbox
   bbox_pa = (str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]))
   dfs = pa_get_df(args.startdate, args.enddate, bbox_pa, args.interval, args.channel, args.metadata, args.filename)
   for key, df in dfs.items():
      data_file_full_path = data_path + os.path.sep + args.filename + "_" + args.startdate.strftime("%Y%m%d") + "_" + args.enddate.strftime("%Y%m%d") + "_" + key + ".csv"
      df.to_csv(data_file_full_path, index=False, header=True)