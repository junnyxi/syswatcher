from datetime import datetime
from app import db

TYPE_MAP = {
    'cpu': 1,
    'mem': 2,
    'disk': 3,
    'network': 4,
    'swap': 5
}


class Record(db.Model):
    __tablename__ = 'records'
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Text)
    type = db.Column(db.SMALLINT, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        json_record = {
            'id': self.id,
            'data': self.data,
            'type': TYPE_MAP[self.type],
            'timestamp': self.timestamp,
        }
        return json_record
