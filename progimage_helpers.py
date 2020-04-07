import requests
import os
import ast

# Used to control the endpoint host, set to localhost for development
progimage = 'http://127.0.0.1:5000'

#*******************************************************************************
# Sends POST request that uploads all files from a directory to ProgImage
#   Takes one argument `path` that contains the path to the directory to send files from
#   Returns dictionary containing image names as keys and their corresponding id's as values
# ******************************************************************************

def upload_images_from_dir(path):
    endpoint = progimage + '/upload_images'

    images_list = [file for file in os.listdir(path)]

    images = {}
    for file in images_list:
        if not file.startswith('.'):
            fpath = path + "/" + file
            f = open(fpath, 'rb')
            images[file] = f

    r = requests.post(endpoint, files=images)

    return ast.literal_eval(r.text)

#*******************************************************************************
# Sends POST request that uploads images by URL to ProgImage
#   Takes one argument, a dictionary in the following fomat:
#       dict = {"URLS": ["url-1", "url-2"....]}
#   Returns dictionary containing image names as keys and their corresponding id's as values
#*******************************************************************************

def upload_images_URL(urls):

    endpoint = progimage + '/upload_images_url'
    r = requests.post(endpoint, json=urls)

    return ast.literal_eval(r.text)

#*******************************************************************************
# Sends POST request to ProgImage that retreives pre-uploaded images by their ID
#   Takes one argument, a dictionary in the following format:
#       dict = {"IMAGES_ID": ["ID-1", "ID-2"....]}
#   Has no return value but downloads Zip file containing all images requested to the script directory
#*******************************************************************************

def images_by_id(ids):

    endpoint = progimage + '/images_by_id'
    r = requests.post(endpoint, json=ids)

#*******************************************************************************
# Sends POST request containing files who's types are to be changed and the new type extention in the request URL
#   Takes two arguments:
#       A dictionary in the following format:
#           dict = {"IMAGES_ID": [image1_id, image2_id....]}
#       A string containing the desired output extention
#   Has no return value but downloads Zip file containing all images requested to the script directory
#*******************************************************************************

def convert_type(ids, new_extention):

    endpoint = progimage + "/convert_type/" + new_extention
    r = requests.post(endpoint, json=ids)

#*******************************************************************************
# Sends GET request containing image ID to create thumbnail from and the max size of the thumbnail in the request URL
#   Takes two arguments:
#       A string containing the image ID to create thumbnail from
#       A tuple containing the max size of the thumbnail
#   Has no return value but downloads the thumbnail image to the script directory
#*******************************************************************************

def create_thumbnail(image_id, max_size):

    string_max_size = "{},{}".format(max_size[0], max_size[1])
    endpoint = progimage + "/create_thumbnail/" + image_id + "/" + string_max_size
    requests.post(endpoint)

create_thumbnail("f188e117-d5ea-4466-b5fd-4efa471a70d6", (100, 100))









#
