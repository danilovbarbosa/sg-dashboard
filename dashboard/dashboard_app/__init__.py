'''
Application factory.
'''

from flask import Flask
from flask_bootstrap import Bootstrap
#from flask.ext.sqlalchemy import SQLAlchemy   


def create_app():
    # We are using the "Application Factory"-pattern here:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__)

    # Install our Bootstrap extension
    Bootstrap(app)
    
    # Configure app
    app.config.from_object('config')
    
    # Database?
    #db = SQLAlchemy(app)

    # Our application uses blueprints. Import and register the blueprint:
    from .views import dashboard
    app.register_blueprint(dashboard)

    # Initialize navigation
    from .nav import nav
    nav.init_app(app)
    

    if not app.debug:
        # Logging when in production:
        
        #Import necessary modules
        import os
        import sys
        from config import TMPDIR
        import logging
        from logging.handlers import RotatingFileHandler
        #from logging import StreamHandler
        
        file_handler = RotatingFileHandler(os.path.join(TMPDIR, 'dashboard.log.txt'), 'a', 1 * 1024 * 1024, 10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        #app.logger = logging.getLogger(__name__)
        app.logger.setLevel(logging.DEBUG)
        #file_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
        app.logger.info('Dashboard Start Up...')   


    return app


