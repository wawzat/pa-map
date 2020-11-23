# Get PurpleAir sensor data from PurpleAir and Thingspeak API's for bounding box and year-month
# Returns pandas dataframe
# James S. Lucas 20201018
# Todo:  prepare as func0ion accepting input for bbox and date range
#        convert sensor_ids tuple to dictionary
#        rename variables consistently with names that are more appropriate to function
#        allow partial month date range
#        exception handling
#        directories and paths from config file vs hardcoded. Prompt for path on first run.
#        add option to store data in local time vs UTC

import requests
import json
import os
import config
import pandas as pd
#import calendar
from datetime import datetime
from time import sleep


# Change this variable in config.py to point to the desired directory above. 
data_directory = config.matrix5

filename = 'bay_area_20201026_20201027.csv'
output_folder = 'pa_map_plot'
output_path = data_directory + os.path.sep + output_folder


def get_sensor_indexes(bbox):
   root_url = "https://api.purpleair.com/v1/sensors"
   params = {
      'fields': "name,latitude,longitude",
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
      response = requests.get(url, headers=header)
      if response.status_code == 200:
         sensors_data = json.loads(response.text)
         for sensor_list in sensors_data['data']:
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
   sensor_ids = []
   root_url = "https://api.purpleair.com/v1/sensors/{sensor_index}"
   header = {"X-API-Key":config.purpleair_read_key}
   for sensor_index in list_of_sensor_indexes:
      params = {'sensor_index': sensor_index}
      url = root_url.format(**params)
      response = requests.get(url, headers=header)
      sensor_data = json.loads(response.text)
      sensor_ids.append((
         sensor_data['sensor']['name'],
         sensor_data['sensor']['latitude'],
         sensor_data['sensor']['longitude'],
         sensor_data['sensor']['sensor_index'], 
         sensor_data['sensor']['primary_id_a'], 
         sensor_data['sensor']['primary_key_a']
         ))
      print(sensor_index)
      sleep(1.5)
   return sensor_ids


def date_range(start_time, end_time, intv):
   diff = (end_time  - start_time ) / intv
   for i in range(intv):
      yield (start_time + diff * i).strftime("%Y%m%d")
   yield end_time.strftime("%Y%m%d")


def calc_aqi(PM2_5):
    # Function takes the 24-hour rolling average PM2.5 value and calculates
    # "AQI". "AQI" in quotes as this is not an official methodology. AQI is 
    # 24 hour midnight-midnight average. May change to NowCast or other
    # methodology in the future.
   # Truncate to one decimal place.
   PM2_5 = int(PM2_5 * 10) / 10.0
   if PM2_5 < 0:
      PM2_5 = 0
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
 

def get_ts_data(sensor_ids, start_time, end_time):
   df = None
   delta = end_time - start_time
   intv = int(delta.days / 10)
   if intv < 1:
      intv = 1
   data_range = list(date_range(start_time, end_time, intv)) 
   for sensor in sensor_ids:
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
            'average': '10'
            }
         url = root_url.format(**params)
         print(url)
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

   # Calculate AQI
   # For clarity may move most of this to calc_aqi()
   df_AQI = df[['created_at', 'PM2.5_CF1_ug/m3']].copy()
   df_AQI['created_at'] = pd.to_datetime(df_AQI['created_at'])
   df_AQI['Ipm25'] = df_AQI.apply(
         lambda x: calc_aqi(x['PM2.5_CF1_ug/m3']),
         axis=1
         )
   df['Ipm25'] = df_AQI['Ipm25']
   return df


def pa_get_df(start_time, end_time, bbox):
   list_of_sensor_indexes = get_sensor_indexes(bbox)
   sensor_ids = get_sensor_ids(list_of_sensor_indexes)
   df = get_ts_data(sensor_ids, start_time, end_time)
   return df