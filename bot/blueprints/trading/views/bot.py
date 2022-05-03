# python lib imports
from datetime import date, datetime
from inspect import trace
import urllib, os, threading
import flask
from sqlalchemy import func
import pandas as pd
import pyexcel_xlsx, json

# 3rd party imports
import pytz, traceback, pprint
import requests
from flask_socketio import emit
from flask import (
    Blueprint,
    redirect,
    current_app as app,
    request,
    flash,
    send_file,
    url_for,
    render_template, make_response, jsonify, after_this_request
)
from bot.models import Wallet, Coin, Alert, Account, Trade

# lib imports
from bot.lib.util_str import is_empty
from bot.lib.util_flask import request_post_json_req, request_get_args_req
from bot.lib import httperrors
from bot.lib import httpsuccess
from bot.lib.httpsuccess import success_response

# project imports
from bot.extensions import db, socketio, binance_socket_client, get_fmt_time, excel, flask_variables
# from bot.models import Trade, Wallet, Botconfig

bot_bp = Blueprint('bot', __name__)

# def price_ticker_callback(msg):
#     # print('price_ticker_callback')
#     try:
#         # if msg:
#         #     pprint.pprint(msg)
#         if msg and 'data' in msg and msg['data']['e'] == 'markPriceUpdate':
#             # {'data':{
#             #     "e": "markPriceUpdate",     // Event type
#             #     "E": 1562305380000,         // Event time
#             #     "s": "BTCUSDT",             // Symbol
#             #     "p": "11794.15000000",      // Mark price
#             #     "i": "11784.62659091",      // Index price
#             #     "P": "11784.25641265",      // Estimated Settle Price, only useful in the last hour before the settlement starts
#             #     "r": "0.00038167",          // Funding rate
#             #     "T": 1562306400000          // Next funding time
#             # },
#             # 'stream': 'btcusdt@markPrice@1s'}
#             coin = msg['data']['s'] + 'PERP'
#             mark_price = float(msg['data']['p'])
#             funding_fee_rate = float(msg['data']['r']) # NEED TO VERIFY
#             funding_fee_time = msg['data']['T']
#             curr_time = msg['data']['E']
            
#             # print(msg['stream'] + ' => ' + coin + " : " + str(mark_price) + 'USDT')
#             # if socket is already reghistered, that means wallet exists

#             # get last open trade for coin
#             # max size can be 2, One open Long, one open Short
#             open_trades = Trade.query.filter_by(coin=coin, close_price=-1.0).all()
#             for trade in open_trades:
#                 if trade is not None:
#                     bot_config = Botconfig.query.order_by(Botconfig._id.desc()).first()
#                     prev_open_trades = Trade.query.filter_by(coin=trade.coin, close_price=-1.0).all()
#                     res = trade.set_trailing_stop_close_price(mark_price, bot_config)
#                     coin_json = get_coin_data(trade.wallet, prev_open_trades=prev_open_trades)
#                     trade_json = trade.get_trade_data()
#                     updated_data = {"coin" : coin_json, "trade": trade_json, "timestamp": get_fmt_time(datetime.now())}
#                     if res == True:
#                         # close the trade
#                         msg = '%s %s Closed Trailing' % (trade.coin ,trade.typ)
#                         print('Trailing Stop CLOSED --> ' + trade.coin + ' typ = ' + str(trade.typ) + ', open_price = ' + str(trade.open_price) + ', open_price = ' + str(trade.close_price) +', trailing_stop_price = ' + str(trade.trailing_stop_price))
#                         updated_data['msg'] = msg
#                         socketio.emit('new_signal', updated_data, broadcast=True,namespace='/spotbot')
#                     elif res != False:
#                         # trailing stop updated
#                         msg = '%s %s Trailing Updated' % (trade.coin ,trade.typ)
#                         updated_data['msg'] = msg
#                         # print('Trailing Stop UPDATED --> ' + trade.coin + ' typ = ' + str(trade.typ) + ' open_price = ' + str(trade.open_price) + ', trailing_stop_price = ' + str(res))
#                         socketio.emit('new_signal', updated_data, broadcast=True,namespace='/spotbot')
#                     elif res == False:
#                         msg = '%s %s Price Update' % (trade.coin ,trade.typ)
#                         updated_data['msg'] = msg
#                         # print('Price UPDATED --> ' + trade.coin + ' typ = ' + str(trade.typ) + ' open_price = ' + str(trade.open_price) + ', trailing_stop_price = ' + str(res))
#                         # socketio.emit('new_signal', updated_data, broadcast=True,namespace='/spotbot')
#                     # TODO : do only price updates, without a notification toast
#                     # socketio.emit('new_signal', updated_data, broadcast=True,namespace='/spotbot')
#                     socketio.sleep(0.1)
#     except:
#         traceback.format_exc()
@bot_bp.route('/main', methods=['GET'])
def index():
    try:
        return render_template('index1.html')
    except:
        print(traceback.format_exc())
        return str(traceback.format_exc()).replace('\n','<br>').replace('\t','  ')

@bot_bp.route('/', methods=['GET'])
def index2():
    try:
        curr_time = datetime.utcnow()
        wallent_cnt = db.session.query(func.count(Wallet.id)).scalar()
        # wallet_res = db.session.query(func.sum(Wallet.balance), func.sum(Wallet.total_pnl)).first()
        server_start_date = Wallet.query.filter_by(id=1).first()[0].created_on
        server_updated_date = Alert.query.order_by(Alert.id.desc()).first()[0].updated_on
        total_wallet_time = curr_time - server_start_date
        total_wallet_time_days = float(total_wallet_time.total_seconds() / (24*3600))
        last_updated_server_time = curr_time - server_updated_date
        wallet_summary = 'Last updated : ' + str(last_updated_server_time) + ' ago<br>'
        total_pnl = 0
        # if wallet_res[1] is not None:
        #     total_pnl = wallet_res[1]
        avg_wallet_pnl = total_pnl / total_wallet_time_days
        
        wallet_summary += 'Count : ' + str(wallent_cnt) + ',' + (' Investment : %0.4f USDT' % (wallent_cnt * 1000)) + (', PNL : %0.4f USDT' % total_pnl) + (', Time : %s' % str(total_wallet_time)) + (', Avg : %0.4f USDT/day' % (avg_wallet_pnl) )

        allAlerts = list(map(lambda x: x.get_alert_data(), Alert.query.order_by(Alert._id.desc()).all()))
        allTrades = list(map(lambda x: x.get_trade_data(), Trade.query.order_by(Trade._id.desc()).all()))
        sample_alert = {
        'buy' : '''
        { 
            "name" : "AISignals", 
            "action" : "Buy", 
            "frame" : "1m", 
            "exchange" : "{{exchange}}", 
            "coin" : "{{ticker}}", 
            "price" : "{{close}}", 
            "timenow" : "{{timenow}}" 
        }
        ''',
        'sell' : '''
        { 
            "name" : "AISignals", 
            "action" : "Sell", 
            "frame" : "1m", 
            "exchange" : "{{exchange}}", 
            "coin" : "{{ticker}}", 
            "price" : "{{close}}", 
            "timenow" : "{{timenow}}" 
        }
        '''
        }
        if len(allAlerts) == 0:
            return success_response(
        httpsuccess.Ok(title="homepage", msg="homepage", data={
            "sample_alert": sample_alert, "app_url": request.url, "allTrades": allTrades,
            "wallet_summary": wallet_summary, "timestamp": get_fmt_time(curr_time)
        })
        )
        return success_response(
        httpsuccess.Ok(title="homepage", msg="homepage", data={
            "sample_alert": sample_alert, "app_url": request.url, "allAlerts": allAlerts, "allTrades": allTrades,
            "wallet_summary": wallet_summary, "timestamp": get_fmt_time(curr_time)
        })
        )
    except:
        print(traceback.format_exc())
        return str(traceback.format_exc()).replace('\n','<br>').replace('\t','  ')

# @bot_bp.route('/signal', methods=['POST'])
# @request_post_json_req
# def signal(input_json):
#     response_success = make_response(
#     jsonify(
#             {'result' : 'success'}
#         ),
#         200,
#     )
#     response_success.headers["Content-Type"] = "application/json"

#     print(input_json)
#     curr_typ = 'Long' if input_json['action'] == 'Buy' else 'Short'
#     alt_typ = 'Short' if curr_typ == 'Long' else 'Long'
#     curr_price = float(input_json['price'])
#     bot_config = Botconfig.query.order_by(Botconfig._id.desc()).first()
#     wallet = Wallet.query.filter_by(coin=input_json['coin']).first()

#     if wallet is None:
#         # first time alert, create new wallet
#         wallet = Wallet(input_json['coin'], input_json['exchange'], input_json['name'], input_json['frame'], float(input_json['price']), input_json['action'], bot_config)
#         binance_socket_client.start_symbol_mark_price_socket(callback=price_ticker_callback, symbol=input_json['coin'].replace('PERP',''), fast=False)
            
#     wallet.alert_count = wallet.alert_count + 1
#     wallet.last_alert_action = input_json['action']
#     wallet.save()

#     # prev alt open trade
#     prev_alt_open_trade = Trade.query.filter_by(coin=wallet.coin, close_price=-1.0, typ=alt_typ).first()
#     prev_same_open_trade = Trade.query.filter_by(coin=wallet.coin, close_price=-1.0, typ=curr_typ).first()
    
#     # if same trade typ is already open
#     if prev_same_open_trade is not None:
#         print('trade_open() --> ' + str(False))
#         bot_config.update_up_time(datetime.utcnow())
#         return response_success

#     # open Long or Short
#     if wallet.balance > 0:
#         # create new trade
#         new_trade = Trade(wallet=wallet)
#         new_trade.coin = new_trade.wallet.coin
#         new_trade.typ = curr_typ
#         new_trade.high_mark_price = curr_price
#         new_trade.open_price = curr_price

#         # if a opposite typ trade is already open, use trade_size => use all remaining balance
#         # else no trade is open, use trade_size/2 => use half of full balance
#         if prev_alt_open_trade is not None:
#             available_balance = 1 * new_trade.wallet.balance
#         else:
#             available_balance = 0.5 * new_trade.wallet.balance
#         new_trade.qty = (available_balance * bot_config.trade_size) / new_trade.open_price
        
#         # current stop_price = min_pnl_close_price
#         if new_trade.typ == "Long":
#             new_trade.trailing_stop_close_price = (new_trade.open_price + (bot_config.min_pnl_change / new_trade.qty)) #* (1 + bot_config.trailing_pnl_percent)
#         else:
#             new_trade.trailing_stop_close_price = (new_trade.open_price - (bot_config.min_pnl_change / new_trade.qty)) #* (1 - bot_config.trailing_pnl_percent)

#         # update wallet trade
#         new_trade.wallet.balance = new_trade.wallet.balance - (available_balance * bot_config.trade_size)
#         new_trade.wallet.last_trade_action = 'Open ' + curr_typ
#         new_trade.wallet.updated_date = datetime.now(pytz.utc)

#         # defaults
#         new_trade.close_price = -1.0
#         new_trade.pnl = -1.0
#         new_trade.pnl_percent = -1.0
#         new_trade.created_date = new_trade.wallet.updated_date
#         new_trade.updated_date = new_trade.wallet.updated_date
#         new_trade.wallet.commit()
#         new_trade.save()
#         print('trade_open() --> ' + str(True))

#         coin_json = get_coin_data(wallet, prev_open_trades=Trade.query.filter_by(coin=new_trade.coin, close_price=-1.0).all())
#         trade_json = new_trade.get_trade_data()
#         msg = '%s %s Opened' % (new_trade.coin ,new_trade.typ)
#         updated_data = {"coin": coin_json, "trade": trade_json, "msg" : msg, "timestamp": get_fmt_time(datetime.now())}

#         # Trigger notifications to all connected clients.
#         # Need to emit from socketio instance rather than the global emit function as we are emitting outside of socketio context
#         print('trade_open() --> emitting new_signal socket')
#         socketio.emit('new_signal', updated_data, broadcast=True,namespace='/spotbot')
#     return response_success
#     return success_response(httpsuccess.Ok(title="New Signal", msg="New Signal", data=input_json))

def generate_related_tables():
    # get coins
    coins = Coin.query.all()
    # get accounts
    accounts = Account.query.all()
            
    Wallets = []

    for coin in coins:
        for account in accounts:
            Wallets.append(Wallet(coin, account, autoSave=False))

    if len(Wallets) > 0:
        db.session.add_all(Wallets)
        db.session.commit()
        print('Generated all wallets')


# Receive a message from the front end HTML
@socketio.on('send_message', namespace='/spotbot')   
def message_recieved(data):
    print(data['text'])
    emit('message_from_server', {'text':'Message recieved!'}, namespace='/spotbot')
    socketio.sleep(0.1)

# Admin flags are sen in flask_variables['admin']
# via websocket 'admin'
@socketio.on('admin', namespace='/spotbot')
def admin_put(field_map):
    global flask_variables
    # field = {
    #     'field_name' : 'field_value'
    # }
    first_pair = next(iter((field_map.items())) )
    if first_pair[0] != '' and first_pair[0] in flask_variables['admin']:
        flask_variables['admin'][first_pair[0]] = first_pair[1]
        socketio.emit('success', str(flask_variables['admin'][first_pair[0]]) + ' updated to ' + str(first_pair[1]), broadcast=True,namespace='/spotbot')
    else:
        print('admin field not found with name ', first_pair[0])
        socketio.emit('error', 'admin field not found with name ' + str(first_pair[0]), broadcast=True,namespace='/spotbot')

@bot_bp.route('/signal', methods=['POST'])
@request_post_json_req
def signal(input_json):
    print(input_json)
    alert = Alert(input_json['coin'], input_json['frame'], input_json['exchange'], float(input_json['price']), input_json['action'], input_json['trigger'])
    print(alert.wallets)
    wallets = json.loads(alert.wallets)
    if len(wallets) == 0:
        print('No wallets enabled for alert_id ' + str(alert.id))
    else:
        # start new trades
        for wallet_id in wallets:
            wallet = Wallet.query.filter_by(id=wallet_id).first()
            # pprint.pprint(wallet.serialize())
            if alert:
                print('Start a new ' + str(alert.action) + ' trade with alert_id = ' + str(alert.id) + ' & wallet_id = ' + str(wallet.id))
                if (alert.action == 'Long' and wallet.open_long_trade_id is not None):
                    print('Existing open order ' + str(alert.action) + ' ;Trade_id : ' + str(wallet.open_long_trade_id) + ', so not opening new one')
                elif (alert.action == 'Short' and wallet.open_short_trade_id is not None):
                    print('Existing open order ' + str(alert.action) + ' ;Trade_id : ' + str(wallet.open_short_trade_id) + ', so not opening new one')
                else:
                    try:
                        if wallet.balance > 0:
                            new_trade = Trade(wallet, alert) #Trade(wallet.object(), alert.object())
                            wallet.new_trade(new_trade)
                            socketio.emit('success', 'TRADE : <br>' + pprint.pformat(new_trade).replace('\n', '<br>').replace('\t', '  '), broadcast=True,namespace='/spotbot')
                        else:
                            print('New Trade Failed, Wallet balance < 0, Wallet_id : ', wallet.id)
                    except:
                        print(traceback.format_exc())
                        print('New Trade Failed')
    response_success = make_response(
    jsonify(
            alert.serialize()
        ),
        200,
    )
    response_success.headers["Content-Type"] = "application/json"

    return response_success


@bot_bp.route('/admin', methods=['GET'])
def admin_get():
    return render_template("admin.html", admin_variables=flask_variables['admin'])

@bot_bp.route('/export_and_delete', methods=['GET'])
def export_and_delete():
    exported_file = doexport(datetime.now().strftime("%m-%d-%Y_%I-%M-%S%p_Archive"))
    db.session.commit()
    db.drop_all()
    db.create_all()
    return exported_file

@bot_bp.route("/export", methods=['GET'])
def doexport(archive=None):
    if archive:
        return excel.make_response_from_tables(db.session, flask_variables['model_classes'], "xlsx", file_name=archive)
    return excel.make_response_from_tables(db.session, flask_variables['model_classes'], "xlsx", file_name='All_Tables')

@bot_bp.route("/import",methods=['GET', 'POST'])
def import_form():
    global flask_variables
    if request.method == 'POST':
        try:
            archive_file = export_and_delete()
            file = request.files['upload-file']
            xl = pd.ExcelFile(file)
            for sheet in xl.sheet_names:
                # if sheet != 'accounts':
                if sheet in flask_variables['db_tables']:
                    df = pd.read_excel(file, sheet_name = sheet)
                    df.to_sql(sheet, con=db.engine, index=False, if_exists='replace',chunksize = 1000)
                    print('added ',sheet)
            # if 'accounts' in xl.sheet_names:
            #     df = pd.read_excel(file, sheet_name = 'accounts')
            #     df.to_sql('accounts', con=db.engine, index=False, if_exists='replace',chunksize = 1000)
            #     print('added ','accounts')
            socketio.emit('success', 'Import completed', broadcast=True,namespace='/spotbot')
            generate_related_tables() # Wallet
            return archive_file
        except:
            print(traceback.format_exc())
            socketio.emit('error', str(traceback.format_exc()).replace('\n','<br>').replace('\t','  '), broadcast=True,namespace='/spotbot')
            return str(traceback.format_exc()).replace('\n','<br>').replace('\t','  ')
    else:
        return render_template("import.html")

