import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SECRET_KEY will come from Render (or .env locally)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

    # SQLite database path (carlog.db inside your project)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'carlog.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional: email config (if you're sending email for forgot password)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
