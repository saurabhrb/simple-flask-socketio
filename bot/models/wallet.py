from bot.extensions import db
from bot.models import Coin, Frame, Botconfig, Account
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict

from datetime import date, datetime
import pytz
import json, traceback

class Wallet(get_resource_mixin(db), db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey(Coin.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey(Account.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    
    open_long_trade_id = db.Column(db.Integer, nullable=True) #, db.ForeignKey(Trade.id), #, primary_key=True)
    open_short_trade_id = db.Column(db.Integer, nullable=True) #, db.ForeignKey(Trade.id), #, primary_key=True)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    pnl = db.Column(db.Float, default=0.0, nullable=False)
    pnl_percent = db.Column(db.Float, default=0.0, nullable=False)
    fees = db.Column(db.Float, default=0.0, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)

    coin = db.relationship('Coin')
    account = db.relationship('Account')
    # open_long_trade = db.relationship('Trade', foreign_keys='Wallet.open_long_trade_id')
    # open_short_trade = db.relationship('Trade', foreign_keys='Wallet.open_short_trade_id')

    # enabled = db.column_property(Coin.enabled & Account.enabled)
    enabled = db.Column(db.Boolean, default=False, nullable=False)


    def __init__(self, coin, account, autoSave=True):
        self.coin_id = coin.id
        self.account_id = account.id
        self.balance = account.botconfig.initial_balance
        
        self.enabled = coin.enabled & account.enabled
        
        if autoSave:
            self.save()

    def new_trade(self, trade):
        if trade.type == 'Long':
            self.open_long_trade_id = trade.id
            # self.open_long_trade = new_trade
        elif trade.type == 'Short':
            self.open_short_trade_id = trade.id
            # self.open_short_trade = new_trade
        self.updated_on = datetime.now(pytz.utc)
        self.save()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        res = {
            'id': self.id,
            'coin_id': self.coin_id,
            'account_id': self.account_id,
            'open_long_trade_id': self.open_long_trade_id,
            'open_short_trade_id': self.open_short_trade_id,
            'balance': self.balance,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'fees': self.fees,
            'created_on': self.created_on,
            'updated_on': self.updated_on,
            'enabled' : self.enabled
        }
        # relational objects
        try:
            res['coin'] = self.coin.serialize()
        except:
            pass
        try:
            res['account'] = self.account.serialize()
        except:
            pass
        try:
            res['open_long_trade'] = self.open_long_trade.serialize()
        except:
            pass
        try:
            res['open_short_trade'] = self.open_short_trade.serialize()
        except:
            pass
        return res
    
    def update_wallet_balance(self, trade):
        # deduct self.balance based on trade.open/close_price, trade.qty
        if trade.close_price is not None:
            self.wallet.balance = self.wallet.balance + (trade.qty * trade.close_price)
        elif trade.open_price is not None:
            self.wallet.balance = self.wallet.balance - (trade.qty * trade.open_price)  
        self.updated_on = datetime.now(pytz.utc)
        self.save()
    
    def object(self):
        res = dotdict(self.serialize())
        # relational objects
        try:
            res.coin = self.coin.object()
        except:
            pass
        try:
            res.account = self.account.object()
        except:
            pass
        try:
            res.open_long_trade = self.open_long_trade.object()
        except:
            pass
        try:
            res.open_short_trade = self.open_short_trade.object()
        except:
            pass
        return res
