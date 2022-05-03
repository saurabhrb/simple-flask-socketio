from bot.extensions import db
from bot.lib.util_sqlalchemy import get_resource_mixin, AwareDateTime, dotdict
from datetime import datetime
import pytz

class Frame(get_resource_mixin(db), db.Model):
    __tablename__ = 'frames'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    frame = db.Column(db.String(10), nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.now(pytz.utc), nullable=False)


    def __init__(self, frame):
        self.frame = frame
        self.save()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'frame': self.frame,
            'enabled': self.enabled
        }
    
    def object(self):
        res = dotdict(self.serialize())
        return res
