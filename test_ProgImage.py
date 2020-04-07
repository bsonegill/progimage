import unittest
import sqlite3
import requests
import os
from ProgImage import app, db
from flask_testing import TestCase

connect = app.config["CONNECT"]
db = app.config["DB"]

home_url = "http://127.0.0.1:5000/"

# Image to work with throughout the test (as inserted into DB)
img_id_1 = '123546'
img_name_1 = 'python_logo'
img_extention_1 = 'png'
img_full_name_1 = 'python_logo.png'

img_path = app.config["IMAGE_UPLOADS"]

img_id_2 = '789'
img_name_2 = 'ben'
img_extention_2 = 'jpg'
img_full_name_2 = 'ben.jpg'


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        # Insert test images into DB
        db.execute("INSERT INTO img VALUES (:id, :name, :extention, :path )",
        {"id": img_id_1, "name": img_name_1, "extention": img_extention_1, "path": img_path})
        connect.commit()

        db.execute("INSERT INTO img VALUES (:id, :name, :extention, :path )",
        {"id": img_id_2, "name": img_name_2, "extention": img_extention_2, "path": img_path})
        connect.commit()

    def tearDown(self):
        # Remove test image from DB
        db.execute("DELETE FROM img WHERE id={}".format(img_id_1))
        connect.commit()

        db.execute("DELETE FROM img WHERE id={}".format(img_id_2))
        connect.commit()


class FlaskTestCase(BaseTestCase):
    def test_upload_images(self):
        endpoint = home_url + 'upload_images'
        file1 = img_path + '/' + img_full_name_1
        file2 = img_path + '/' + img_full_name_2

        # POST request without files
        r1 = requests.post(endpoint)
        self.assertEqual(r1.text, 'No images received with request')

        # POST request with invalid file type
        files = {img_full_name_1: open("test_uploads/python_logo.png", 'rb'), 'python_logo.pdf': open("test_uploads/python_logo.pdf", 'rb')}
        r2 = requests.post(endpoint, files=files)
        self.assertEqual(r2.text, "Invalid file type")

    def test_upload_images_URL(self):
        endpoint = home_url + 'upload_images_url'
        bad_url = 'https://cdn.arstechnica.net/BAD_URL/Images-977644614-800x869.jpg'
        url = 'https://cdn.arstechnica.net/wp-content/uploads/2019/10/GettyImages-977644614-800x869.jpg'

        # POST request with bad url
        r1 = requests.post(endpoint, json={"URLS": [url, bad_url]})
        self.assertIn('Request contains bad URL:', r1.text)

        # POST request key error in JSON
        r2 = requests.post(endpoint, json={"wrong_key": [url]})
        self.assertIn('"URLS" not found in JSON', r2.text)

if __name__ == '__main__':
    unittest.main()
