from flask import Blueprint, render_template, redirect, url_for
from pf import model as md 

adminapp = Blueprint('adminapp', __name__, 
    # static_url_path='admin',
    template_folder='templates'
    )

@adminapp.route('/')
def index():
    return render_template('adminapp/floginadm.html')