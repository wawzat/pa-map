# Visualize PA data on a map
#  *** WARNING! *** this program deletes files from a temporary images folder. This is not safed off yet. Use at your own risk.
# You must establish the appropriate paths to folders below.
# James S. Lucas 20201115

from datetime import datetime, timedelta
from time import strftime
import pytz
import pandas as pd
import matplotlib.pyplot as plt
#import glob
import os
import sys
import argparse
import config
from pa_get_df import pa_get_df
from get_map import get_map
from pa_map_vid import generate_video
from pa_map_plot import cleanup_files, plot_map


# Change this variable to point to the desired directory in config.py. 
data_directory = config.matrix5

root_path = data_directory + os.path.sep

#data_filename = 'bay_area_20201026_20201027.csv'
#data_filename = 'TV_20201108_20201112.csv'
map_filename = 'map_dark.png'

#data_full_file_path = root_path + 'pa_map_plot' + os.path.sep + data_filename
map_full_file_path = root_path + 'pa_map_plot' + os.path.sep + map_filename 

images_folder = 'images'
images_path = root_path + 'pa_map_plot' + os.path.sep + images_folder + os.path.sep 
data_full_path = root_path + 'pa_map_plot' + os.path.sep + 'Data'


def valid_date(s):
    try:
        #print(s)
        #print(" ")
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def get_arguments():
    parser = argparse.ArgumentParser(
    description='generate time-lapse video of PA-II readings on a map.',
    prog='pa_map_plot',
    usage='%(prog)s [-d <data>], [-b <bbox>], [-v <video>], [-f <frames>], [-l <label>], [-o <output>], [-s <start>], [-e <end>]',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g=parser.add_argument_group(title='arguments',
          description='''    -d, --data    optional.  get data from either csv or ThingSpeak.
    -b  --bbox                            optional.  bounding box.
    -v  --video                           optional.  generate video. 
    -f  --frames                          optional.  prepare video frames.
    -l  --label                           optional.  label for the video.
    -o  --output                          optional.  output filename prefix.
    -s  --start                           optional.  start date. format "YYYY-MM-DD HH:MM:SS" include quotes. 
    -e  --end                             optional.  end date. format "YYYY-MM-DD HH:MM:SS" include quotes.           ''')
    g.add_argument('-d', '--data',
                    type=str,
                    default = 'TS',
                    choices = ['CSV', 'TS'],
                    dest='data',
                    help=argparse.SUPPRESS)
    g.add_argument('-b', '--bbox',
                    type=float,
                    nargs = 4,
                    default = [-117.5298, 33.7180, -117.4166, 33.8188],
                    dest='bbox',
                    help=argparse.SUPPRESS)
    g.add_argument('-r', '--range',
                    type=int,
                    nargs = 2,
                    default = [20, 225],
                    dest='range',
                    help=argparse.SUPPRESS)

    g.add_argument('-v', '--video', action='store_true',
                    dest='video',
                    help=argparse.SUPPRESS)
    g.add_argument('-f', '--frames', action='store_true',
                    dest='frames',
                    help=argparse.SUPPRESS)
    g.add_argument('-l', '--label',
                    type=str,
                    default = 'AQI',
                    dest='label',
                    help=argparse.SUPPRESS)
    g.add_argument('-o', '--output',
                    type=str,
                    default = 'no_name',
                    dest='output',
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

output_pathname = root_path + 'pa_map_plot' + os.path.sep + args.output + "_" + args.startdate.strftime("%Y%m%d") + "_" + args.enddate.strftime("%Y%m%d") + ".csv"
vid_filename = args.output + "_" + args.startdate.strftime("%Y%m%d") + "_" + args.enddate.strftime("%Y%m%d") + ".mp4"
vid_full_file_path = root_path + 'pa_map_plot' + os.path.sep + vid_filename 


if args.data == 'TS':
    #           SE lon / lat            NW lon / lat
    bbox = args.bbox
    #bbox = [-117.5298, 33.7180, -117.4166, 33.8188]  #Temescal Valley
    #bbox = [-122.9068, 37.1778, -121.6626, 38.4536]  #Bay Area
    #bbox = [-118.432617,33.582019,-117.557831,34.009981]  #Lake Forest to Inglewood
    bbox_plot = (bbox[0]-.004, bbox[2]+.004, bbox[1]-.004, bbox[3]+.004)
    bbox_mapbox = (bbox[0]-.004, bbox[1]-.004, bbox[2]+.004, bbox[3]+.004)
    bbox_pa = (str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]))
    df = pa_get_df(args.startdate, args.enddate, bbox_pa)
    data_file_full_path = data_full_path + os.path.sep + args.output + "_" + args.startdate.strftime("%Y%m%d") + "_" + args.enddate.strftime("%Y%m%d") + ".csv"
elif args.data == 'CSV':
    items = os.listdir(data_full_path)
    file_list =[name for name in items if name.endswith(".csv")]
    for n, fileName in enumerate(file_list, 1):
        sys.stdout.write("[%d] %s\n\r" % (n, fileName))
    choice = int(input("Select data file[1-%s]: " % n))
    data_file_full_path = data_full_path + os.path.sep + file_list[choice-1]
    df = pd.read_csv(data_file_full_path)
    bbox = (df.Lon.min(), df.Lat.min(), df.Lon.max(), df.Lat.max())
    bbox_plot = (bbox[0]-.004, bbox[2]+.004, bbox[1]-.004, bbox[3]+.004)
    bbox_mapbox = (bbox[0]-.004, bbox[1]-.004, bbox[2]+.004, bbox[3]+.004)
    bbox_pa = (str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]))
    

df.to_csv(data_file_full_path, index=False, header=True)


df['created_at'] = pd.to_datetime(df['created_at'])


fig_num = 1
first_datetime = min(df['created_at'])
last_datetime = max(df['created_at'])
#last_datetime = args.enddate


if args.startdate is not None and args.enddate is not None:
    if args.startdate > args.enddate:
        print("error. start date greater than end date. exiting")
        exit()
    if args.enddate < args.startdate:
        print("error. end date less than start date. exiting")
        exit()


if args.startdate is not None:
    start_time = pytz.utc.localize(args.startdate)
else:
    start_time = first_datetime
if args.enddate is not None:
    last_datetime = pytz.utc.localize(args.enddate)
time_increment = timedelta(minutes = 10)

get_map(map_full_file_path, bbox_mapbox)
map_plt = plt.imread(map_full_file_path)
if args.frames:
    cleanup_files(images_path)
    while start_time <= last_datetime:
        end_time = start_time + time_increment
        df2 = df[(df['created_at'] >= start_time) & (df['created_at'] <= end_time)]
        fig_num = plot_map(root_path, df2, map_plt, fig_num, start_time, bbox_plot, args.label, args.range)
        start_time = end_time
if args.video:
    generate_video(images_path, vid_full_file_path)