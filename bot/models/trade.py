from bot.extensions import db
from bot.models import Coin, Frame, Botconfig, Account, Alert, Wallet
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict

from datetime import date, datetime
import pytz
import json, traceback
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict

class Trade(get_resource_mixin(db), db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey(Alert.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey(Wallet.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    
    coin_id = db.Column(db.Integer, db.ForeignKey(Coin.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    frame_id = db.Column(db.Integer, db.ForeignKey(Frame.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    botconfig_id = db.Column(db.Integer, db.ForeignKey(Botconfig.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey(Account.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)

    coin_name = db.Column(db.String(10), nullable=False)
    frame_name = db.Column(db.String(10), nullable=False)

    type = db.Column(db.String(10), nullable=False)
    leverage = db.Column(db.String(15), default='1x', nullable=False)
    margin = db.Column(db.Float, default=0.0, nullable=False)

    open_activation_price = db.Column(db.Float, nullable=False)
    open_call_back_rate = db.Column(db.Float, nullable=False)
    open_trailing_stop_price = db.Column(db.Float, nullable=False)
    open_price = db.Column(db.Float, nullable=True)
    
    close_activation_price = db.Column(db.Float, nullable=False)
    close_call_back_rate = db.Column(db.Float, nullable=False)
    close_trailing_stop_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=True)
    
    qty = db.Column(db.Float, nullable=True)
    fees = db.Column(db.Float, nullable=True)
    pnl = db.Column(db.Float, nullable=True)
    pnl_percent = db.Column(db.Float, nullable=True)

    created_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    trade_time = db.Column(db.Float, default=0.0, nullable=False)


    def __init__(self, wallet, alert):
        self.alert_id = alert.id
        self.wallet_id = wallet.id

        # alert = Alert.query.filter_by(id=self.alert_id).first()
        # wallet = Wallet.query.filter_by(id=self.wallet_id).first()

        self.coin_id = wallet.id
        self.frame_id = alert.frame_id
        self.botconfig_id = wallet.account.botconfig_id
        self.account_id = wallet.account.id

        self.coin_name = alert.coin_name
        self.frame_name = alert.frame_name
        
        self.type = alert.action

        self.open_activation_price = alert.price
        self.open_call_back_rate = wallet.account.botconfig.trailing_stop_open_percent
        self.open_trailing_stop_price = self.open_activation_price * (1 + (self.open_call_back_rate/100))

        # changes when open_price is updated
        self.close_activation_price = alert.price * (1 + (wallet.account.botconfig.activation_close_price_percent/100))
        self.close_call_back_rate = wallet.account.botconfig.trailing_stop_close_percent
        self.close_trailing_stop_price = self.close_activation_price * (1 + (self.close_call_back_rate/100))

        if self.open_call_back_rate == 0:
            self.open(wallet, self.open_activation_price)
        else:
            self.save()
            # binance order thread(self.id, self.account_id), callback => Trade.open(price)
    
    def open(self, open_price):
        self.open_price = open_price
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        self.close_activation_price = self.open_price * (1 + (wallet.account.botconfig.activation_close_price_percent/100))

        if  wallet.open_long_trade_id is None and wallet.open_short_trade_id is None:
            balance_use = wallet.balance / 2
        else:
            balance_use = wallet.balance
        self.qty = (balance_use * wallet.account.botconfig.trade_size) / self.open_price
        self.updated_on = datetime.now(pytz.utc)
        self.save()
        wallet.update_wallet_balance(self)

    def fees_(self, fees):
        # event callback of Binance socket
        self.updated_on = datetime.now(pytz.utc)
        self.fees += fees
        self.save()

    def close(self, close_price):
        # event callback of Binance socket
        self.close_price = close_price
        # update PNL
        self.pnl = (self.close_price - self.open_price) * self.qty
        self.pnl_percent = 100 * ((self.close_price - self.open_price) / self.open_price)
        if type == 'Short':
            self.pnl *= -1
            self.pnl_percent *= -1

        self.updated_on = datetime.now(pytz.utc)
        self.trade_time = (self.updated_on - self.created_on).total_seconds()
        self.save()
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        wallet.update_wallet_balance(self)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'wallet_id': self.wallet_id,
            'coin_id': self.coin_id,
            'frame_id': self.frame_id,
            'botconfig_id': self.botconfig_id,
            'account_id': self.account_id,
            'coin_name': self.coin_name,
            'frame_name': self.frame_name,
            'type': self.type,
            'leverage': self.leverage,
            'margin': self.margin,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'fees': self.fees,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'created_on': self.created_on,
            'updated_on': self.updated_on,
            'trade_time': self.trade_time,

            'open_activation_price' : self.open_activation_price,
            'open_call_back_rate' : self.open_call_back_rate,
            'open_trailing_stop_price' : self.open_trailing_stop_price,

            'close_activation_price' : self.close_activation_price,
            'close_call_back_rate' : self.close_call_back_rate,
            'close_trailing_stop_price' : self.close_trailing_stop_price,
        }
    
    def get_trade_data(self):
        trade_json = self.serialize()
        trade_json.update({
            "created_date": str(trade_json["created_on"]),
            "updated_date": str(trade_json["updated_on"]),
            "diff_date": str(self.updated_on - self.created_on),
            "trailing_stop_close_price" : round(trade_json["close_trailing_stop_price"], 4),
            'typ': trade_json["type"],
            "open_price": round(self.open_price, 4),
            "close_price": round(self.close_price, 4) if self.close_price != -1 else "",
            "qty": round(self.qty, 4),
            "pnl": round(self.pnl, 4) if self.pnl != -1 else "",
            'pnl_percent': f"{round(self.pnl_percent, 4)} %" if self.pnl_percent != -1 else "",
        })
        return trade_json
    
    def object(self):
        res = dotdict(self.serialize())
        return res

        