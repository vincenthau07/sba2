from flask import Flask
import os
import importlib
import config
from app.blueprints.auth import oauth

def create_app():
    """
    Initiate Flask Website, including session lifetime, secret key, loading all blueprints.

    Returns:
        flask.Flask:flask object
    """

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['PERMANENT_SESSION_LIFETIME'] = config.SESSION_LIFETIME

    oauth.init_app(app)

    for module in os.listdir(os.path.join(os.path.dirname(__file__),
                                          'blueprints')
                             ):
        if module[-3:] == '.py':
            print(f"Loading blueprint-{module}...")
            app.register_blueprint(importlib.import_module(f"app.blueprints.{module[:-3]}").blueprint)

    return app