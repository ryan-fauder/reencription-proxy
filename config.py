import os

# You need to replace the next values with the appropriate values for your configuration
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:dtbase321@localhost/proxy_db"

# IPFS API SERVER SETTINGS
IPFS_BASE_URL = "http://127.0.0.1:5001/api/v0"