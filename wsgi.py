# Without monkey pacthing not able to emit events outside flask socketio context
# see: https://github.com/miguelgrinberg/Flask-SocketIO/issues/1144
# also see: https://github.com/miguelgrinberg/Flask-SocketIO/issues/65 for pycharm debugger issue
# from gevent import monkey
# monkey.patch_all()
from time import sleep
# import eventlet
# eventlet.monkey_patch()
# from engineio.async_drivers import gevent

import os
import importlib, inspect

from sqlalchemy.sql.elements import BooleanClauseList
from bot.app import create_app
from bot.extensions import db, socketio, binance_socket_client, flask_variables
# from bot.blueprints.trading.views.bot import price_ticker_callback
from bot.models import Account, Alert, Botconfig, Coin, Frame, Trade, Wallet 

for name, cls in inspect.getmembers(importlib.import_module("bot.models"), inspect.isclass):
    if cls.__module__.startswith('bot.models.') :
        flask_variables['model_classes'].append(cls)
        flask_variables['model_classes_names'].append(name)

app = create_app()

# from dotenv import load_dotenv
# load_dotenv()

@app.before_first_request
def before_first_request():
    global flask_variables
    db.create_all()
    flask_variables['db_tables'] = []
    for tables in db.session.execute("select table_name from information_schema.tables where table_schema = 'public' and table_name not LIKE '%alembic_version%'").all():
        flask_variables['db_tables'].append(tables[0])

    # # get all existing coins and enable price ticker
    # coins = Coin.query.with_entities(Coin.coin).all()
    # for coin in coins:
    #     binance_socket_client.start_symbol_mark_price_socket(callback=price_ticker_callback, symbol=coin.coin.lower(), fast=False)

if __name__ == '__main__':
    print('starting app')
    socketio.run(app, debug = False)
