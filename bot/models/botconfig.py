from bot.extensions import db
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict
from datetime import datetime
import pytz

class Botconfig(get_resource_mixin(db), db.Model):
    __tablename__ = 'botconfigs'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    initial_balance = db.Column(db.Float, default=0.0, nullable=False)
    trade_size = db.Column(db.Float, default=0.0, nullable=False)
    trailing_stop_open_percent = db.Column(db.Float, default=0.0, nullable=False)
    activation_close_price_percent = db.Column(db.Float, default=0.0, nullable=False)
    trailing_stop_close_percent = db.Column(db.Float, default=0.0, nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)


    def __init__(self, initial_balance, trade_size, trailing_stop_open_percent, activation_close_price_percent, trailing_stop_close_percent):
        self.initial_balance = initial_balance
        self.trade_size = trade_size
        self.trailing_stop_open_percent = trailing_stop_open_percent
        self.activation_close_price_percent = activation_close_price_percent
        self.trailing_stop_close_percent = trailing_stop_close_percent
        self.save()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'initial_balance': self.initial_balance,
            'trade_size': self.trade_size,
            'trailing_stop_open_percent': self.trailing_stop_open_percent,
            'activation_close_price_percent': self.activation_close_price_percent,
            'trailing_stop_close_percent': self.trailing_stop_close_percent,
            'enabled': self.enabled
        }
    
    def object(self):
        res = dotdict(self.serialize())
        return res