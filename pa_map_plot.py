# Visualize PA data on a map
#James S. Lucas 20200921

from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse
from get_map import get_map

#user_directory = r' '
matrix5 = r'd:\Users\James\OneDrive\Documents\House\PurpleAir\pa_map_plot'
servitor = r'c:\Users\Jim\OneDrive\Documents\House\PurpleAir\pa_map_plot'
wsl_ubuntu_matrix5 = r'/mnt/d/Users/James/OneDrive/Documents/House/PurpleAir/pa_map_plot'
wsl_ubuntu_servitor = r'/mnt/c/Users/Jim/OneDrive/Documents/House/PurpleAir/pa_map_plot'

# Change this variable to point to the desired directory above. 
data_directory = matrix5

root_path = data_directory + os.path.sep

data_filename = 'combined_csv_map_plot.csv'
map_filename = 'map_dark.png'

data_full_file_path = root_path + data_filename
map_full_file_path = root_path + map_filename 


def get_arguments():
    parser = argparse.ArgumentParser(
    description='plot PA-II readings on a map every 15 minutes for use in visualization.',
    prog='pa_map_plot',
    usage='%(prog)s [-m <map>]',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g=parser.add_argument_group(title='arguments',
          description='''   -m, --map     optional.  get a map image from mapbox. ''')
    g.add_argument('-m', '--map', action='store_true',
                    dest='map',
                    help=argparse.SUPPRESS)
    args = parser.parse_args()
    return(args)


df = pd.read_csv(data_full_file_path)
df['DateTime_US_Pacific'] = pd.to_datetime(df['DateTime_US_Pacific'])

bbox = (df.Lon.min()-.004, df.Lon.max()+.004, df.Lat.min()-.004, df.Lat.max()+.004)
bbox_mapbox = (bbox[0], bbox[2], bbox[1], bbox[3])
#print(bbox)


def plot_map(root_path, df, map_plt, fig_num, start_time, bbox):
    img_fname = root_path + "images" + os.path.sep + str(fig_num) + '_frame.png'
    fig, ax = plt.subplots(figsize = (8, 7))
    ax.set_axis_off()
    ax.scatter(df.Lon, df.Lat, zorder=1, alpha=0.6, c=df.Ipm25, s=80, cmap=plt.get_cmap('YlOrRd'), vmin=0, vmax=175)
    ax.set_title('Temescal Valley Air Quality Index')
    ax.text(0.1, 0.1, str(start_time), transform=ax.transAxes, color='w')
    ax.set_xlim(bbox[0],bbox[1])
    ax.set_ylim(bbox[2],bbox[3])
    ax.imshow(map_plt, zorder=0, extent = bbox, aspect= 'auto')
    plt.savefig(img_fname, bbox_inches='tight', pad_inches=0)
    plt.close('all')
    fig_num += 1
    return(fig_num)


fig_num = 1
first_datetime = min(df['DateTime_US_Pacific'])
last_datetime = max(df['DateTime_US_Pacific'])
start_time = first_datetime
time_increment = timedelta(minutes = 15)

args = get_arguments()

if args.map:
    get_map(map_full_file_path, bbox_mapbox)


map_plt = plt.imread(map_full_file_path)


while start_time <= last_datetime:
    end_time = start_time + time_increment
    df2 = df[(df['DateTime_US_Pacific'] >= start_time) & (df['DateTime_US_Pacific'] <= end_time)]
    fig_num = plot_map(root_path, df2, map_plt, fig_num, start_time, bbox)
    start_time = end_time