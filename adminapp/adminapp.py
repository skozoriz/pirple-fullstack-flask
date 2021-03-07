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

# from pf import model as md 
from . import adminapp_model as mda

adminapp = Blueprint('adminapp', __name__, 
    # static_url_path='admin',
    template_folder='templates'
    )

@adminapp.before_request
def before_request():
	g.admuname = None
	if 'adm_user_name' in session:
		g.admuname = session["adm_user_name"]

@adminapp.route('/')
def adm_home():
    if not g.admuname:
        flash('You are not administrator, please login as pf admin.')
        return redirect(url_for('adminapp.adm_login'))

    # read ncount users registered total
    ncount = mda.count_user(case='all')
    # read n24count users registed for last 24 hours
    n24count = mda.count_user(case='24h')
    # read tlcount task lists total
    tlcount = mda.count_tlist(case='all')
    # read tl24count task lists created for last 24 hours   
    tl24count = mda.count_tlist(case='24h')
    return render_template('adminapp/admin_dashb.html',
        ncount=ncount,
        n24count=n24count,
        tlcount=tlcount,
        tl24count=tl24count
    )

@adminapp.route('/users')
def adm_usermgmt():
    if not g.admuname:
        flash('You are not administrator, please login as pf admin.')
        return redirect(url_for('adminapp.adm_login'))
    return render_template('adminapp/admin_users.html')

@adminapp.route('/login', methods=['GET','POST'])
def adm_login():

    if  request.method == 'POST':
    
        session.pop('adm_user_name', None)
        fauname = request.form.get('admusern', "")
        faupswd = request.form.get('password', "")
        print(f'  :::[adm_login] fauname={fauname} faupswd={faupswd}')
        # hash_upswd = hashlib.md5(upswd.encode()).hexdigest()	

        # check  uname, password in DB
        au = mda.read_adminuser(fauname)
        print(f'  :::[adm_login] au={au}')
        # usern = "admin"  # md.read_adminuser(auname)
        # pswd = "admin"

        if au.uname == fauname and au.upasswd == faupswd :
            session['adm_user_name'] = au.uname
            g.admuname = au.uname
            flash(f"You are successfully logged in as admin user: {au.uname}")
            return redirect(url_for('adminapp.adm_home'))
        
        flash('Try login again...')
        return redirect(url_for('adminapp.adm_login'))        

    # GET
    return render_template('adminapp/floginadm.html')

@adminapp.route('/logout')
def adm_logout():
	session.pop('adm_user_name', None)
	return redirect(url_for('adminapp.adm_home'))
