import random
import string

from flask import flash
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from . import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0)  # Default balance of 0
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_identifier = db.Column(db.String(12), unique=True, nullable=False)  # New alphanumeric identifier

    # Relationship with User
    user = db.relationship('User', back_populates='accounts')

    def __init__(self, balance=0, user=None):
        self.balance = balance
        self.user = user
        self.account_identifier = self.generate_unique_identifier()

    @staticmethod
    def generate_unique_identifier():
        """Generates a unique 12-character alphanumeric identifier."""
        characters = string.ascii_uppercase + string.digits
        while True:
            identifier = ''.join(random.choices(characters, k=12))
            if not Account.query.filter_by(account_identifier=identifier).first():
                return identifier

    def get_balance(self):
        return self.balance

    def get_id(self):
        return self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # One-to-many relationship with Account
    accounts = db.relationship('Account', back_populates='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_user(cls, email, full_name, password, confirm_password, age):
        # Check if email already exists
        user = cls.query.filter_by(email=email).first()
        if user:
            return "This email already exists."

        # Validate input data
        if len(full_name) < 1:
            return "You need to enter a name."
        elif len(password) < 6:
            return "Password must be at least 6 characters long."
        elif password != confirm_password:
            return "Passwords do not match."
        try:
            age = int(age)
            if age < 18:
                return "You must be 18 or older to register."
        except ValueError:
            return "Age must be a valid number."

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user
        new_user = cls(email=email, full_name=full_name, password=hashed_password, age=age)

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        # Automatically create an account for the user
        return new_user.create_account()

    def create_account(self):
        # Create an account linked to the current user
        new_account = Account(balance=0, user=self)
        db.session.add(new_account)
        db.session.commit()

        flash(f"Account for {self.full_name} created successfully! Account ID: {new_account.id}", category="success")
        return f"Account for {self.full_name} created successfully! Account ID: {new_account.id}"

    def withdraw(self, account_id, amount):
        # Perform withdrawal on a specific account
        account = Account.query.filter_by(id=account_id, user=self).first()
        if account:
            if account.balance >= amount:
                account.balance -= amount
                db.session.commit()
                flash(f"Withdrawal successful from Account {account.account_identifier}. New balance: ${account.balance}", category="success")
                return f"Withdrawal successful from Account {account.account_identifier}. New balance: ${account.balance}"
            else:
                flash("Insufficient funds.", category="error")
                return "Insufficient funds."
        else:
            flash(f"Account {account.account_identifier} not found.", category="error")
            return f"Account {account.account_identifier} not found."

    def deposit(self, account_id, amount):
        # Perform deposit to a specific account
        account = Account.query.filter_by(id=account_id, user=self).first()
        if account:
            account.balance += amount
            db.session.commit()
            flash(f"Deposit successful to Account {account.account_identifier}. New balance: ${account.balance}", category="success")
            return f"Deposit successful to Account {account.account_identifier}. New balance: ${account.balance}"
        else:
            flash(f"Account ID {account.account_identifier} not found.", category="error")
            return f"Account {account.account_identifier} not found."

    def delete_account(self, account_id):
        # Delete an account if it exists
        account = Account.query.filter_by(id=account_id, user=self).first()
        if account:
            db.session.delete(account)
            db.session.commit()
            flash(f"Account {account.account_identifier} has been deleted successfully.", category="success")
            return f"Account {account.account_identifier} has been deleted successfully."
        else:
            flash(f"Account {account.account_identifier} not found.", category="error")
            return f"Account {account.account_identifier} not found."
