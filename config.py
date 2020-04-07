import sqlite3

# Default config
class BaseConfig(object):
    DEBUG = False
    # directory containing user uploaded images
    IMAGE_UPLOADS = '/Users/yohana/desktop/flask/uploads'
    # Image extentions that the app can work with
        # Note: allowed extentions need to take into account the supported formats in
        # the PIL libarary https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html#psd
    ALLOWED_EXTENSIONS = ["BMP", "ICO", "PNG", "JPG", "JPEG", "GIF"]

    # Connect database
    CONNECT = sqlite3.connect("database.db", check_same_thread = False)
    DB = CONNECT.cursor()

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

class TestConfig(BaseConfig):
    DEBUG = True
    Testing = True
    WTF_CSRF_ENABLED = False
    IMAGE_UPLOADS = '/Users/yohana/desktop/flask/test_uploads'
