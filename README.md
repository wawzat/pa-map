Read PurpleAir PA-II sensor data from a .csv file (refer to included sample csv file for format). 
Plot the AQI readings on a map image file 
Save an image "frame" for data plotted every 15 minutes to be used to create a visualization video. 

combined_csv_map_plot.csv: sample data 
pa_map_plot.py: create the image frames, optionally get a map image from mapbox with appropriate geographic bounds. 
get_map.py: used by pa_map_plot.py to get map image from mapbox. 
pa_map_vid.py: create h.264 mp4 video from image frames. 
