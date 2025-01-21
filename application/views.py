from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_user, login_required, current_user, logout_user

from application import db
from application.models import Account

views = Blueprint('views', __name__)


@views.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@views.route('/')
def index():
    return render_template('index.html')

@views.route('/dashboard')
@login_required
def dashboard():
    # Retrieve the user's accounts
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(account.balance for account in accounts)
    return render_template('dashboard.html', accounts=accounts, total_balance=total_balance)


@views.route('/contact')
def contact():
    return render_template('contact.html')

@views.route('/create_account', methods=['GET', 'POST'])
@login_required
def create_account():
    # Create a new account for the current user
    new_account = Account(balance=0, user=current_user)  # Passing the current_user directly
    db.session.add(new_account)
    db.session.commit()
    flash("New account created successfully!", category="success")
    return redirect(url_for('views.dashboard'))


@views.route('/deposit', methods=['POST'])
@login_required
def deposit():
    amount = request.form.get('amount')
    account_identifier = request.form.get('account_identifier')

    if not amount or not account_identifier:
        flash("Amount or account identifier is missing.", category="error")
        return redirect(url_for('views.dashboard'))

    amount = float(amount)
    account = Account.query.filter_by(account_identifier=account_identifier).first()

    if not account:
        flash("Account not found.", category="error")
        return redirect(url_for('views.dashboard'))

    result = current_user.deposit(account.id, amount)

    if "success" in result:
        flash(result, category="success")
    else:
        flash(result, category="error")

    return redirect(url_for('views.dashboard'))


@views.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    amount = request.form.get('amount')
    account_identifier = request.form.get('account_identifier')

    if not amount or not account_identifier:
        flash("Amount or account identifier is missing.", category="error")
        return redirect(url_for('views.dashboard'))

    amount = float(amount)
    account = Account.query.filter_by(account_identifier=account_identifier).first()

    if not account:
        flash("Account not found.", category="error")
        return redirect(url_for('views.dashboard'))

    result = current_user.withdraw(account.id, amount)

    if "success" in result:
        flash(result, category="success")
    else:
        flash(result, category="error")

    return redirect(url_for('views.dashboard'))


@views.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    account_identifier = request.form.get('account_identifier')

    if not account_identifier:
        flash("Account identifier is missing.", category="error")
        return redirect(url_for('views.dashboard'))

    account = Account.query.filter_by(account_identifier=account_identifier).first()

    if not account:
        flash("Account not found.", category="error")
        return redirect(url_for('views.dashboard'))

    result = current_user.delete_account(account.id)

    if "success" in result:
        flash(result, category="success")
    else:
        flash(result, category="error")

    return redirect(url_for('views.dashboard'))
