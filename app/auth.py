from werkzeug.security import generate_password_hash, check_password_hash
from flask import (Blueprint, render_template,
                   request, url_for, redirect, flash,
                   session, g)
from .models import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

#Do not forget methods get/post
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    #You dont' wanna see the sign up page if you're already logged in
    if g.user:
        return redirect(url_for('tracker.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username, generate_password_hash(password))
        error = None

        existing_user = User.query.filter_by(username = username).first()
        if existing_user == None:
            db.session.add(user)
            db.session.commit()
            #Takes u to the welcome page only if you just registered
            session['just_registered'] = True
            return redirect(url_for('auth.welcome'))
        else:
            error = f'User {username} is already registered.'
            flash(error)

    return render_template('auth/register.html')

#Welcomes new users
@bp.route('/welcome')
def welcome():
    #Only for brand new users
    if not session.get('just_registered'):
        return redirect(url_for('index'))
    session.pop('just registered', None)
    return render_template('auth/welcome.html')

# Do not forget methods GET/POST... please
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        #Data validation
        user = User.query.filter_by(username=username).first()
        if user == None:
            error = 'Invalid user or password [0]'
        elif not check_password_hash(user.password, password):
            error = 'Invalid user or password [1]'

        #Actual login
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('tracker.index'))
    
        flash(error)
    return redirect(url_for('index'))

#Storing session
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id == None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#Implementing login required
import functools
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view




        

        