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
   Pandas Data frame of sensor readings for sensors within the bounding box during the provided start and end times.

Notes:
   Description of operation:
      PurpleAir API is queried for a list of sensors within the bounding box.
      PurpleAir API is queried a second time for the ThingSpeak keys for each of the sensors
      ThingSpeak API is queried for the sensor historical readings.

   Todo: 
      rename variables consistently with names that are more appropriate to function
      exception handling
      Status and error logging
      add option to store data in local time vs UTC
      filter apparent bad sensor readings 
      Get both sensors data and exclude based on confidence
'''
 
 #James S. Lucas 20201209

import requests
import json
import config
import pandas as pd
from time import sleep
import math


def get_sensor_indexes(bbox):
   '''Gets list of sensor indexes (aka ID's) from the PurpleAir API for sensors located within a bounding box.

      Args:
         bbox (list, float)
            bounding box coordinates in the format lat1 lon1 lat2 lon2 for the SE and NW corners respectively

      Returns:
         (List, str)
   '''
   root_url = "https://api.purpleair.com/v1/sensors"
   params = {
      'fields': "name,location_type",
      'nwlng': bbox[0],
      'selat': bbox[1],
      'selng': bbox[2],
      'nwlat': bbox[3]
      }
   url_template = root_url + "?fields={fields}&nwlng={nwlng}&nwlat={nwlat}&selng={selng}&selat={selat}"
   url = url_template.format(**params)
   try:
      list_of_sensor_indexes = []
      header = {"X-API-Key":config.purpleair_read_key}
      #response will be a list of lists in the format [[sensor_id, sensor_name, location_type]]
      response = requests.get(url, headers=header)
      if response.status_code == 200:
         sensors_data = json.loads(response.text)
         for sensor_list in sensors_data['data']:
            # if sensor_location is outside (0)
            if sensor_list[2] == 0:
               list_of_sensor_indexes.append(sensor_list[0])
         print(" ")
         print(len(list_of_sensor_indexes))
         print(" ")
         print (list_of_sensor_indexes)
         print(" ")
         return list_of_sensor_indexes
      else:
         print("error no 200 response.")
   except Exception as e:
      print(e)


def get_sensor_ids(list_of_sensor_indexes):
   '''Gets list of lists of sensor metadata from the PurpleAir API

      Args:
         list_of_sensor_indexes: (list, str)

      Returns:
         list of lists of sensor metadata.

      Notes:
         Metadata includes:
            sensor name
            latitude
            longitude
            sensor index
            ThingSpeak primiary id a
            ThingSpeak primary key a
   '''
   i = 0
   num_sensors = len(list_of_sensor_indexes)
   sensor_ids = []
   root_url = "https://api.purpleair.com/v1/sensors/{sensor_index}"
   header = {"X-API-Key":config.purpleair_read_key}
   for sensor_index in list_of_sensor_indexes:
      i += 1
      params = {'sensor_index': sensor_index}
      url = root_url.format(**params)
      response = requests.get(url, headers=header)
      if response.status_code == 200:
         sensor_data = json.loads(response.text)
         try:
            sensor_ids.append((
               sensor_data['sensor']['name'],
               sensor_data['sensor']['latitude'],
               sensor_data['sensor']['longitude'],
               sensor_data['sensor']['sensor_index'], 
               sensor_data['sensor']['primary_id_a'], 
               sensor_data['sensor']['primary_key_a']
               ))
         except KeyError as e:
            print(e)
            pass
         print(str(i) + " of " + str(num_sensors) + " : " + str(sensor_index))
         #sleep(3.1)
         sleep(0.75)
      else:
         print(" ")
         print("error not 200 response. pausing for 60 seconds.")
         print(response.reason)
         sleep(60)
   return sensor_ids


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
   if (PM2_5 < 0) or math.isnan(PM2_5):
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
         print("PM2_5: " + str(PM2_5))
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
      print("error in calc_aqi() function: %s") % e
 

def get_ts_data(sensor_ids, start_time, end_time, interval):
   '''Gets sensor readings from the ThingSpeak API.

      Args:
         sensor_ids: (list, str)
         start_time: (datetime)
         end_time: (datetime)
         interval: (int)

      Returns:
         (Pandas dataframe)
   '''
   df = None
   delta = end_time - start_time
   intv = int(delta.days / 10)
   if intv < 1:
      intv = 1
   data_range = list(date_range(start_time, end_time, intv)) 
   i = 0
   num_sensors = len(sensor_ids)
   for sensor in sensor_ids:
      i += 1
      sensor_name = sensor[0]
      lat = sensor[1]
      lon = sensor[2]
      for t in range(0, intv):
         root_url = 'https://api.thingspeak.com/channels/{channel}/feeds.csv?api_key={api_key}&start={start}%2000:00:00&end={end}%2023:59:59&average={average}'
         channel = sensor[4]
         api_key = sensor[5]
         start_time = data_range[t]
         end_time = data_range[t+1]
         params = {
            'channel': channel,
            'api_key': api_key,
            'start': start_time,
            'end': end_time,
            'average': interval
            }
         url = root_url.format(**params)
         print(str(i) + " of " + str(num_sensors) + " " + url)
         if df is None:
            df = pd.read_csv(url)
            df.insert(0, 'Sensor', sensor_name)
            df.insert(0, 'Lat', lat)
            df.insert(0, 'Lon', lon)
         else:
            df_s = pd.read_csv(url)
            df_s.insert(0, 'Sensor', sensor_name)
            df_s.insert(0, 'Lat', lat)
            df_s.insert(0, 'Lon', lon)
            df = pd.concat([df, df_s])
         sleep(.5)
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
   df = df.rename(columns=mapping)
   df['created_at'] = pd.to_datetime(df['created_at'])
   df = df[df['PM2.5_CF1_ug/m3'].notnull()]

   # Calculate AQI
   df_AQI = df[['created_at', 'PM2.5_CF1_ug/m3']].copy()
   df_AQI['created_at'] = pd.to_datetime(df_AQI['created_at'])
   df_AQI['Ipm25'] = df_AQI.apply(
         lambda x: calc_aqi(x['PM2.5_CF1_ug/m3']),
         axis=1
         )
   df['Ipm25'] = df_AQI['Ipm25']
   df = df[df['Ipm25'] <= 800]
   return df


def pa_get_df(start_time, end_time, bbox, interval):
   '''Main entry point. Executes the various functions.
      
      Args:
         start_time: (datetime)
         end_time: (datetime)
         bbox: (list, float)
         intv: (int)
      
      Returns:
         (Pandas dataframe)
   '''
   list_of_sensor_indexes = get_sensor_indexes(bbox)
   sensor_ids = get_sensor_ids(list_of_sensor_indexes)
   df = get_ts_data(sensor_ids, start_time, end_time, interval)
   return df


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
      usage='%(prog)s [-b <bbox>], [-o <output>], [-i <interval>], [-s <start>], [-e <end>]',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      )
      g=parser.add_argument_group(title='arguments',
            description='''    -b, --bbox    optional.  bounding box coordinates, format  SE lon lat NW lon lat. omit SE and NW.
      -o  --output                          optional.  output filename prefix.
      -i  --interval                        optional.  data average interval. minutes.
      -s  --start                           optional.  start date. format "YYYY-MM-DD HH:MM:SS" include quotes. 
      -e  --end                             optional.  end date. format "YYYY-MM-DD HH:MM:SS" include quotes.           ''')
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
      args = parser.parse_args()
      return(args)

   args = get_arguments()

   bbox = args.bbox
   bbox_pa = (str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]))
   df = pa_get_df(args.startdate, args.enddate, bbox_pa, args.interval)
   data_file_full_path = data_path + os.path.sep + args.filename + "_" + args.startdate.strftime("%Y%m%d") + "_" + args.enddate.strftime("%Y%m%d") + ".csv"
   df.to_csv(data_file_full_path, index=False, header=True)