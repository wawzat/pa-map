# Visualize PA data on a map
#  *** WARNING! *** this program deletes files from a temporary images folder. This is not safed off yet. Use at your own risk.
# You must establish the appropriate paths to folders below.
# James S. Lucas 20201017

from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#from matplotlib.colors import ListedColormap
import colorcet as cc
import os
import config


def cleanup_files(images_path):
    filelist = [ f for f in os.listdir(images_path) if f.endswith(".png") ]
    for f in filelist:
        os.remove(os.path.join(images_path, f))


def plot_map(root_path, df, map_plt, fig_num, start_time, bbox):
    #N = 256
    #vals = np.ones((N, 4))
    #vals[:, 0] = np.linspace(1/256, 228/256, 1/256)    # Green
    #vals[:, 1] = np.linspace(256/256, 256/256, 1/256)  # Yellow
    #vals[:, 2] = np.linspace(256/256, 127/256, 1/256)  # Dark Orange
    #vals[:, 3] = np.linspace(255/256, 1/256, 2/256)    # Red
    #vals[:, 4] = np.linspace(152/256, 1/256, 77/256)   # Purple
    #vals[:, 5] = np.linspace(126/256, 1/256, 35/256)   # Brown
    #vals[:, 0] = np.linspace(256/256, 1, N)    # Green
    #vals[:, 1] = np.linspace(125/256, 1, N)    # Yellow
    #vals[:, 2] = np.linspace(60/256, 1, N)    # Dark Orange
    #vals[:, 3] = np.linspace(30/256, 1, N)    # Red
    #vals[:, 4] = np.linspace(15/256, 1, N)    # Purple
    #vals[:, 5] = np.linspace(1/256, 1, N)    # Brown
    #newcmp = ListedColormap(vals)
    #cmap, norm = mpl.colors.from_levels_and_colors([0,50,100,150,200,300,500], ['green','yellow','orange','red','purple','maroon'])

    # Section START
    # create a colormap that consists of
    # - 1/5 : custom colormap, ranging from white to the first color of the colormap
    # - 4/5 : existing colormap

    # set upper part: 4 * 256/4 entries
    ##upper = mpl.cm.YlOrRd(np.arange(256))

    # set lower part: 1 * 256/4 entries
    # - initialize all entries to 1 to make sure that the alpha channel (4th column) is 1
    ##lower = np.ones((int(256/4),4))
    # - modify the first three columns (RGB):
    #   range linearly between white (1,1,1) and the first color of the upper colormap
    ##for i in range(3):
        ##lower[:,i] = np.linspace(1, upper[0,i], lower.shape[0])

    # combine parts of colormap
    ##cmap = np.vstack(( lower, upper ))

    # convert to matplotlib colormap
    ##cmap = mpl.colors.ListedColormap(cmap, name='myColorMap', N=cmap.shape[0])
    #Section END

    #cmap, norm = mpl.colors.from_levels_and_colors(
                #[0, 12, 25, 37, 50,
                 #62, 75, 87, 100,
                 #112, 125, 137, 150,
                 #162, 175, 187, 200,
                 #225, 250, 275, 300,
                 #350, 400, 450, 500
                 #],
                 #['springgreen', 'lime', 'limegreen', 'forestgreen',
                  #'yellowgreen','greenyellow', 'yellow', 'gold',
                  #'palegoldenrod', 'goldenrod', 'orange', 'darkorange',
                  #'coral', 'tomato', 'orangered','red',
                  #'crimson', 'mediumvioletred','palevioletred', 'plum',
                  #'indianred', 'firebrick', 'brown', 'maroon'
                  #])
    images_path = root_path + 'pa_map_plot' + os.path.sep + 'images' + os.path.sep
    img_fname = images_path + os.path.sep + str(fig_num) + '_frame.png'
    fig, ax = plt.subplots(figsize = (8, 7))
    ax.set_axis_off()
    ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.8, c=df.Ipm25, s=18, cmap=cc.cm.fire, vmin=20, vmax=255)
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.6, c=df.Ipm25, s=18, cmap=plt.get_cmap('YlOrRd'), vmin=40, vmax=235)
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.5, c=df.Ipm25, s=5, cmap=plt.get_cmap('magma'), vmin=0, vmax=275)
    #ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.6, c=df.Ipm25, s=20, cmap=cmap, vmin=10, vmax=245)
    ax.set_title('Fairfield Fire Air Quality Index')
    ax.text(0.1, 0.1, str(start_time), transform=ax.transAxes, color='w')
    ax.set_xlim(bbox[0],bbox[1])
    ax.set_ylim(bbox[2],bbox[3])
    ax.imshow(map_plt, zorder=0, extent = bbox, aspect= 'auto')
    plt.savefig(img_fname, bbox_inches='tight', pad_inches=0)
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