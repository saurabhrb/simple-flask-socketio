from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
# from flask_mail import Mail
from flask_cors import CORS

from bot.lib.python_binance.binance.client import Client
from bot.lib.python_binance.binance import ThreadedWebsocketManager
from config.settings import Config

import traceback, pprint
from datetime import date, datetime

import flask_excel as excel
flask_variables = {
    'admin' :
    {
        'enable_bot' : True,
        'stop_new_trades' : False,
        'close_open_trades' : False
    },
    'model_classes' : [],
    'model_classes_names' : []
}

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(logger=True, engineio_logger=True, allow_upgrades=True)
# mail = Mail()
cors = CORS()
try :
    binance_client = Client(api_key=Config.BINANCE_API_KEY, api_secret=Config.BINANCE_API_SECRET, testnet=Config.BINANCE_TESTNET)
    binance_socket_client = ThreadedWebsocketManager(testnet=Config.BINANCE_TESTNET, api_key=Config.BINANCE_API_KEY, api_secret=Config.BINANCE_API_SECRET, daemon=True)
except:
    traceback.print_exc()

def get_fmt_time(date: date):
    return date.strftime("%d %b %Y, %I:%M:%S %p")
