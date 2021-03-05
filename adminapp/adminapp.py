from flask import (
    Blueprint, 
    render_template, 
    redirect, 
    url_for, 
    flash,
    request,
    session,
    g,
)

from pf import model as md 

adminapp = Blueprint('adminapp', __name__, 
    # static_url_path='admin',
    template_folder='templates'
    )

@adminapp.before_request
def before_request():
	g.admuser = None
	if 'adm_user_name' in session:
		g.admuser = session["adm_user_name"]

@adminapp.route('/')
def adm_home():
    if not g.admuser:
        flash('You are not administrator, please login as pf admin.')
        return redirect(url_for('adminapp.adm_login'))
    return render_template('adminapp/admin_dashb.html')

@adminapp.route('/login', methods=['GET','POST'])
def adm_login():

    if  request.method == 'POST':
    
        session.pop('adm_user_name', None)
        auname = request.form.get('admusern', "")
        aupswd = request.form.get('password', "")
        # hash_upswd = hashlib.md5(upswd.encode()).hexdigest()	

        # check  uname, password in DB
        usern = "admin"  # md.read_user(uname)
        pswd = "admin"

        if usern == auname and pswd == aupswd :
            session['adm_user_name'] = usern
            g.admuser = usern
            flash(f"You are successfully logged in as admin user: {usern}")
            return redirect(url_for('adminapp.adm_home'))
        
        flash('Try login again...')
        return redirect(url_for('adminapp.adm_login'))        

    # GET
    return render_template('adminapp/floginadm.html')

@adminapp.route('/logout')
def adm_logout():
	session.pop('adm_user_name', None)
	return redirect(url_for('adminapp.adm_home'))
