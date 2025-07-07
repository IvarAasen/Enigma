from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)

    messages_sent = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    messages_received = db.relationship('Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')

    sent_requests = db.relationship('FriendRequest', foreign_keys='FriendRequest.from_user_id', backref='from_user', lazy='dynamic')
    received_requests = db.relationship('FriendRequest', foreign_keys='FriendRequest.to_user_id', backref='to_user', lazy='dynamic')

    def get_friends(self):
        sent = FriendRequest.query.filter_by(from_user_id=self.id, status='accepted').all()
        received = FriendRequest.query.filter_by(to_user_id=self.id, status='accepted').all()
        friends = [req.to_user for req in sent] + [req.from_user for req in received]
        return friends

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')
