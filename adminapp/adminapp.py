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
from pf import model as md

adminapp = Blueprint('adminapp', __name__, 
    # static_url_path='admin',
    template_folder='templates'
    )

@adminapp.before_request
def before_request():
	g.admuname = None
	if 'adm_user_name' in session:
		g.admuname = session["adm_user_name"]

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
# URL parameters processed by template
#   pg_style in (1..6), 
#   pg_lines in (10, =12, 20, 24)
#   pg_num_ - page num to be shown (default is '1' or 'first'), '1' or 'first', '2', ... 'n' or 'last'
#   uid_del - user to be promoted for deletion
# variables for template
#   nn - number of users in appuser table
#   mdaproc - procedure from admin model which reads users for one page (template decides)
def adm_usermgmt():
    
    if not g.admuname:
        flash('You are not administrator, please login as pf admin.')
        return redirect(url_for('adminapp.adm_login'))
    
    return render_template(
        'adminapp/admin_users.html', 
        nn=mda.count_user("all"),
        mdaproc=mda.read_users_page
    )

@adminapp.route('/users/<uname>/delete')
def adm_delete_user(uname):

    if not g.admuname:
        flash('You are not administrator, please login as pf admin.')
        return redirect(url_for('adminapp.adm_login'))
    
    if md.delete_user(uname, delete_alldata=True) == 0:
        flash(f"User '{uname}' and it's data were not deleted.")
    else:
        flash(f"User '{uname}' and it's data were successsfully deleted.")

    return redirect(url_for("adminapp.adm_usermgmt", **request.args))

