from flask import Flask, request, send_from_directory, send_file, abort, after_this_request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from zipfile import ZipFile, ZIP_DEFLATED
import sqlite3
import os
import uuid
import requests
import zipfile

# Start Flask
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# Get DB variables to work with
connect = app.config["CONNECT"]
db = app.config["DB"]
image_uploads = app.config["IMAGE_UPLOADS"]

# Checks if file extention is allowed, returns True/False
def allowed_extention(image):
    if not "." in image:
        return False

    extention = image.rsplit(".", 1)[1]

    if extention.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False

################################################################################
# Upload one or more image files
#   Files should be provided in the "files" request attribute in the following format:
#
#        files = {"file1_name.ext": "file1_bytes", "file2_name.ext": file2_bytes...}
#
#   Returns json object -> {"image1_name": "image1_id", "image2_name": "image2_id"}
################################################################################

@app.route("/upload_images", methods=['POST'])
def upload_images():
    if request.files:
        file_ids = {}
        for file in request.files:
            
            # Handle empty file names
            if file == "":
                return "no_file_name"

            # Ensure that file was received
            file_data = request.files[file]
            if file_data == None or file_data == "":
                 return "No or empty file received"

            # Make sure file type is valid
            if allowed_extention(file) == False:
                return "Invalid file type"
           
            # Make sure that we store secure filename
            file_name = secure_filename(file)
            file_name_only, file_ext = file_name.rsplit(".", 1)
            
            # Save Image to designated folder
            file_data.save(os.path.join(image_uploads, file_name))

            # generate unique id and insert file information into database
            id = str(uuid.uuid4())
            db.execute("INSERT INTO img (id, name, extention, path) VALUES (:id, :filename, :extention, :path)",
            {"id": id, "filename": file_name_only, "extention": file_ext, "path": image_uploads})
            connect.commit()

            # Add file information to dict that is returned
            file_ids[file_name] = id

        return jsonify(file_ids)
    return 'No images received with request'


################################################################################
# Upload one or more images by URL
#   URLs should be provided in the "json" request attribute in the following format:
#
#        json = {URLS: ["url-1", "url-2"....]}
#
#   Returns json object -> {"image1_name": "image1_id", "image2_name": "image2_id"}
################################################################################

@app.route("/upload_images_url", methods=['POST'])
def upload_images_URL():


    if request.get_json():

        json = request.get_json()
        try:
            urls = json["URLS"]
        except KeyError:
            return '"URLS" not found in JSON\nJSON format -> {"URLS": ["url-1", "url-2"....]}'

        file_ids = {}
        for url in urls:

            # Ensure that URL returns success response when getting image
            r = requests.get(url)
            if r.ok == False:
                return "Request contains bad URL: " + url

            # Make sure that received file is an image
            content_type = r.headers['Content-type'].split('/')[0]
            if content_type != 'image':
                return "URL does not contain an image: " + url

            # Get file name and secure it for insertion into DB
            url_image_name = url.rsplit("/", 1)[1]
            image_name_full = secure_filename(url_image_name)
            image_name, image_ext = image_name_full.rsplit(".", 1)

            # Save file to designated folder
            with open(os.path.join(image_uploads, image_name_full), "wb") as f:
                f.write(r.content)

            # generate unique id and insert file information into database
            id = str(uuid.uuid4())
            db.execute("INSERT INTO img (id, name, extention, path) VALUES (:id, :filename, :extention, :path)",
            {"id": id, "filename": image_name, "extention": image_ext, "path": image_uploads})
            connect.commit()

            # Add to dictionary containing file names and ids to return
            file_ids[image_name_full] = id

        return jsonify(file_ids)

    return "No JSON received with request"

################################################################################
# Gets one or more image by providing the image ID
#   Image IDs should be provided in the "json" request attribute in the following format
#
#       json = {"IMAGES_ID": [image1_id, image2_id....]}
#
#  Returns -> Zip file containing all images
################################################################################

@app.route("/images_by_id", methods=["POST"])
def images_by_id():

    if request.get_json():

        json = request.get_json()
        try:
            ids = json["IMAGES_ID"]
        except KeyError:
            return '"IMAGES_ID" not found in JSON\nJSON format -> {"IMAGES_ID": ["id-1", "id-2"....]}'

        file_names = []
        for id in ids:
            # Get DB data for the ID
            db.execute("SELECT * FROM img WHERE id = :id", {"id": id})
            image = db.fetchall()

            # Check if ID can be found in DB
            if len(image) == 0:
                return 'No data found for image id: ' + id

            image_full_name = image[0][1] + "." + image[0][2]
            # image_path = image[0][3]

            file_names.append(image_full_name)

        # Write files to Zip file
        with ZipFile('images.zip', 'w', ZIP_DEFLATED) as zip_file:
            for file in file_names:
                zip_file.write(os.path.join(image_uploads, file))
                # zip_file.write("uploads/" + file)

        return send_file('images.zip', mimetype='zip', attachment_filename='images.zip')

    else:
        return "No JSON received with request"

################################################################################
# Converts the type of one or more images by id
#   New extention should be provided in the request URL
#   Image_id's should be provided in the "json" request attribute in the following format:
#
#       json = {"IMAGES_ID": [image1_id, image2_id....]}
#
#  Returns -> Zip file containing all images
################################################################################


@app.route("/convert_type/<string:new_extention>", methods=["POST"])
def convert_type(new_extention):

        # Make sure new extention is allowed
        if new_extention.upper() not in app.config["ALLOWED_EXTENSIONS"]:
            return 'New image extention not currently supported'

        if request.get_json():

            json = request.get_json()
            try:
                ids = json["IMAGES_ID"]
            except KeyError:
                return '"IMAGES_ID" not found in JSON\nJSON format -> {"IMAGES_ID": ["id-1", "id-2"....]}'

            file_names = []
            for id in ids:
                # Get DB data for the id
                db.execute("SELECT * FROM img WHERE id = :id", {"id": id})
                image = db.fetchall()

                if len(image) == 0:
                    return 'Image ID not found'

                image_name = image[0][1] + "." + image[0][2]
                path = image[0][3]
                new_image_name = "temp_dir/" + image[0][1] + "." + new_extention

                # Save image in a temporary directory with converted file type
                # NOTE: Not all new formats support the alpha channel hense the conversion to RGB
                image_obj = Image.open(path + "/"+ image_name)
                image_obj = image_obj.convert("RGB")
                image_obj.save(new_image_name)

                file_names.append(new_image_name)

            # Write files to Zip file
            with ZipFile('images.zip', 'w', ZIP_DEFLATED) as zip_file:
                for file in file_names:
                    zip_file.write(file)

            # Remove temporary files after request
            @after_this_request
            def remove_file(response):
                for file in file_names:
                    os.remove(file)
                return response

            return send_file('images.zip', mimetype='zip', attachment_filename='images.zip')

        else:
            return "No JSON received with request"


################################################################################
# Creates thumbnail of max_size from image by ID
#   Image ID and max size should be provided in the request URL
#   Max size format should be: int,int
#
#  Returns -> image thumbnail
################################################################################

@app.route("/create_thumbnail/<string:image_id>/<max_size>")
def create_thumbnail(image_id, max_size):

    # Add input validation
    # Get DB data for the ID
    db.execute("SELECT * FROM img WHERE id = :id", {"id": image_id})
    image = db.fetchall()

    if len(image) == 0:
        return 'Image ID not found'

    # create the thumbnail
    image_name = image[0][1]
    extention = image[0][2]
    size = tuple(map(int, max_size.split(",")))
    image_path = image[0][3] + "/" + image_name + "." + extention

    i = Image.open(image_path)
    i.thumbnail(size)

    # Save the thumbnail
    thumbnail_path = 'temp_dir/{}_thumbnail.{}'.format(image_name, extention)
    i.save(thumbnail_path)

    # Remove thumbnail from temporary directory after request
    @after_this_request
    def remove_file(response):
        os.remove(thumbnail_path)
        return response

    return send_file(thumbnail_path, as_attachment=True)


if __name__ == '__main__':
    app.run()
