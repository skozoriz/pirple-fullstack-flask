from collections import namedtuple
import hashlib
import datetime as dt

from flask import (
	Flask, 
	g, 	
	session, 
	request, 
	render_template, 
	redirect,
	url_for,
	flash,
	abort,
)

import model as md

app = Flask(__name__)
app.secret_key = "1234509876!@#$%+_)(*"


# @app.before_first_request
# def before_first_request():
#   init db connection here?

@app.before_request
def before_request():

	if app.debug:
		print(f'<<<<<<<<<<<<<<\n[before_request]: { request.method }  {request.full_path}')
		print(f'  >> session.username: { session.get("user_name", "not-exists") }  g.user: { g.get("user", "not-exists") }')
		print(f'  >> request.url: {request.url}')
		print(f'  >> request.referrer: {request.referrer}')
		print(f'  >> request.form: { request.form }') 
		print(f'  >> request.args: { request.args }')
		print(f'  >> request.headers: { request.headers }')

	g.user = None
	if 'user_name' in session:
		g.user = md.read_user(session["user_name"])

	if app.debug:
		print(f'  >> session.username: { session.get("user_name", "not-exists") }  g.user: { g.get("user", "not-exists") }')


# @app.after_request
# def after_request(responce):

# 	if app.debug:
# 		print(f'  >> responce.headers: { responce.headers }')
# 		print(f'[after_request] session.username:{session.get("user_name", "not-exists")}  g.user: {g.get("user", "not-exists")}')
# 		print(f'[after_request] { request.method }  {request.full_path}'')

# 	return(responce)

@app.teardown_request
def teardown_request(responce):
	if app.debug:
		print(f'[teardown_request]: { request.method }  {request.full_path}')
		print(f'>>>>>>>>>>>>>>')
	return(responce)


@app.route('/', methods=['GET'])
def home():
	return render_template('index.html', username='')

@app.route('/about', methods=['GET'])
def about():
	return render_template('about.html')

@app.route('/termsofuse', methods=['GET'])
def termsofuse():
	return render_template('termsofuse.html')

@app.route('/privacy', methods=['GET'])
def privacy():
	return render_template('privacy.html')


@app.route('/signon', methods=['GET','POST'])
def signon():
	
	if  request.method == 'POST':
		uname = request.form.get('username', "")
		upswd = request.form.get('password', "")
		hash_upswd = hashlib.md5(upswd.encode()).hexdigest()
		# try to enter  uname, password in DB
		user =  md.create_user(uname, hash_upswd)
		if user.uid :  # None means unsuccessfull user creation, username exist in db e.g. 
			flash(f'Succesfully signed-up as user {user.uname} - please login')
			return render_template('index.html', username=user.uname)
		else:
			flash('Sign-on unsuccessfull. Try again...')
			return render_template('fsignon.html')

	# GET
	return render_template('fsignon.html')

@app.route('/signoff')
def signoff():

	if not g.user:
		flash('You are not logged-in, and cannot to be signed off, sorry')
		return redirect(url_for('home'))

	uname = g.user.uname

	# get confirmation from user side for sign off
	#  TBD 

	# delete user record from DB and all assosiated data, for uid
	#   task    : ttlid = {{tlist.tlid}}
	#   tlist   : tluid = {{g.uid}}
	#    appuser : uid = {{g.uid}} 	if row_cnt = 0:
	row_cnt = md.delete_user(uname, delete_alldata=False) # error inside del_user now, row_cnt==0

	if row_cnt == 0:
		flash(f'Cannot sign-off for user {uname}: tlists or tasks existed')
	else:
		# log out, if logged in
		if g.user.uname == uname:
			session.pop('user_name', None)
	
	return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

	if  request.method == 'POST':
		
		session.pop('user_name', None)
		uname = request.form.get('username', "")
		upswd = request.form.get('password', "")
		hash_upswd = hashlib.md5(upswd.encode()).hexdigest()	

		# check  uname, password in DB
		user = md.read_user(uname)
	
		if user.uid and user.upasswd == hash_upswd :
			session['user_name'] = user.uname
			g.user = user
			return redirect(url_for('tlists'))
			
		flash('Try login again...')
		return redirect(url_for('login'))        

	# GET		
	return render_template('flogin.html')

@app.route('/logout')
def logout():
	session.pop('user_name', None)
	return redirect(url_for('home'))


# main view I of app: TLISTS <--> tasks for tlist

@app.route('/tlists', methods=['GET'])  
def tlists():

	if not g.user:
		return redirect(url_for('login'))

	tlsts_Tlist = md.read_tlists(g.user.uname) # list of Tlist_ext

	return render_template(
		'tlists.html', 
		list_of_tlists = tlsts_Tlist
	)


@app.route('/tlist', methods=['GET', 'POST'])   # CREATE tlist
@app.route('/tlist/<int:tlist_id>', methods=['GET', 'POST']) # UPDATE tlist
def tlist(tlist_id=None):
	if not g.user:
		return redirect(url_for('login'))
	uname = g.user.uname
	uid = g.user.uid
	
	if  request.method == 'GET':

		if tlist_id is None: 
			# new tlist empty form
			return render_template(
				'ftlist.html',
				TLID = None,
				TLN = '',
				TLPRI = 0,
				TLCOLOR = 'white',
				form_title = f'Create NEW task-list:'
			)	

		else: # existed tlist <-> update
			
			tl = md.read_tlist(tlist_id)

			return render_template(
				'ftlist.html',
				TLN = tl.tlname,
				TLID = tl.tlid,
				TLACTIVE = "checked" if tl.tlactive else "",
				TLPRI = tl.tlpri,
				TLCOLOR = tl.tlcolor,
				form_title = f'Update task-list:'
			)		

	elif request.method == 'POST':
		
		if tlist_id is None:

			# new tlist to be created
			
			tlactive = request.form.get("tlactive", False)
			tlpri = request.form.get("tlpri", 0)
			tlcolor = request.form.get("tlcolor", "white")
			new_tl = md.create_tlist(
				uname=uname, 
				tlname=request.form.get("tlname", "Default Tlist Name"),
				tlpri=tlpri,
				tlcolor=tlcolor,
			)
			if new_tl == md.TLIST_EMPTY : 
				flash('Task list was not created')
			return redirect(url_for('tlists'))

		else: # existed tlist, update 
			
			tl = md.Tlist(*md.read_tlist(tlist_id))

			# 	change updated fields
			f_tlname = request.form.get('tlname', "")
			f_tlactive = request.form.get("tlactive", False)
			f_tlpri = request.form.get("tlpri", 0)
			f_tlcolor = request.form.get("tlcolor", "white")
			
			print(f'[POST tlist: {tlist_id}] n:{f_tlname}, a:{f_tlactive}, p:{f_tlpri}')  # debug print
			tlname = f_tlname if f_tlname != tl.tlname else tl.tlname
			tlactive = f_tlactive if f_tlactive != tl.tlactive else tl.tlactive
			tlpri = f_tlpri if f_tlpri != tl.tlpri else tl.tlpri
			tlcolor = f_tlcolor if f_tlcolor != tl.tlcolor else tl.tlcolor

			#	update tlist
			upd_tl = md.update_tlist(
				tlid=tlist_id, 
				tlname=tlname, 
				tlactive=tlactive, 
				tlpri=tlpri,
				tlcolor=tlcolor
			)
			if upd_tl == md.TLIST_EMPTY: 
				flash('Task list was not updated')
			return redirect(url_for('tlists'))

	else:  # no pass here anyway
		abort(400)


@app.route('/tlist/<int:tlist_id>/delete', methods=['GET']) # DELETE tlist
def tlist_delete(tlist_id=None):

	if not g.user:
		return redirect(url_for('login'))
	if tlist_id is None: 
		return redirect(url_for('tlists'))	
	
	rows_deleted = md.delete_tlist(tlid=tlist_id, delete_alldata=False)
	if rows_deleted == 0:
		flash('Task list was not deleted')
	return redirect(url_for('tlists'))	



# alternative view of app: all TASKS 
# all the tasks from all the tlists in one united view

@app.route('/tlist/all/tasks', methods=['GET'])
def tasksall(tlist_id=None):

	if not g.user:
		return redirect(url_for('login'))

	tasks_Task_ext = md.read_tasksall(uid=g.user.uid)			# list of tuples

	# md.print_namedtuplelist(md.Task_ext, tasks_Task_ext, prefixstr='---0>')
	
	if request.args.get("altsort") == "Yes":
		# Alternative sort order: ttlpi DESC, ttl.name ASC, tpri Desc, tname Asc 
		tasks_Task_ext = sorted(tasks_Task_ext, key=lambda x:(-x.ttlpri, x.ttlname, -x.tpri, x.tname))
	
	# md.print_namedtuplelist(md.Task_ext, tasks_Task_ext, prefixstr='---1>')
	
	return render_template(
		'tasksall.html', 
		list_of_tasks = tasks_Task_ext
	)	


# main view II of app: tlists --> TASKS for one tlist

@app.route('/tlist/<int:tlist_id>/tasks', methods=['GET'])  
def tasks(tlist_id=None):

	if not g.user:
		return redirect(url_for('login'))

	tasks_Task = md.read_tasks(tlist_id)			# list of tuples

	tl = md.read_tlist(tlist_id)

	return render_template(
		'tasks.html', 
		TLID = tlist_id,
		TLNAME = tl.tlname,
		TLCOUNT = tl.tltcount,
		list_of_tasks = tasks_Task
	)	


@app.route('/tlist/<int:tlist_id>/task', methods=['GET', 'POST'])   # CREATE task
@app.route('/tlist/<int:tlist_id>/task/<int:task_id>', methods=['GET', 'POST'])  # UPD task
def task(tlist_id=None, task_id=None):

	if not g.user:
		return redirect(url_for('login'))

	if  request.method == 'GET':

		# save initial referer for requested operation (new or upd) of current user 
		form_get_referrer = request.referrer
		session["form_get_referrer"] = form_get_referrer

		mode = request.args.get('mode', '')
		list_of_tlists = md.read_tlists(uname=g.user.uname)
		
		if task_id is None: 
			# CREATE 1, GET

			return render_template(
				'ftask.html',
				form_title = 'Create new task',
				TLID = tlist_id,
				TPRI = 0,
				TID = None,
				TLISTS = list_of_tlists
			)

		else:
			# UPD 1, GET

			# read task
			t = md.read_task(tid=task_id)
			# set form field values from task fields
			# show form with filled fields
			return render_template(
						'ftask.html',
						TLID = t.ttlid,
						TID = t.tid,
						TNAME = t.tname,
						TDESC = t.tdesc,
						TDTDUE = t.tdtdue,
						TCOMPL = t.tcompleted,
						TDTCOMPL = t.tdtcompleted,
						TPRI = t.tpri,
						form_title = 'Update task',
						TLISTS = list_of_tlists
					)	

	elif request.method == 'POST':

		form_get_referrer = session.get('form_get_referrer', url_for('tasksall'))

		if task_id is None:	
			# CREATE 2, POST
			
			f_dtdue = request.form.get("tdatedue")
			if f_dtdue == '': 
				f_dtdue = None

			f_dtcompleted = request.form.get("tdatecompleted")
			if f_dtcompleted == '': 
				f_dtcompleted = None
			
			if tlist_id == 0:  # new task, from alt view ~ no task list id in url
				tlist_id = request.form.get("tlid")

			new_task = md.create_task(
				tlid=tlist_id,
				name=request.form.get("tname", ""),
				desc=request.form.get("tdesc", ""),
				dtdue=f_dtdue,
				completed=request.form.get("tcompleted", False),
				dtcompleted=f_dtcompleted,
				pri=request.form.get("tpri", 0)
			)
			# print('>>>>>>>new_task', new_task)
			if new_task == md.TASK_EMPTY :  
				flash('Task was not created')
			# return redirect(url_for('tasks', tlist_id=tlist_id))
			return redirect(form_get_referrer)

		else:
			# UPD 2, POST	

			# read values from db fields
			t = md.read_task(tid=task_id)

			# set updated field values according to form field values
			tid = task_id

			f_ttlid = request.form.get("tlid")
			ttlid = tlist_id
			if f_ttlid is not None:
				if f_ttlid != tlist_id:
					ttlid = f_ttlid 

			f_tname = request.form.get("tname")
			tname =  f_tname if f_tname != t.tname else t.tname 

			f_tpri = request.form.get("tpri", 0)
			tpri = f_tpri if f_tpri != t.tpri else t.tpri
			
			f_tdesc = request.form.get("tdesc")
			tdesc = f_tdesc if f_tdesc != t.tdesc else t.tdesc
	
			f_dtdue = request.form.get("tdatedue")
			if f_dtdue == '': 
				f_dtdue = None 
			tdatedue = f_dtdue if f_dtdue != t.tdtdue else t.tdtdue
			
			f_completed = request.form.get("tcompleted", False)
			
			f_dtcompleted = request.form.get("tdatecompleted")
			if f_dtcompleted == '': 
				f_dtcompleted = None 
			
			if f_completed and f_dtcompleted:
				tcompleted = f_completed
				tdatecompleted = f_dtcompleted
			elif not f_completed and not f_dtcompleted:
				tcompleted = False
				tdatecompleted = None
			elif f_completed and not f_dtcompleted:
				tcompleted = f_completed
				# tdatecompleted = dt.date.today()
				tdatecompleted = None
			else :  #  not f_completed and f_dtdue
				tcompleted = True
				tdatecompleted = f_dtcompleted

			upd_task = md.update_task(
				tid=tid,
				tlid=ttlid, 
				name=tname, 
				desc=tdesc, 
				dtdue=tdatedue, 
				completed=tcompleted, 
				dtcompleted=tdatecompleted,
				pri=tpri
			)

			if upd_task == md.TASK_EMPTY :  
				flash('Task was not updated')
			# return redirect(url_for('tasks', tlist_id=tlist_id))
			return redirect(form_get_referrer)
			
	else:   # no pass here anyway
		abort(400)


@app.route('/tlist/<int:tlist_id>/task/<int:task_id>/delete', methods=['GET']) # DEL task
def task_delete(tlist_id=None, task_id=None):
	if not g.user:
		return redirect(url_for('login'))

	rows_deleted = md.delete_task(tid=task_id)
	if rows_deleted == 0 : 
		flash('Task was not deleted')
	# return redirect(url_for('tasks', tlist_id=tlist_id))
	return redirect(request.referrer)


if __name__ == '__main__':

	md.conn_db()

	print(f'[before_app.run] ...') 

	app.run(host='localhost', port=5001, debug=True)  # host='0.0.0.0' or host='localhost'  

	print(f'[after_app.run] ...') 

	md.close_db()

	print(f'[after_close_db] ...') 