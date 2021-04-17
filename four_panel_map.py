# Visualize PA data on a map
#  *** WARNING! *** this program deletes files from a temporary images folder. This is not safed off yet. Use at your own risk.
# James S. Lucas 20210406

from datetime import date, datetime, timedelta
import pytz
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import colorcet as cc
import os
import sys
import config
from get_map import get_map


def plot_map(root_path, df, map_plt, bbox, range, marker, map):
    fig_num = 1
    seasons = [['Winter','2020-02-29'], ['Spring', '2020-05-31'], ['Summer', '2020-08-31'], ['Fall', '2020-11-30']] 
    plots_dict = {1: [0, 0], 2: [0, 1], 3: [ 1, 0], 4: [1, 1]}
    if map == 'd':
        map_text_color = 'w'
    elif map == 'l' or map == 's':
        map_text_color = 'navy'
    mapbox_attribution = u"\u00A9"+" Mapbox"
    dpi = 96
    mapsize = map_plt.shape
    images_path = root_path + os.path.sep + config.all_sensors_images_folder
    img_fname = images_path + os.path.sep + str(fig_num) + '_frame.png'
    plt.rcParams['savefig.facecolor']='white'
    fig, ax = plt.subplots(2, 2, figsize = (mapsize[1]/dpi, mapsize[0]/dpi))
    for season in seasons:
        print(plots_dict[fig_num])
        df2 = df[df['DateTime_US_Pacific'] == season[1]]
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].scatter(
            df2.Lon,
            df2.Lat,
            zorder=1,
            alpha=0.7,
            c=df2.PM25,
            linewidths = 1.5,
            edgecolors = 'navy',
            s=marker,
            cmap=cc.cm.rainbow,
            vmin=range[0],
            vmax=range[1])
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].set_title(season[0])
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].set_xlim(bbox[0],bbox[1])
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].set_ylim(bbox[2],bbox[3])
        im = ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].imshow(map_plt, zorder=0, extent=bbox, aspect='auto', cmap=cc.cm.rainbow, vmin=range[0], vmax=range[1])
        if fig_num == 3:
            ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].text(0.02, 0.02, mapbox_attribution, transform=ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].transAxes, color=map_text_color)
        if fig_num == 4:
            fig.subplots_adjust(top=0.8)
            fig.patch.set_edgecolor('black')
            fig.patch.set_linewidth('1')
            fig.tight_layout(pad=0.15, h_pad=2.0, w_pad=3.0)
            fig.suptitle('PM2.5', x=.42, y=1.02, fontsize='xx-large')
            fig.colorbar(im, ax=ax.ravel().tolist())
            plt.savefig(img_fname, bbox_inches='tight', pad_inches=0.15)
            plt.close('all')
        fig_num += 1


def plot_diurnal(root_path, df):
    fig_num = 1
    seasons = [
        ['Winter',
         '2019-11-29',
         '2020-02-29'],
        ['Spring',
         '2020-02-28',
         '2020-05-31'],
        ['Summer',
         '2020-05-30',
         '2020-08-31'],
        ['Fall',
         '2020-08-30',
         '2020-11-30']
        ] 
    plots_dict = {1: [0, 0], 2: [0, 1], 3: [ 1, 0], 4: [1, 1]}
    dpi = 96
    images_path = root_path + os.path.sep + config.all_sensors_images_folder
    img_fname = images_path + os.path.sep + str(fig_num) + '_diurnal.png'
    plt.rcParams['savefig.facecolor']='white'
    fig, ax = plt.subplots(2, 2, figsize = (640/dpi, 640/dpi))
    min_hourly_std = 1000
    max_hourly_std = 0
    for season in seasons:
        df2 = df.loc[season[1]:season[2]]
        cols = ['PM25']
        df2 = df2[cols]
        df2['Hour'] = df2.index.hour
        df2 = df2.groupby(['Hour']).agg({'PM25':['mean', 'std']})
        df2.columns = ['PM25', 'std']
        df2['std+'] = df2['PM25'] + df2['std']
        df2['std-'] = df2['PM25'] - df2['std']
        if max_hourly_std < df2['std+'].max():
            max_hourly_std = df2['std+'].max()
        if df2['std-'].min() < min_hourly_std:
            min_hourly_std = df2['std-'].min()
    for season in seasons:
        print(plots_dict[fig_num])
        df2 = df.loc[season[1]:season[2]]
        df2['Hour'] = df2.index.hour
        #Calculate sample standard deviation
        df2 = df2.groupby(['Hour']).agg({'PM25':['mean', 'std']})
        df2.columns = ['PM25', 'std']
        df2['std+'] = df2['PM25'] + df2['std']
        df2['std-'] = df2['PM25'] - df2['std']
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].plot(
            df2.index,
            df2['PM25']
            )
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].fill_between(df2.index, df2['std-'], df2['std+'], alpha=0.35)
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].set_title(season[0])
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].set_xlabel('Hour')
        ax[plots_dict[fig_num][0], plots_dict[fig_num][1]].set_ylim(ymin=min_hourly_std-2, ymax=max_hourly_std + 3.5)
        if fig_num == 4:
            fig.subplots_adjust(top=0.8)
            fig.patch.set_edgecolor('black')
            fig.patch.set_linewidth('2')
            fig.tight_layout(pad=0.05, h_pad=2.0, w_pad=2.0)
            fig.suptitle('PM2.5', x=.5, y=1.05, fontsize='xx-large')
            plt.savefig(img_fname, bbox_inches='tight', pad_inches=0.5)
            plt.close('all')
        fig_num += 1


def set_aqi(x):
    if x >= 0 and x <= 50:
        return 'Good'
    elif x > 50 and x <= 100:
        return 'Moderate'
    elif x > 100 and x <= 150:
        return 'Sensitive'
    elif x > 150 and x <= 200:
        return 'Unhealthy'
    elif x > 200 and x <= 300:
        return 'Very'
    elif x > 300:
        return 'Hazardous'


def plot_donut(root_path, df):
    fig_num = 0
    fire1_start = datetime.strptime('2018-07-26', '%Y-%m-%d')
    fire1_end = datetime.strptime('2018-10-31', '%Y-%m-%d')
    fire2_start = datetime.strptime('2019-06-30', '%Y-%m-%d')
    fire2_end = datetime.strptime('2019-10-15', '%Y-%m-%d')
    fire3_start = datetime.strptime('2020-06-30', '%Y-%m-%d')
    fire3_end = datetime.strptime('2020-10-15', '%Y-%m-%d')
    colors = {'Good': 'Limegreen', 'Moderate': 'Yellow', 'Sensitive': 'Orange', 'Unhealthy': 'Red', 'Very': 'Purple', 'Hazardous': 'Brown'}
    dpi = 96
    images_path = root_path + os.path.sep + config.all_sensors_images_folder
    img_fname = images_path + os.path.sep + str(fig_num) + '_donut.png'
    plt.rcParams['savefig.facecolor']='white'
    fig, ax = plt.subplots(2, figsize = (1280/dpi, 1280/dpi))
    df2 = df.copy()
    df2 = df2.resample('24H').mean()
    df2.reset_index(inplace=True)
    df2['Season'] = (df2['DateTime_US_Pacific'].apply(
        lambda x: 'Fire' if (
            (x >= fire1_start and x <= fire1_end) or (x >= fire2_start and x <= fire2_end or (x >= fire3_start and x <= fire3_end))) else 'Non-Fire'))
    df2['AQI'] = (df2['Ipm25'].apply(set_aqi))
    cols = ['Season', 'AQI']
    df2 = df2[cols]
    print(df2)
    for i, m in df2.groupby('Season'):
        categories, counts = zip(*Counter(m.AQI).items())
        print(i, categories, counts)
        wedges, texts = ax[fig_num].pie(
            counts,
            colors=[colors[key] for key in categories],
            wedgeprops=dict(width=0.4)
            )
        ax_title = f"{i} Season"
        ax[fig_num].set_title(ax_title, y=.48)
        if fig_num == 1:
            plt.legend(
            wedges,
            categories,
            title="Category",
            loc="center left",
            bbox_to_anchor=(0.68, 0.19),
            bbox_transform=plt.gcf().transFigure
            #bbox_to_anchor=(1, 0, 0.5, 1)
            )
        fig_num += 1
    #plt.tight_layout(pad=0.05, h_pad=1.0, w_pad=2.0)
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig(img_fname, bbox_inches='tight', pad_inches=0.3)
    plt.close('all')


#Main
range = [0, 25]
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
map_filename = 'map.png'
map_full_file_path = root_path + os.path.sep + images_folder + os.path.sep + map_filename
get_map(map_full_file_path, map, bbox_mapbox)
map_plt = plt.imread(map_full_file_path)
df = pd.read_csv(
        input_full_file_path,
        index_col=['DateTime_US_Pacific'],
        usecols=['Sensor', 'DateTime_US_Pacific', 'Lat', 'Lon', 'PM2.5_ATM_ug/m3', 'Ipm25'],
        parse_dates=['DateTime_US_Pacific']
        )
mapping = ({
            'PM2.5_ATM_ug/m3': 'PM25'
            })
df = df.rename(columns=mapping)
df2 = df.copy()
df2.reset_index(inplace=True)
df2 = df2.groupby('Sensor')
df2 = df2.resample('Q-NOV', on='DateTime_US_Pacific').mean()
plot_start_time = datetime(2020, 5, 31)
df2.reset_index(inplace=True)
first_datetime = min(df2['DateTime_US_Pacific'])
#last_datetime = max(df['DateTime_US_Pacific'])
start_time = first_datetime
cols = ['Lon', 'Lat', 'Sensor', 'DateTime_US_Pacific', 'PM25']
df2 = df2[cols]
df2 = df2.dropna()
#plot_map(root_path, df2, map_plt, bbox_plot, range, marker, map)
#plot_diurnal(root_path, df)
plot_donut(root_path, df)