from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с заявками (один ко многим)
    requests = db.relationship('Request', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.login}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'phone': self.phone,
            'email': self.email,
            'login': self.login,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%d.%m.%Y %H:%M') if self.created_at else ''
        }


class Request(db.Model):
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    preferred_date = db.Column(db.String(50), nullable=False)
    preferred_time = db.Column(db.String(20), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default='новая заявка')
    cancel_reason = db.Column(db.String(300), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Request {self.id} - {self.status}>'
    
    def to_dict(self):
        status_ru = {
            'новая заявка': '🟡 Новая',
            'в работе': '🔵 В работе',
            'выполнено': '✅ Выполнено',
            'отменено': '❌ Отменено'
        }
        
        return {
            'id': self.id,
            'address': self.address,
            'contact_phone': self.contact_phone,
            'service_type': self.service_type,
            'preferred_date': self.preferred_date,
            'preferred_time': self.preferred_time,
            'payment_type': self.payment_type,
            'status': self.status,
            'status_display': status_ru.get(self.status, self.status),
            'cancel_reason': self.cancel_reason,
            'created_at': self.created_at.strftime('%d.%m.%Y %H:%M') if self.created_at else ''
        }