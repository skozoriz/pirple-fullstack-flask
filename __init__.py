# from flask import Flask

# include blueprints
# from pf.adminapp.adminapp import adminapp

# app = Flask(__name__)

from . import db
# configure app
# app.config.from_object('pf.config')

# register blueprints imported
# app.register_blueprint(adminapp, url_prefix='/admin')
