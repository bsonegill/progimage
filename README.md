# ProgImage

This is a simple flask app that allows users to store and get images by bulk and perform simple manipulations on images via an API.

## Getting Started

### Prerequisites 

Apart from the standard libraries, you will need to install the below, all can be installed with the allmighty PIP:

```
flask
flask-testing
werkzeug
PIL
requests
```
## Files

A brief overview of the files in the repository can be found below, each (python) file has descriptive comments to further elaborate spesific functionality.

* **ProgImage.py:** The main flask app containing API endpoints and their functionality
* **progimage_helpers.py:** Library of functions that can be used to work with the API endpoints
* **test_ProgImage.py:** Unittests for `ProgImage.py`
* **config.py:** Configurations for `ProgImage.py` and `test_ProgImage.py`
* **database.db:** Database containing table `img` that keeps record of uploaded images and their unique ID's

## Directories

* **uploads:** User uploaded images will be stored here
* **temp_dir:** Stores files that are being worked on by `ProgImage.py`, this directory should be empty except when a script is running
* **test_uploads:** contains images that are used for unit testing
