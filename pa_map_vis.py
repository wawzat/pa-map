# Visualize PA data on a map
#  *** WARNING! *** this program deletes files from a temporary images folder. This is not safed off yet. Use at your own risk.
# James S. Lucas 20201226

from datetime import datetime, timedelta
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import argparse
import config
from pa_get_df import pa_get_df
from get_map import get_map
from pa_map_vid import generate_video
from pa_map_plot import cleanup_files, plot_map


root_path = config.root_path + os.path.sep

map_filename = 'map_dark.png'
map_full_file_path = root_path + os.path.sep + map_filename 
images_path = root_path + config.images_folder
data_path = root_path + config.data_folder


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def get_arguments():
    parser = argparse.ArgumentParser(
    description='generate time-lapse video of PA-II readings on a map.',
    prog='pa_map_plot',
    usage='%(prog)s [-d <data>], [-b <bbox>], [-r <ramge>] [-v <video>], [-f <frames>], [-l <label>], [-o <output>], [-i <interval>], [-s <start>], [-e <end>], [--md], [--nw], [--map]',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g=parser.add_argument_group(title='arguments',
          description='''    -d, --data    optional.  get data from either csv or ThingSpeak.
    -b  --bbox                            optional.  bounding box coordinates, format  SE lon lat NW lon lat. omit SE and NW.
    -r  --range                           optional.  color range of readings. min max
    -m  --marker                          optional.  size of sensor icon circle.
    -v  --video                           optional.  generate video. 
    -f  --frames                          optional.  frames per second.
    -l  --label                           optional.  label for the video.
    -o  --output                          optional.  output filename prefix.
    -i  --interval                        optional.  data average interval. minutes. used for retriving data and the image frame increment.
    -s  --start                           optional.  start date. format "YYYY-MM-DD HH:MM:SS" include quotes. 
    -e  --end                             optional.  end date. format "YYYY-MM-DD HH:MM:SS" include quotes. 
        --md                              optional.  use stored sensor metadata.
        --nw                              optional.  suppress file deletion warning. 
        --map                             optional.   map backgound ((l)ight or (d)ark).                                ''')
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
    g.add_argument('-m', '--marker',
                    type=int,
                    default = 18,
                    dest='marker',
                    help=argparse.SUPPRESS)
    g.add_argument('-v', '--video', action='store_true',
                    dest='video',
                    help=argparse.SUPPRESS)
    g.add_argument('-f', '--frames',
                    type=int,
                    default = 15,
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
    g.add_argument('-i', '--interval',
                    type=str,
                    default = '10',
                    dest='interval',
                    help=argparse.SUPPRESS)
    g.add_argument('-s', '--startdate', 
                    type=valid_date,
                    help=argparse.SUPPRESS)
    g.add_argument('-e', '--enddate', 
                    type=valid_date,
                    help=argparse.SUPPRESS)
    g.add_argument('--md', action='store_true',
                    dest='metadata',
                    help=argparse.SUPPRESS)
    g.add_argument('--nw', action='store_true',
                    dest='no_warning',
                    help=argparse.SUPPRESS)
    g.add_argument('--map',
                    type=str,
                    default = 'd',
                    choices = ['d', 'l'],
                    dest='map',
                    help=argparse.SUPPRESS)

    args = parser.parse_args()
    return(args)

args = get_arguments()

if args.data == 'TS':
    #           SE lon / lat            NW lon / lat
    #bbox = [-117.5298, 33.7180, -117.4166, 33.8188]  #Temescal Valley
    #bbox = [-122.9068, 37.1778, -121.6626, 38.4536]  #Bay Area
    #bbox = [-118.4#32617,33.582019,-117.557831,34.009981]  #Lake Forest to Inglewood
    bbox = args.bbox
    bbox_plot = (bbox[0]-.004, bbox[2]+.004, bbox[1]-.004, bbox[3]+.004)
    bbox_mapbox = (bbox[0]-.004, bbox[1]-.004, bbox[2]+.004, bbox[3]+.004)
    bbox_pa = (str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]))
    dfs = pa_get_df(args.startdate, args.enddate, bbox_pa, args.interval, 'a',args.metadata, args.output)
    df = dfs['a']
    data_file_full_path = data_path + os.path.sep + args.output + "_" + args.startdate.strftime("%Y%m%d") + "_" + args.enddate.strftime("%Y%m%d") + "_a" + ".csv"
    df.to_csv(data_file_full_path, index=False, header=True)
    if args.metadata:
        bbox = (df.Lon.min(), df.Lat.min(), df.Lon.max(), df.Lat.max())
        bbox_plot = (bbox[0]-.004, bbox[2]+.004, bbox[1]-.004, bbox[3]+.004)
        bbox_mapbox = (bbox[0]-.004, bbox[1]-.004, bbox[2]+.004, bbox[3]+.004)
elif args.data == 'CSV':
    items = os.listdir(data_path)
    file_list = [name for name in items if name.endswith("_a.csv")]
    for n, fileName in enumerate(file_list, 1):
        sys.stdout.write("[%d] %s\n\r" % (n, fileName))
    choice = int(input("Select data file[1-%s]: " % n))
    data_file_full_path = data_path + os.path.sep + file_list[choice-1]
    df = pd.read_csv(data_file_full_path)
    bbox = (df.Lon.min(), df.Lat.min(), df.Lon.max(), df.Lat.max())
    bbox_plot = (bbox[0]-.004, bbox[2]+.004, bbox[1]-.004, bbox[3]+.004)
    bbox_mapbox = (bbox[0]-.004, bbox[1]-.004, bbox[2]+.004, bbox[3]+.004)
    

df['created_at'] = pd.to_datetime(df['created_at'])

fig_num = 1
first_datetime = min(df['created_at'])
last_datetime = max(df['created_at'])
vid_filename = args.output + "_" + first_datetime.strftime("%Y%m%d") + "_" + last_datetime.strftime("%Y%m%d") + ".mp4"
vid_full_file_path = root_path + config.video_folder + os.path.sep + vid_filename 


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
time_increment = timedelta(minutes = int(args.interval))

get_map(map_full_file_path, args.map, bbox_mapbox)
map_plt = plt.imread(map_full_file_path)
cleanup_files(images_path, args.no_warning)
while start_time <= last_datetime:
    end_time = start_time + time_increment
    df2 = df[(df['created_at'] >= start_time) & (df['created_at'] <= end_time)]
    fig_num = plot_map(root_path, df2, map_plt, fig_num, start_time, bbox_plot, args.label, args.range, args.marker, args.map)
    start_time = end_time
if args.video:
    generate_video(images_path, vid_full_file_path, args.frames)