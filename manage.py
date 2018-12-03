from flaskr import create_app
from flask_script import Manager

application = create_app()
manager = Manager(application)
