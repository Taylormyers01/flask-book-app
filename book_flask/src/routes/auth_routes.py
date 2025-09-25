from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required
from services.auth_service import register_user, authenticate_user
from logger import logger

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        found_user = authenticate_user(request.form['username'], request.form['password'])
        if found_user:
            login_user(found_user)
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('home', name=found_user.username))
        return "Invalid credentials", 401
    return render_template('content/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            return redirect(url_for('auth.login'))
        return "User already exists", 400
    return render_template('content/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
