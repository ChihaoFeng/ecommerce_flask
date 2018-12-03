import os

from flask import Flask
from flask_mail import Mail

mail = Mail()


def create_app(test_config=None):
    application = Flask(__name__, instance_relative_config=True)
    # application.config.from_mapping(
    #     SECRET_KEY='ecommerce',
    #     DATABASE=os.path.join(application.instance_path, 'flaskr.sqlite'),
    # )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        application.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        application.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(application.instance_path)
    except OSError:
        pass

    mail.init_app(application)

    # a simple page that says hello
    @application.route('/hello')
    def hello():
        return 'Hello, World!'

    from flaskr.db import db
    # register the database commands
    db.init_app(application)

    from flaskr import auth
    application.register_blueprint(auth.bp)
    return application
