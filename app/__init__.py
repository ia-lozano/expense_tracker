from flask import Flask, render_template, g, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from markupsafe import Markup

#Databse object
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
#If you need to run migrations do:
#flask db init
#flask db migrate -m 'first migration'
#flask db upgrade
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DEBUG = True,
        SQLALCHEMY_DATABASE_URI =  'sqlite:///tracker.db'
    )
    db.init_app(app)
    #Do not forget this if you're doing migrations
    migrate.init_app(app, db)

    #Index page
    @app.route('/')
    def index():
        print(f'g.user() =', g.user)
        #You're not supossed to see the very index if you're logged in
        if g.user:
            return redirect(url_for('tracker.index'))
        #But you can see it if you're not logged in
        return render_template('index.html')

    #Importing Blueprints
    from . import auth
    app.register_blueprint(auth.bp)
    from . import tracker
    app.register_blueprint(tracker.bp)

    #Create SQL tables
    with app.app_context():
        db.create_all()

    return app