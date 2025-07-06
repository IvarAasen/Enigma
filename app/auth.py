from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('routes.chat'))
        else:
            flash('Invalid credentials')

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('confirm')

        user_exists = User.query.filter_by(username=username).first()

        if user_exists:
            flash('Username already exists')
        elif password1 != password2:
            flash('Passwords do not match')
        elif len(password1) < 4:
            flash('Password must be at least 4 characters')
        else:
            new_user = User(
                username=username,
                password=generate_password_hash(password1)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!')
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
