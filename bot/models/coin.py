from bot.extensions import db
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict
from datetime import datetime
import pytz

class Coin(get_resource_mixin(db), db.Model):
    __tablename__ = 'coins'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    coin = db.Column(db.String(50), nullable=False)
    exchange = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)


    def __init__(self, coin, exchange):
        self.coin = coin
        self.exchange = exchange
        self.save()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'coin': self.coin,
            'exchange': self.exchange,
            'enabled': self.enabled
        }
    
    def object(self):
        res = dotdict(self.serialize())
        return res
