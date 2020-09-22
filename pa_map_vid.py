#pa_map video maker
#James S. Lucas 20200920

import cv2
import os
import re

#user_directory = r' '
matrix5 = r'd:\Users\James\OneDrive\Documents\House\PurpleAir\pa_map_plot'
servitor = r'c:\Users\Jim\OneDrive\Documents\House\PurpleAir\pa_map_plot'
wsl_ubuntu_matrix5 = r'/mnt/d/Users/James/OneDrive/Documents/House/PurpleAir/pa_map_plot'
wsl_ubuntu_servitor = r'/mnt/c/Users/Jim/OneDrive/Documents/House/PurpleAir/pa_map_plot'

# Change this variable to point to the desired directory above. 
data_directory = matrix5

root_path = data_directory + os.path.sep
images_folder = 'images'
images_path = root_path + images_folder + os.path.sep 
vid_filename = 'pa_tv.mp4'
vid_full_file_path = root_path + vid_filename 


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
def generate_video(images_path, vid_full_file_path): 
    os.chdir(images_path) 
      
    images = [img for img in os.listdir(images_path) 
              if img.endswith(".jpg") or
                 img.endswith(".jpeg") or
                 (img.endswith(".png") and not img.startswith("map"))] 
    images = sort_nicely(images)

    # Array images should only consider 
    # the image files ignoring others if any 
    #print(images)  
  
    frame = cv2.imread(os.path.join(images_path, images[0])) 
  
    # setting the frame width, height width 
    # the width, height of first image 
    height, width, layers = frame.shape   
  
  
    #video = cv2.VideoWriter(vid_filename, 0, 15, (width, height))  
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(vid_full_file_path, fourcc, 30, (width, height))  

    # Appending the images to the video one by one 
    for image in images:  
        video.write(cv2.imread(os.path.join(images_path, image)))  
      
    # Deallocating memories taken for window creation 
    cv2.destroyAllWindows()  
    video.release()  # releasing the video generated 
  
  
# Calling the generate_video function 
generate_video(images_path = images_path, vid_full_file_path = vid_full_file_path) 