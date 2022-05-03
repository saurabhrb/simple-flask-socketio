import os, subprocess

from bot.lib.Binance import BINANCE

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))

from dotenv import load_dotenv
load_dotenv()

class Config:
    DEBUG = False
    APP_NAME = 'BOT'
    SECRET_KEY = 'secret!'

    # Binance Main Testnet account for price ticker
    BINANCE_TESTNET = True
    BINANCE_API_KEY = 'ee129cad8826f9f90b84ccefff08a36958d152ac9ea37351b655e1f12a286692'
    BINANCE_API_SECRET = 'd479505e6e78a2c4f25eec6ce3694d7d7e6ea484e96a1d2c0777b1c5578f4596'
    
    # APP_VERSION = '1.0'
    # API_PREFIX = f"/api/v{APP_VERSION}"
    # WEBSITE_SERVER = os.getenv('WEBSITE_SERVER', '')
    # API_SERVER = os.getenv('API_SERVER', '')
    # WEBSITE_URLS = {
    #     'home': f"{WEBSITE_SERVER}/home",
    #     'login': f"{WEBSITE_SERVER}/signin",
    #     'reset_password': f"{WEBSITE_SERVER}/reset-password"
    # }

    # # Secret keys
    # AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY', '')
    # OTHERS_SECRET_KEY = os.getenv('OTHERS_SECRET_KEY', '')

    # Database settings
    # replacing postgres url needed for Azure deployment
    SQLALCHEMY_DATABASE_URI = 'postgresql://gyroscope:james007!@binance-tradingbot-postgres.postgres.database.azure.com/postgres?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIGRATION_DIR = os.path.abspath(os.path.join(basedir, 'bot', 'migrations'))

    # # Email config
    # MAIL_SERVER = os.getenv('MAIL_SERVER', '')
    # MAIL_PORT = int(os.getenv('MAIL_PORT', '') or 25)
    # MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', '') == "1"
    # MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    # MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')

    # # Google Oauth
    # GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
    # GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')