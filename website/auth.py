from flask import Blueprint, render_template, redirect, url_for, request, flash
from jinja2 import UndefinedError
from . import db
from .models import User, Band
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.feed'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user, is_Authenticated=is_Authenticated)

# User (Listener) Sign up
@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='pbkdf2:sha1'), isBand=0)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.feed'), user=current_user, is_Authenticated=is_Authenticated)

    return render_template("sign_up.html", user=current_user, is_Authenticated=is_Authenticated)

# Band Sign Up
@auth.route("/sign-up-band", methods=['GET', 'POST'])
def sign_up_band():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = Band.query.filter_by(email=email).first()
        username_exists = Band.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_band = Band(email=email, username=username, password=generate_password_hash(
                password1, method='pbkdf2:sha1'), isBand=1)
            db.session.add(new_band)
            db.session.commit()
            login_user(new_band, remember=True)
            flash('Band Account created!')
            return redirect(url_for('views.feed'), new_band=current_user, is_Authenticated=is_Authenticated)

    return render_template("sign_up_band.html", new_band=current_user, is_Authenticated=is_Authenticated)

def is_Authenticated(user, band):
    try: 
        if user.is_authenticated:
            return True
    except: 
        if band.is_authenticated:
            return True
    else:
        return False


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
