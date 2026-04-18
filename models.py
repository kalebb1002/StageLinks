from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)

class ActorProfile(db.Model):
    __tablename__ = 'actor_profiles'
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    profile_photo = db.Column(db.String(255))
    user = db.relationship('User', backref=db.backref('actor_profile', uselist=False))

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, primary_key=True)
    company_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    profile_photo = db.Column(db.String(255))
    website = db.Column(db.String(255))
    user = db.relationship('User', backref=db.backref('company_profile', uselist=False))

class ActorCredit(db.Model):
    __tablename__ = 'actor_credits'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    show_name = db.Column(db.String(255))
    theater_name = db.Column(db.String(255))
    role = db.Column(db.String(255))
    month = db.Column(db.String(20))
    year = db.Column(db.Integer)
    user = db.relationship('User', backref=db.backref('actor_credits', lazy=True))

class PastCompanyShow(db.Model):
    __tablename__ = 'prev_company_shows'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    show_name = db.Column(db.String(255))
    month = db.Column(db.String(20))
    year = db.Column(db.Integer)
    description = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref('past_company_shows', lazy=True))