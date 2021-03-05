# data model for my pf pirple project
from collections import namedtuple
import sys 
import psycopg2 as pg

_CONNECT_STRING = "host=localhost dbname=pf user=pf password=pf"
_CONN = None



def conn_db(cs=_CONNECT_STRING):
    # Connect to postgres DB
    global _CONN
    _CONN = pg.connect(cs)  # GLOBALLY AVAILABLE   
    # _CONN.autocommit = 'True' 
    # Open a cursor to perform database operations
    cur = _CONN.cursor()
    _print_dbcount(cur, "appuser")
    _print_dbcount(cur, "tlist")
    _print_dbcount(cur, "task")
    _CONN.commit()
    cur.close()

def close_db():
    _CONN.commit()
    _CONN.close()

# module internal funcs
def _print_dbcount(cur, tablename):
	# Execute a query
    cur.execute(f"SELECT count(*) FROM {tablename};")  # 'bed practice" for table name inclusion
	# Retrieve query results
    count = cur.fetchone()
    print(f"table: {tablename} count: {count[0]}")

def print_namedtuplelist(nt_class, nt_list, prefixstr='--->'):
    print(nt_class._fields)
    for nt in nt_list:
        print(prefixstr, '|'.join( map(lambda x: str(x), nt)) )


# USER entity

User = namedtuple(
    "User", 
    "uid uname udtcreated udtout upasswd",
    defaults = [None, None, None, None, None]
)
USER_EMPTY = User()

# special case - read adminuser

def read_adminuser(auname=None): 
    if auname is None: 
        return USER_EMPTY
    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute("""
                SELECT auid, auname, audtcreated, Null as audtout, aupasswd 
                FROM admuser
                WHERE auname=%s; """,
                (auname,)
            )
            if (res := (cur.fetchone())):
                auinfo = User(*res)
            else:
                auinfo = USER_EMPTY
    return auinfo 

def read_users():
    cur = _CONN.cursor()
    cur.execute("SELECT uid, uname, udtcreated, udtout, upasswd FROM appuser;")
    if (ds := cur.fetchall()) :
        users = tuple( map(User._make, ds) )
    else:
        users = ()
    _CONN.commit()
    cur.close()
    return users

def create_user(uname=None, pw=None):

    with _CONN:
        with _CONN.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO appuser (uname, udtcreated, upasswd)
                    VALUES (%s, CURRENT_DATE, %s); """,
                    (uname[:30], pw[:32])     
                )
            except:
                return USER_EMPTY
    return read_user(uname)

def read_user(uname=None): 
    if uname is None: 
        return USER_EMPTY
    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute("""
                SELECT uid, uname, udtcreated, udtout, upasswd 
                FROM appuser
                WHERE uname=%s; """,
                (uname,)
            )
            if (res := (cur.fetchone())):
                uinfo = User(*res)
            else:
                uinfo = USER_EMPTY
    return uinfo 

def update_user(uname=None, udtout=None, pw=None):  # not realized in this version
    if uname is None: 
        return USER_EMPTY
    with _CONN:
        with _CONN.cursor() as cur:
            try:
                cur.execute("""
                    UPDATE appuser
                    SET udtout=%s, upasswd=%s 
                    WHERE uname=%s
                    RETURNING  uid, uname, udtcreated, udtout, upasswd; """,
                    (udtout, pw[:32], uname)
                )
                if (res := cur.fetchone()):
                    uinfo = User(*res)
                else:        
                    uinfo = USER_EMPTY
            except:
                return USER_EMPTY
    return uinfo

def delete_user(uname=None, delete_alldata=False):  

    if uname is None: 
        return 0

    uid = read_user(uname)[0]
    if uid is None: 
        return 0

    with _CONN:
        with _CONN.cursor() as cur:

            if delete_alldata:
                # // try needed///
                #delete all user tasks from table Task
                cur.execute("""
                    DELETE  FROM task
                    WHERE ttlid IN (
                        SELECT DISTINCT tlid 
                        FROM tlist
                        WHERE tluid=%s) """,
                    (uid,) 
                )    
                #delete all user task lists from table Tlist
                cur.execute("""
                    DELETE  FROM tlist
                    WHERE tluid=%s; """,
                    (uid,) 
                )   
              
            #delete user from table User   
            try:
                cur.execute("""
                    DELETE  FROM appuser
                    WHERE uid=%s 
                    RETURNING *; """,
                    (uid,) 
                )
                urows_deleted = len(cur.fetchall())
            except:
                urows_deleted = 0

    return urows_deleted


# TLIST entity

Tlist = namedtuple(
    "Tlist", 
    "tluid tlid tlname tldtcreated tlactive tlpri tlcolor tltcount",
    defaults = [None, None, None, None, None, None, None, None]
)
Tlist_ext = namedtuple(
    "Tlist_ext",
    ("tluname",) + Tlist._fields
)
TLIST_EMPTY = Tlist()

# leave as is or convert to use Tlist/Tlist_ext ?
# uname is additional attribute to Tlist: < uname, *(TList) >
def read_tlists(uname=None):
    if uname is None: 
        return ()

    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute("""
                SELECT 
                    u.uname, tluid, tlid, tlname, tldtcreated, tlactive, tlpri, tlcolor,
                    (SELECT count(*) FROM task where task.ttlid=tlid) as tltcount  
                FROM tlist tls, appuser u
                WHERE tls.tluid=u.uid
                    and u.uname=%s
                ORDER BY tlpri DESC, tlname ASC; """,   # ?? %s or '%s' ??
                (uname,)     
            )
            ds = cur.fetchall()
            if ds:
                tls = tuple( map(Tlist_ext._make, ds) )
            else:
                tls = ()

    return tls 


def create_tlist(uname=None, tlname=None, tlpri=0, tlcolor='white'): 
# to be added:  tlactive to parameter list
    if uname is None:
        return TLIST_EMPTY
    uid = read_user(uname).uid
    if uid is None:
        return TLIST_EMPTY
    with _CONN:
        with _CONN.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO tlist (tluid, tlname, tldtcreated, tlactive, tlpri, tlcolor)
                    VALUES (%s, %s, CURRENT_DATE, TRUE, %s, %s)
                    RETURNING tluid, tlid, tlname, tldtcreated, tlactive, tlpri, tlcolor, 0; """,
                    (uid, tlname[:30], tlpri, tlcolor)
                )
                tl = cur.fetchone()
                tl = Tlist(*tl)
            except:
                tl = TLIST_EMPTY
    return tl 

def read_tlist(tlid=None):

    if tlid is None: 
        return TLIST_EMPTY

    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute("""
                SELECT 
                    tluid, tlid, tlname, tldtcreated, tlactive, tlpri, tlcolor,
                    (SELECT count(*) FROM task where task.ttlid=tlid) as tltcount  
                FROM tlist
                WHERE tlid=%s""",
                (tlid,)
            )
            ds = cur.fetchone()
            if ds:
                tlinfo = Tlist(*ds)
            else:
                tlinfo = TLIST_EMPTY

    return tlinfo 

def update_tlist(tlid=None, tlname=None, tlactive=None, tlpri=None, tlcolor=None):
    
    if tlid is None: 
        return TLIST_EMPTY

    with _CONN:
        with _CONN.cursor() as cur:
            try:
                cur.execute("""
                    UPDATE tlist
                    SET tlname=%s, tlactive=%s, tlpri=%s, tlcolor=%s
                    WHERE tlid=%s
                    RETURNING  tluid, tlid, tlname, tldtcreated, tlactive, tlpri, tlcolor,
                            (SELECT COUNT(*) FROM task WHERE ttlid=tlid) AS tcnt; """,
                    (tlname[:30], tlactive, tlpri, tlcolor, tlid)
                )
                ds = cur.fetchone()
                tlinfo = Tlist(*ds)
            except:
                tlinfo = TLIST_EMPTY

    return tlinfo

def delete_tlist(tlid=None, delete_alldata=False):
    with _CONN:
        with _CONN.cursor() as cur:
            if delete_alldata:
                # delete tasks for task list given
                try:
                    cur.execute("""
                        DELETE  FROM task
                        WHERE ttlid=%s; """,
                        (tlid,) 
                    )
                except:
                    pass
            # delete task list given
            try:
                cur.execute("""
                    DELETE  FROM tlist
                    WHERE tlid=%s
                    RETURNING *; """,
                    (tlid,) 
                )
                rows_deleted = len(cur.fetchall())
            except:
                rows_deleted = 0

    return rows_deleted


# TASK entity

Task = namedtuple(
    "Task", 
    "tid ttlid tname tdesc tdtdue tcompleted tdtcompleted tpri",
    defaults = [None, None, None, None, None, None, None, None] 
)
Task_ext = namedtuple(
    "Task_ext",
    ("ttlname", "ttlpri", "ttlactive", "ttlcolor") + Task._fields
)
TASK_EMPTY = Task()


def read_tasks(tlid=None):
    if tlid is None: 
        return ()

    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute("""
                SELECT tid, ttlid, tname, tdesc, tdtdue, tcompleted, tdtcompleted, tpri
                FROM task
                WHERE ttlid=%s
                ORDER BY tpri DESC, tname ASC; """, 
                (tlid,)     
            )
            ds = cur.fetchall()
            if ds:
                tasks = tuple( map(Task._make, ds) )
            else:
                tasks = ()

    return tasks 

def read_tasksall(uid=None):
    if uid is None: 
        return ()

    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute("""
                SELECT 
                    tl.tlname, tl.tlpri, tl.tlactive, tl.tlcolor,
                    t.tid, t.ttlid, t.tname, t.tdesc, t.tdtdue, t.tcompleted, t.tdtcompleted, t.tpri
                FROM tlist tl, task t
                WHERE tl.tlid=t.ttlid
                  and tl.tluid=%s
                ORDER BY tpri DESC, tname ASC; """, 
                (uid,)     
            )
            ds = cur.fetchall()
            if ds:
                tasksall = tuple( map(Task_ext._make, ds) )
            else:
                tasksall = ()

    return tasksall 

#
def create_task(tlid=None, name=None, desc=None, dtdue=None, completed=False, dtcompleted=None, pri=0):
    if tlid is None:
        return TASK_EMPTY
    # print(f'-=-=[create_task] tlid:{tlid}, name:{name}, desc:{desc}, dtdue:{dtdue}, completed:{completed}, dtcompleted:{dtcompleted}, pri:{pri}')
    with _CONN:
        with _CONN.cursor() as cur:
            try:
                sql = """INSERT INTO task (ttlid, tname, tdesc, tdtdue, tcompleted, tdtcompleted, tpri)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING tid, ttlid, tname, tdesc, tdtdue, tcompleted, tdtcompleted, tpri; """
                # sql_m = cur.mogrify(sql,
                #     (tlid, name[:30], desc[:60], dtdue, completed, dtcompleted, pri)
                # )
                # print('--==sql: ', sql_m) 
                cur.execute(sql,
                    (tlid, name[:30], desc[:60], dtdue, completed, dtcompleted, pri)
                )
                res = cur.fetchone()
                taskinfo = Task(*res)
            except:
                taskinfo = TASK_EMPTY
    return taskinfo

#
def read_task(tid=None):
    if tid is None: 
        return TASK_EMPTY
    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute("""
                SELECT tid, ttlid, tname, tdesc, tdtdue, tcompleted, tdtcompleted, tpri
                FROM task
                WHERE tid=%s; """, 
                (tid,)     
            )
            ds = cur.fetchone()
            if ds:
                taskinfo = Task(*ds)
            else:
                taskinfo = TASK_EMPTY
    return taskinfo

#
def update_task(tid=None, tlid=None, name=None, desc=None, dtdue=None, completed=False, dtcompleted=None, pri=None):

    print(f'-=-=[update_task] tid:{tid}, tlid:{tlid}, name:{name}, desc:{desc}, dtdue={dtdue}, completed:{completed}, dtcompleted:{dtcompleted}, pri:{pri}')

    if tid is None: 
        return TASK_EMPTY

    with _CONN:
        with _CONN.cursor() as cur:
            try:
                # sql = cur.mogrify("""
                #     UPDATE task
                #     SET ttlid=%s, tname=%s, tdesc=%s, tdtdue=%s, tcompleted=%s, tdtcompleted=%s, tpri=%s 
                #     WHERE tid=%s
                #     RETURNING tid, ttlid, tname, tdesc, tdtdue, tcompleted, tdtcompleted, tpri; """,
                #     (tlid, name[:30], desc[:60], dtdue, completed, dtcompleted, pri,
                #     tid)
                # )
                # print('--==sql: ', sql)
                cur.execute("""
                    UPDATE task
                    SET ttlid=%s, tname=%s, tdesc=%s, tdtdue=%s, tcompleted=%s, tdtcompleted=%s, tpri=%s 
                    WHERE tid=%s
                    RETURNING tid, ttlid, tname, tdesc, tdtdue, tcompleted, tdtcompleted, tpri; """,
                    (tlid, name[:30], desc[:60], dtdue, completed, dtcompleted, pri,
                    tid)
                )
                ds = cur.fetchone()
                taskinfo = Task(*ds)
            except:
                taskinfo = TASK_EMPTY

    return taskinfo

#
def delete_task(tid=None):
    if tid is None:
        return 0 
    with _CONN:
        with _CONN.cursor() as cur:
            try:
                cur.execute("""
                    DELETE  FROM task
                    WHERE tid=%s
                    RETURNING *; """,
                    (tid,) 
                )
                rows_deleted = len(cur.fetchall())
            except:
                rows_deleted = 0
    return rows_deleted


if __name__ == '__main__':

    print('model test started...')
    print(f'model.py started as {__name__}')
    
    conn_db()

    # # list all users
    # lr = read_users()
    # print(type(lr))
    # for r in lr:
    #     print(r)

    # create new user
    # new_uname = "pirple@pirple.comm"
    # create_user(uname=new_uname, pw="-1-2-3")
    # print("new user: ", read_user(uname=new_uname))

    # list all users
    # print(read_users())

    # delete last created user
    # delete_user(uname=new_uname)
    # print("new_user deleted: ", read_user(uname=new_uname))

    # list all users
    # print(read_users())

    close_db()    
    print('model test finished...')