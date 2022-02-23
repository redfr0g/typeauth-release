from sqlalchemy.orm import relationship
from db import db

table_args__ = {'extend_existing': True}

# user table for first factor
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    password = db.Column(db.String(128))
    biometric = relationship("Biometric")

# biometric table with classification parameters
class Biometric(db.Model):
    __tablename__ = 'biometric'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hold_mean = db.Column(db.Float)
    hold_median = db.Column(db.Float)
    idle_mean = db.Column(db.Float)
    idle_median = db.Column(db.Float)
    shift_count = db.Column(db.Integer)
    backspace_count = db.Column(db.Integer)
    is_capslock = db.Column(db.Boolean)
