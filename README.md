# pa-map
 
## Overview
This set of modules when used together gets PurpleAir PA-II sensor data for sensors located within a bounding box for a given date range, plots the data on a map and generates a timelapse video of the readings.

Some of the modules may also be used independently as modules in other programs or directly from the command line.

## Files
1. pa_map_vis.py: The main program that executes the other modules to get the data and make the timelapse video.
2. pa_get_df.py: Gets historical sensor data and returns a Pandas data frame.
3. pa_map_plot.py: create the image frames. 
4. get_map.py: Gets a map image for the provided bounding box from Mapbox. 
5. pa_map_vid.py: create h.264 encoded mp4 video from image frames.

## Installation and Use
1. Request a key for the PurpleAir REST API from contact@purpleair.com.
2. Register an account with https://www.mapbox.com.
3. Create a root folder path and subfolders for images, data and video.
4. Rename the config_template.py file to config.py.
5. Edit config.py with the PurpleAir keys, Mapbox tokens and file directory paths.
6. Run python pa_map_vis.py -h for help on the command line arguments.

## Notes:
1. There are two data modes that may be selected with the -d argument. 
  1. -d TS obtains historical data from ThinkSpeak. Historical data are saved in the Data folder as csv files.
  2. -d CSV provides a list the of csv files that exist in the Data folder to choose from. The intent here is if you want to adjust to a shorter date range, or modify some of the plotting/video parameters you can re-create the time lapse without re-downloading the historical data.
4. sleep() functions are used to rate limit. Durations have not been rigorously tested and there is room for improvement.