from bot.extensions import db
from bot.models import Coin, Frame, Account, Wallet
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict, dotdict

from datetime import date, datetime
import pytz
import json, traceback
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict

class Alert(get_resource_mixin(db), db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    coin_name = db.Column(db.String(10), nullable=False)
    frame_name = db.Column(db.String(10), nullable=False)
    exchange = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    action = db.Column(db.String(10), nullable=False)
    trigger_time = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)

    # calculated
    coin_id = db.Column(db.Integer, db.ForeignKey(Coin.id, ondelete='CASCADE'), nullable=True) #, primary_key=True)
    frame_id = db.Column(db.Integer, db.ForeignKey(Frame.id, ondelete='CASCADE'), nullable=True) #, primary_key=True)

    coin = db.relationship('Coin')
    frame = db.relationship('Frame')

    wallets = db.Column(db.String(1000), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)

    enabled = db.Column(db.Boolean, default=False, nullable=False)


    def __init__(self, coin_name, frame_name, exchange, price, action, trigger_time):
        self.coin_name = coin_name
        self.frame_name = frame_name
        self.exchange = exchange
        self.price = price
        self.action = action
        self.trigger_time = trigger_time

        # calculate coin_id and frame_id
        coin_ = Coin.query.filter_by(coin=coin_name).first()
        frame_ = Frame.query.filter_by(frame=frame_name).first()
        self.coin_id = coin_.id
        self.frame_id = frame_.id

        # all matching accounts for frame_id
        accounts_ = Account.query.filter_by(frame_id=frame_.id).all()
        account_ids = [account_.id for account_ in accounts_]

        # all matching wallets for frame_id and account_id
        wallets_ = Wallet.query.filter(Wallet.coin_id == coin_.id).filter(Wallet.enabled == True).filter(Wallet.account_id.in_(account_ids)).all()
        if len(wallets_) == 0:
            self.enabled = False
            self.wallets = json.dumps({})
        else:
            wallets_dict_ = {}
            for _wallet in wallets_:
                wallets_dict_[_wallet.id] = _wallet.enabled
            self.wallets = json.dumps(wallets_dict_)
        self.save()
    
    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        res = {
            'id': self.id,
            'coin_name': self.coin_name,
            'frame_name': self.frame_name,
            'exchange': self.exchange,
            'price': self.price,
            'action': self.action,
            'trigger_time': self.trigger_time,
            'coin_id': self.coin_id,
            'frame_id': self.frame_id,
            'wallets' : self.wallets,
            'created_on' : self.created_on,
            'enabled': self.enabled
        }
        # relational objects
        try:
            res['coin'] = self.coin.serialize()
        except:
            pass
        try:
            res['frame'] = self.frame.serialize()
        except:
            pass
        return res

    def get_alert_data(self):
        curr_time = datetime.utcnow()
        alert_json = self.serialize()
        
        alert_json.update({
            "created_date" : '%s (%s ago)' % (
            str(alert_json['created_on']), str(curr_time - alert_json['created_on'])),
            "updated_date" : '%s (%s ago)' % (
            str(alert_json['created_on']), str(curr_time - alert_json['created_on'])),
            "total_pnl" : "0 USDT",
            "avg_pnl" : "",
            "avg_pnl_percent" : "0 %",
            "balance" : "0 USDT"
        })

        # time_elapsed = curr_time - alert_json['created_on']
        # time_elapsed_hr = float(time_elapsed.total_seconds() / 3600)
        # if time_elapsed_hr >= 1 and alert_json['total_pnl'] > 0:
        #     alert_json['avg_pnl'] = [
        #         '%0.4f USDT/hr, ' % (alert_json['total_pnl'] / time_elapsed_hr),
        #         '%0.4f USDT/day, ' % ((alert_json['total_pnl'] / time_elapsed_hr) * 24),
        #         '%0.4f USDT/week, ' % ((alert_json['total_pnl'] / time_elapsed_hr) * 24 * 7),
        #         '%0.4f USDT/month' % ((alert_json['total_pnl'] / time_elapsed_hr) * 24 * 7 * 4)
        #     ]

        #     alert_json['avg_pnl_percent'] = [
        #         '%0.4f %%/hr, ' % (alert_json['total_pnl_percent'] / time_elapsed_hr),
        #         '%0.4f %%/day, ' % ((alert_json['total_pnl_percent'] / time_elapsed_hr) * 24),
        #         '%0.4f %%/week, ' % ((alert_json['total_pnl_percent'] / time_elapsed_hr) * 24 * 7),
        #         '%0.4f %%/month' % ((alert_json['total_pnl_percent'] / time_elapsed_hr) * 24 * 7 * 4),
        #     ]

        # if alert_json['total_pnl'] > 0.0:
        #     alert_json['total_pnl'] = '%0.4f USDT in %s' % (alert_json['total_pnl'], str(time_elapsed))
        #     alert_json['total_pnl_percent'] = '%0.4f %% in %s' % (
        #     alert_json['total_pnl_percent'], str(time_elapsed))
        # else:
        #     alert_json['total_pnl'] = ''
        #     alert_json['total_pnl_percent'] = ''

        
        return alert_json

    def object(self):
        res = dotdict(self.serialize())
        # relational objects
        try:
            res.coin = self.coin.object()
        except:
            pass
        try:
            res.frame = self.frame.object()
        except:
            pass
        return res
