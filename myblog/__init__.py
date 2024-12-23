import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

# Initialize SQLAlchemy without app context, it will be bound in the create_app function
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is None:
        # load the instance config in instance dir, if it exists), when not testing or in development
       app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize SQLAlchemy with this app
    db.init_app(app)
    migrate.init_app(app, db)


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import db_commands
    db_commands.init_app(app)
    
    return app


