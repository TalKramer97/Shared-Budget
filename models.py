from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_recurring = db.Column(db.Boolean, default=False)

    #foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    hebrew_name = db.Column(db.String(50), nullable=False, server_default='משתמש')
#relationship with the expense table
    expenses = db.relationship('Expense', backref='user', lazy=True)
#foreign key to the household table
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)

class Household(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    join_code = db.Column(db.String(10), unique=True, nullable=False)

    #relationships
    users = db.relationship('User', backref='household', lazy=True)
    expenses = db.relationship('Expense', backref='household', lazy=True)

   
    