from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(255), unique=True, nullable=False)
    username   = db.Column(db.String(100), nullable=False)
    avatar     = db.Column(db.String(50), default='skull')
    is_admin   = db.Column(db.Boolean, default=False)
    is_dev     = db.Column(db.Boolean, default=False)
    is_creator = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id':         self.id,
            'email':      self.email,
            'username':   self.username,
            'avatar':     self.avatar,
            'is_admin':   self.is_admin,
            'is_dev':     self.is_dev,
            'is_creator': self.is_creator,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'

    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(255), nullable=False)
    code       = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AppToken(db.Model):
    """Временные токены для авторизации внешних приложений через Nomchat ID"""
    __tablename__ = 'app_tokens'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    app_id     = db.Column(db.String(100), nullable=False)
    token      = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('app_tokens', cascade='all, delete-orphan'))
