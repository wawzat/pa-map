# Visualize PA data on a map
#  *** WARNING! *** this program deletes files from a temporary images folder. This is not safed off yet. Use at your own risk.
# You must establish the appropriate paths to folders below.
# James S. Lucas 20201017

from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#from mpl_toolkits.axes_grid1 import make_axes_locatable
import colorcet as cc
import os
import config


def cleanup_files(images_path):
    filelist = [ f for f in os.listdir(images_path) if f.endswith(".png") ]
    for f in filelist:
        os.remove(os.path.join(images_path, f))


def plot_map(root_path, df, map_plt, fig_num, start_time, bbox, label, range, marker):
    mapbox_attribution = u"\u00A9"+" Mapbox"
    dpi = 96
    mapsize = map_plt.shape
    images_path = root_path + 'pa_map_plot' + os.path.sep + 'images' + os.path.sep
    img_fname = images_path + os.path.sep + str(fig_num) + '_frame.png'
    fig, ax = plt.subplots(figsize = (mapsize[1]/dpi, mapsize[0]/dpi))
    ax.set_axis_off()
    ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.7, c=df.Ipm25, s=marker, cmap=cc.cm.fire, vmin=range[0], vmax=range[1])
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.8, c=df.Ipm25, s=18, cmap=cc.cm.fire, vmin=20, vmax=255)
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.6, c=df.Ipm25, s=18, cmap=plt.get_cmap('YlOrRd'), vmin=40, vmax=235)
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.5, c=df.Ipm25, s=5, cmap=plt.get_cmap('magma'), vmin=0, vmax=275)
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.6, c=df.Ipm25, s=20, cmap=cmap, vmin=10, vmax=245)
    ax.set_title(label)
    ax.text(0.06, 0.06, str(start_time), transform=ax.transAxes, color='w')
    ax.text(0.02, 0.02, mapbox_attribution, transform=ax.transAxes, color='w')
    ax.set_xlim(bbox[0],bbox[1])
    ax.set_ylim(bbox[2],bbox[3])
    im = ax.imshow(map_plt, zorder=0, extent=bbox, aspect='auto', cmap=cc.cm.fire, vmin=range[0], vmax=range[1])
    fig.colorbar(im, ax=ax, pad=0.01, aspect=50)
    plt.rcParams['savefig.facecolor']='gray'
    plt.savefig(img_fname, bbox_inches='tight', pad_inches=0.05)
    plt.close('all')
    fig_num += 1
    return(fig_num)


if __name__ == "__main__":
    # Change this variable to point to the desired directory in config.py. 
    data_directory = config.matrix5

    root_path = data_directory + os.path.sep

    data_filename = 'combined_csv_map_plot.csv'
    map_filename = 'map_dark.png'

    data_full_file_path = root_path + data_filename
    map_full_file_path = root_path + map_filename 

    images_folder = 'images'
    images_path = root_path + 'pa_map_plot' + os.path.sep + images_folder + os.path.sep 
    vid_filename = 'pa_tv.mp4'
    vid_full_file_path = root_path + vid_filename 


    #           SE lon / lat            NW lon / lat
    #bbox = [-117.5298, 33.7180, -117.4166, 33.8188]  #Temescal Valley
    bbox = [-122.9068, 37.1778, -121.6626, 38.4536]  #Bay Area
    bbox_plot = (bbox[0]-.004, bbox[2]+.004, bbox[1]-.004, bbox[3]+.004)
    bbox_mapbox = (bbox[0]-.004, bbox[1]-.004, bbox[2]+.004, bbox[3]+.004)
    bbox_pa = (str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]))
    #df = pd.read_csv(data_full_file_path)
    df = pa_get_df(args.startdate, args.enddate, bbox_pa)
    df['created_at'] = pd.to_datetime(df['created_at'])


    fig_num = 1
    first_datetime = min(df['created_at'])
    last_datetime = max(df['created_at'])
    start_time = first_datetime
    time_increment = timedelta(minutes = 30)


    cleanup_files(images_folder)
    plot_map(root_path, df, map_plt, fig_num, start_time, bbox)