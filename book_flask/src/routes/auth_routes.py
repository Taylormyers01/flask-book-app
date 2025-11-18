from tkinter import EXCEPTION

from flask import Blueprint, request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required
from services.auth_service import register_user, authenticate_user
from logger import logger

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Generic login request form"""
    data = request.json
    username = data.get('username', None)
    password = data.get('password', None)
    found_user = authenticate_user(username, password)
    if found_user:
        logger.info(f'User found {username}')
        login_user(found_user)
        next = request.args.get('next', None)
        if next:
            return redirect(next)
        return redirect(url_for('home', name=found_user.username))
    return 'No User found', 204

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Generic user registration, redirects to home page"""
    if request.method == 'POST':
        try:
            data = request.json
            username = data.get('username', None)
            password = data.get('password', None)
            if register_user(username, password):
                new_user = authenticate_user(username, password)
                login_user(new_user)
                flash(f'Welcome {username}, to Book-Flask!', 'success')
                return redirect(url_for('home'))
        except Exception as e:
            logger.exception(f'Exception while creating user {e}')
            return "Ran into an issue creating user", 204

@auth_bp.route('/logout')
@login_required
def logout():
    """Generic logout, redirects to home page"""
    logout_user()
    return redirect(url_for('home'))
