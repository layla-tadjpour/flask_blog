import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

from myblog.model import User 
from myblog import db

bp = Blueprint('auth', __name__, url_prefix='/auth')



@bp.route('/register', methods=('GET', 'POST'))
def register():
    if not can_register_admin():
        flash('Registration is disabled. Maximum number of administrators reached.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                User.create_user(username, password)
                db.session.commit()
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for("auth.login"))
            except IntegrityError:
                db.session.rollback()
                error = f"User {username} is already registered."
            except Exception as e:
                db.session.rollback()
                error = f"An error occurred: {str(e)}"
            
        flash(error,'error')

    return render_template('auth/register.html')



@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.get_user_by_username(username)

        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.get_user_by_id(user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def can_register_admin(max_admins=1):
    """Check if more admin users can be registered"""
    return User.query.count() < max_admins