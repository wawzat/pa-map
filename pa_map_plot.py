# Visualize PA data on a map
#  *** WARNING! *** this program deletes files from a temporary images folder. This is not safed off yet. Use at your own risk.
# James S. Lucas 20201028

from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
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
    images_path = root_path + config.images_folder
    img_fname = images_path + os.path.sep + str(fig_num) + '_frame.png'
    fig, ax = plt.subplots(figsize = (mapsize[1]/dpi, mapsize[0]/dpi))
    ax.set_axis_off()
    ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.7, c=df.Ipm25, s=marker, cmap=cc.cm.fire, vmin=range[0], vmax=range[1])
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.8, c=df.Ipm25, s=18, cmap=cc.cm.fire, vmin=20, vmax=255)
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