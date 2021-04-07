# Visualize PA data on a map
#  *** WARNING! *** this program deletes files from a temporary images folder. This is not safed off yet. Use at your own risk.
# James S. Lucas 20210406

from datetime import date, datetime, timedelta
import pytz
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import colorcet as cc
import os
import sys
import config
from get_map import get_map


def plot_map(root_path, df, map_plt, fig_num, start_time, bbox, label, range, marker, map):
    #print(df)
    if map == 'd':
        map_text_color = 'w'
    elif map == 'l':
        map_text_color = 'navy'
    mapbox_attribution = u"\u00A9"+" Mapbox"
    dpi = 96
    mapsize = map_plt.shape
    images_path = root_path + os.path.sep + config.all_sensors_images_folder
    img_fname = images_path + os.path.sep + str(fig_num) + '_frame.png'
    fig, ax = plt.subplots(figsize = (mapsize[1]/dpi, mapsize[0]/dpi))
    ax.set_axis_off()
    ax.scatter(
        df.Lon,
        df.Lat,
        zorder=1,
        alpha=0.7,
        c=df.PM25,
        linewidths = 1.5,
        edgecolors = 'navy',
        s=marker,
        cmap=cc.cm.fire_r,
        vmin=range[0],
        vmax=range[1])
    ax.set_title(label)
    ax.text(0.06, 0.06, str(start_time), fontsize=10, transform=ax.transAxes, color=map_text_color)
    ax.text(0.02, 0.02, mapbox_attribution, transform=ax.transAxes, color=map_text_color)
    ax.set_xlim(bbox[0],bbox[1])
    ax.set_ylim(bbox[2],bbox[3])
    im = ax.imshow(map_plt, zorder=0, extent=bbox, aspect='auto', cmap=cc.cm.fire_r, vmin=range[0], vmax=range[1])
    fig.colorbar(im, ax=ax, pad=0.01, aspect=50)
    plt.rcParams['savefig.facecolor']='gray'
    plt.savefig(img_fname, bbox_inches='tight', pad_inches=0.05)
    #plt.show
    plt.close('all')
    fig_num += 1
    return(fig_num)

#Main
seasons = ['2020-02-29', '2020-05-31', '2020-08-31', '2020-11-30'] 
range = [0, 50]
marker = 60
map = 'l'
bbox = [-117.5298, 33.7180, -117.4166, 33.8188] # Temescal Valley
bbox_plot = (bbox[0]-.004, bbox[2]+.004, bbox[1]-.004, bbox[3]+.004)
bbox_mapbox = (bbox[0]-.004, bbox[1]-.004, bbox[2]+.004, bbox[3]+.004)
root_path = config.all_sensors_root_path
images_folder = config.all_sensors_images_folder
input_filename = 'combined_summarized_csv.csv'
output_filename = 'resample_df.csv'
input_full_file_path = root_path + os.path.sep + images_folder + os.path.sep + input_filename
output_full_file_path = root_path + os.path.sep + images_folder + os.path.sep + output_filename
map_filename = 'map_dark.png'
map_full_file_path = root_path + os.path.sep + images_folder + os.path.sep + map_filename
get_map(map_full_file_path, map, bbox_mapbox)
map_plt = plt.imread(map_full_file_path)
df = pd.read_csv(
        input_full_file_path,
        index_col=['DateTime_US_Pacific'],
        usecols=['Sensor', 'DateTime_US_Pacific', 'Lat', 'Lon', 'PM2.5_ATM_ug/m3'],
        parse_dates=['DateTime_US_Pacific']
        )
df.reset_index(inplace=True)
mapping = ({
            'PM2.5_ATM_ug/m3': 'PM25'
            })
df = df.rename(columns=mapping)
df = df.groupby('Sensor')
df = df.resample('Q-NOV', on='DateTime_US_Pacific').mean()
plot_start_time = datetime(2020, 5, 31)
#plot_end_time = datetime(2020, 8, 31)
df.reset_index(inplace=True)
#df = df[(df['DateTime_US_Pacific'] >= plot_start_time) & (df['DateTime_US_Pacific'] <= plot_end_time)]
first_datetime = min(df['DateTime_US_Pacific'])
#last_datetime = max(df['DateTime_US_Pacific'])
start_time = first_datetime
cols = ['Lon', 'Lat', 'Sensor', 'DateTime_US_Pacific', 'PM25']
df = df[cols]
df = df.dropna()
#df['PM25'] = df['PM25'].astype(int)
#print(df)
df.to_csv(output_full_file_path)
fig_num = 1
for season in seasons:
    df2 = df[df['DateTime_US_Pacific'] == season]
    fig_num = plot_map(root_path, df2, map_plt, fig_num, start_time, bbox_plot, 'NASA', range, marker, map)