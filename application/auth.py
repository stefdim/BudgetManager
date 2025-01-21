
from flask import Blueprint, render_template, request, flash, redirect, url_for
import re
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.dashboard'))
            else:
                flash('Invalid password.', category='error')
        else:
            flash('Email does not exist', category='error')
    return render_template('login.html', user = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        age = request.form.get('age')  # Get the age from the form

        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email already exists.', category='error')
        elif len(name) < 1:
            flash("You need to enter a name.", category='error')
        elif len(password) < 6:
            flash("Password must be at least 6 characters long.", category='error')
        elif password != confirm_password:
            flash("Passwords do not match.", category='error')
        elif not age.isdigit() or int(age) < 18:  # Ensure age is valid and at least 18
            flash("You must be at least 18 years old to sign up.", category='error')
        else:
            new_user = User(email=email, full_name=name, password=generate_password_hash(password), age=int(age))
            db.session.add(new_user)
            db.session.commit()

            # Create the account for the new user
            new_user.create_account()

            db.session.commit()

            # Log in the newly created user
            login_user(new_user, remember=True)

            flash("Account created and logged in successfully!", category='success')
            return redirect(url_for('views.index'))
    return render_template('sign_up.html', user=current_user)

