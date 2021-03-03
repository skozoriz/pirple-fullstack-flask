from flask import Flask

# include blueprints
from pf.adminapp.adminapp import adminapp

app = Flask(__name__)

# configure app
app.config.from_object('pf.config')
# app.secret_key = "1234509876!@#$%+_)(*"

# register blueprints imported
app.register_blueprint(adminapp, url_prefix='/admin')

# connect to db for the whole app life
# (one connection for the whole app, not session based)
from . import model as md
md.conn_db()