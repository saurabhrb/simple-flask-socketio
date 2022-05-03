from flask import Flask
from werkzeug.exceptions import HTTPException
from bot.lib.httperrors import BaseHTTPError, error_response, flask_error_response, uncaught_exception


from config.settings import Config

# Blueprints
# from bot.blueprints.user.views import (
#     user_auth_bp, user_profile_bp,
# )
from bot.blueprints.ui.views import ui_bp
from bot.blueprints.trading.views import bot_bp
# from bot.blueprints.public.views import public_bp
# from bot.blueprints.admin.views import (
#     admin_users_bp
# )

import pprint, traceback

# Extensions
from bot.extensions import (
    db, migrate, socketio, cors, binance_socket_client, binance_client, excel
)


def create_app():
    """
    Create a Flask application using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='gevent', async_handlers=True) 

    error_templates(app)
    register_blueprints(app)
    extensions(app)

    # exception_handler(app)

    return app


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def uncaught_exception_wrapper(error):
        return uncaught_exception(error, debug=app.debug)

    app.errorhandler(BaseHTTPError)(error_response)  # HTTP errors specifically raised by the app
    app.errorhandler(HTTPException)(flask_error_response)  # HTTP errors raised by flask
    app.errorhandler(Exception)(uncaught_exception_wrapper)  # Uncaught (Non-HTTP) Exceptions

    return None

def register_blueprints(app):
    """
    Register 0 or more blueprints (mutates the app passed in).

    :param app: Flask application instance
    :return: None
     """

    api_blueprints = [bot_bp]
    for blueprint in api_blueprints:
        bp_prefix = blueprint.url_prefix if blueprint.url_prefix is not None else ""
        blueprint.url_prefix = f"/api{bp_prefix}"

    pages_blueprints = [ui_bp]

    blueprints = pages_blueprints + api_blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # # To list down all the end points
    # if True or app.debug:
    #     print(app.url_map)

    return None

def futures_callback(msg):
    # print('futures_callback')
    try:
        if msg:
            pprint.pprint(msg)
            # if 'data' in msg:
            #     if msg['data']['e'] == 'markPriceUpdate':
            #         print('markPriceUpdate')
            #     elif msg['data']['e'] == 'ORDER_TRADE_UPDATE':
            #         print('ORDER_TRADE_UPDATE')
            #         # self.get_open_trades()
            # elif msg['e'] == 'ACCOUNT_UPDATE':
            #     print('ACCOUNT_UPDATE')
    except:
        print(traceback.format_exc())

def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    excel.init_excel(app)
    db.init_app(app)
    migrate.init_app(app, db, directory=app.config['MIGRATION_DIR'])
    cors.init_app(app, resources={r"/api/*": {"origins": "*", 'expose_headers': ["Content-Disposition"]}})
    
    binance_socket_client.start()
    binance_socket_client.start_futures_socket(callback=futures_callback)
    # binance_socket_client.start_symbol_mark_price_socket(callback=price_ticker_callback, symbol='BTCUSDT', fast=False)
    return None

