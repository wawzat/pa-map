#pa_map video maker
#James S. Lucas 20201023

import cv2
import os
import re

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)
    return(l)


# Video Generating function 
def generate_video(images_path, vid_full_file_path, frames): 
    os.chdir(images_path) 
      
    images = [img for img in os.listdir(images_path) 
              if img.endswith(".jpg") or
                 img.endswith(".jpeg") or
                 (img.endswith(".png") and not img.startswith("map"))] 
    images = sort_nicely(images)

    # Array images should only consider 
    # the image files ignoring others if any 
  
    frame = cv2.imread(os.path.join(images_path, images[0])) 
  
    # setting the frame width, height width 
    # the width, height of first image 
    height, width, layers = frame.shape   
  
  
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(vid_full_file_path, fourcc, frames, (width, height))  

    # Appending the images to the video one by one 
    for image in images:  
        video.write(cv2.imread(os.path.join(images_path, image)))  
      
    # Deallocating memories taken for window creation 
    cv2.destroyAllWindows()  
    video.release()  # releasing the video generated 
  
if __name__ == "__main__":
    import argparse
    import config
    import glob
    import sys

    # Calling the generate_video function 
    def get_arguments():
        parser = argparse.ArgumentParser(
        description='generate time-lapse video from image files.',
        prog='pa_map_vid',
        usage='%(prog)s [-o <filename>], [-f <frames per second>]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        g=parser.add_argument_group(title='arguments',
            description='''    -o, --output    optional.  filename prefix for the video.   
        -f  --frames                          optional.  frames per second.

             ''')
        g.add_argument('-o', '--output',
                        type=str,
                        default = 'no_name',
                        dest='filename',
                        help=argparse.SUPPRESS)
        g.add_argument('-f', '--frames',
                        type=int,
                        default = 15,
                        dest='frames',
                        help=argparse.SUPPRESS)
        args = parser.parse_args()
        return(args)


    args = get_arguments()

    filename = args.output + '.mp4'

    images_path = config.root_path + os.path.sep + config.images_folder
    vid_full_file_path = config.root_path + os.path.sep + config.video_folder + os.path.sep + filename

    files = glob.glob(images_path + os.path.sep + '*.png')

    if not files:
        print("error. no image files found.")
    else:
        generate_video(images_path, vid_full_file_path, args.frames) 
        sys.exit()