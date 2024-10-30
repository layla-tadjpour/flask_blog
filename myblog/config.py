import os

class Config:
    """Development configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://layla@localhost/blog_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Enable debugging for development