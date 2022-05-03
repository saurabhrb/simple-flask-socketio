from bot.extensions import db
from bot.models import Frame, Botconfig
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict
from datetime import datetime
import pytz

class Account(get_resource_mixin(db), db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, unique=True, primary_key=True) #, autoincrement=True)

    frame_id = db.Column(db.Integer, db.ForeignKey(Frame.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    botconfig_id = db.Column(db.Integer, db.ForeignKey(Botconfig.id, ondelete='CASCADE'), nullable=False) #, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    exchange = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(200), nullable=False)
    api_secret = db.Column(db.String(200), nullable=False)
    testnet = db.Column(db.Boolean, default=False, nullable=False)
    futures_balance = db.Column(db.Float, default=0.0, nullable=False)
    spot_balance = db.Column(db.Float, default=0.0, nullable=False)

    frame = db.relationship('Frame')
    botconfig = db.relationship('Botconfig')

    enabled = db.Column(db.Boolean, default=False, nullable=False)
    # enabled = db.column_property(Frame.enabled & Botconfig.enabled)
    # db.Column(db.Boolean, default=False, nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)

    def __init__(self, frame_id, botconfig_id, username, exchange, api_key, api_secret, testnet):
        self.frame_id = frame_id
        self.botconfig_id = botconfig_id
        self.username = username
        self.exchange = exchange
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        # query balance
        self.futures_balance = 0
        self.spot_balance = 0

        self.enabled = Frame.query.filter_by(id=frame_id).with_entities(Frame.enabled).first().scalar() & Botconfig.query.filter_by(id=botconfig_id).with_entities(Botconfig.enabled).first().scalar()
        
        self.save()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        res = {
            'id': self.id,
            'frame_id': self.frame_id,
            'botconfig_id': self.botconfig_id,
            'username': self.username,
            'exchange': self.exchange,
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'testnet': self.testnet,
            'futures_balance': self.futures_balance,
            'spot_balance': self.spot_balance,
            'enabled' : self.enabled
        }
        # relational objects
        try:
            res['frame'] = self.frame.serialize()
        except:
            pass
        try:
            res['botconfig'] = self.botconfig.serialize()
        except:
            pass
        return res
    
    def object(self):
        res = dotdict(self.serialize())
        # relational objects
        try:
            res.frame = self.frame.object()
        except:
            pass
        try:
            res.botconfig = self.botconfig.object()
        except:
            pass
        return res
