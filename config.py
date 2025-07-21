# config.py

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'your-secret-key'  # Change this to something secure
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'carlog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False