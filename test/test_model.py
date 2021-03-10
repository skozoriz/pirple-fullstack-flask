import sys 
print(sys.path)

from pf.db import CONN as _CONN 
from pf import model as md   # The code to test

import datetime as dt
import hashlib

import pytest

print('---from pytest---')

new_user = "new_test_user@n.t.u"
new_user_pw = "ntu"
hash_new_user_pw = hashlib.md5(new_user_pw.encode()).hexdigest()

today_dt = dt.date.today()

test_user = "test_user@t.u"
test_user_pw = "tu"
hash_test_user_pw = hashlib.md5(test_user_pw.encode()).hexdigest()

_test_uid = None

_new_tlid1 = None
_new_tlid2 = None
_new_tid1_1 = None
_new_tid1_2 = None


@pytest.fixture(scope='module', autouse=True)
def setup_db():
    print('[test_model] setup module start')    
    global _test_uid, _new_tlid1, _new_tlid2, _new_tid1_1, _new_tid1_2    
    print('\n', f'<<< test_user:{test_user} test_uid:{_test_uid} new_user:{new_user}')
    
    print(f'conn:{_CONN}')
    # md.conn_db()  # used but not tested
    # print(f'conn: {md._CONN}')
    # add test user
    with _CONN:
        with _CONN.cursor() as cur:
            try:
                print(f'cur: {cur}')
                sql = f"""INSERT INTO appuser (uname, udtcreated, udtout, upasswd)
                    VALUES ('{test_user}', '2020-01-01', '2021-01-01', '{hash_test_user_pw}')
                    RETURNING uid;"""
                print(f'SQL : {sql}')
                cur.execute(sql)
                test_uid = cur.fetchone()[0]
                print(test_uid)

                cur.execute(f"""
                    INSERT INTO tlist (tluid, tlname, tldtcreated, tlactive, tlpri)
                    VALUES ('{test_uid}', 'Список 1', CURRENT_DATE, TRUE, 0)
                    RETURNING tlid;""" 
                )
                new_tlid1 = cur.fetchone()[0]
                print(new_tlid1)

                cur.execute(f"""
                    INSERT INTO tlist (tluid, tlname, tldtcreated, tlactive, tlpri)
                    VALUES ('{test_uid}', 'List 2', CURRENT_DATE, TRUE, 127) 
                    RETURNING tlid;""" 
                )
                new_tlid2 = cur.fetchone()[0]
                print(new_tlid2)

                sql = f"""
                    INSERT INTO task (ttlid, tdesc, tname, tdtdue, tpri, tcompleted)
                    VALUES ('{new_tlid1}', 'task for <{test_user}, {new_tlid1}>', 'test task 1', '2021-12-01', 0, TRUE) 
                    RETURNING tid;"""
                print(f'SQL: {sql}')
                cur.execute(sql)             
                new_tid1_1 = cur.fetchone()[0]
                print(new_tid1_1)

                cur.execute(f"""
                    INSERT INTO task (ttlid, tdesc, tname, tdtdue, tpri, tcompleted)
                    VALUES ('{new_tlid1}', 'task for <{test_user}, {new_tlid1}>', 'test task 2', '2021-02-01', -22, FALSE) 
                    RETURNING tid;"""
                )
                new_tid1_2 = cur.fetchone()[0]
                print(new_tid1_2)

            except Exception as e:
                print('setup EXCEPTION!!', e)

    print(f'test_user:{test_user} test_uid:{test_uid} new_user:{new_user} ')  
    print(f'test ids::  test_uid:{test_uid}, new_tlid:{new_tlid1}, new_tid: {new_tid1_1}  >>>')
    _test_uid = test_uid
    _new_tlid1 = new_tlid1
    _new_tlid2 = new_tlid2
    _new_tid1_1 = new_tid1_1
    _new_tid1_2 = new_tid1_2

    yield

    print('\n[test_model] setup module after yield')

    with _CONN:
        with _CONN.cursor() as cur:
            print('teardown...')
            try:

                sql = f"""DELETE  FROM task
                          WHERE ttlid in ({_new_tlid1}, {_new_tlid2});"""
                # WHERE tid IN ({_new_tid1_1}, {_new_tid1_2}, {_task_id})
                print(f'SQL: {sql}')
                cur.execute(sql)
                
                cur.execute(f"""
                    DELETE  FROM tlist
                    WHERE tlid IN ({_new_tlid1}, {_new_tlid2});
                    """
                )
                
                cur.execute(f"""
                    DELETE  FROM appuser
                    WHERE uname='{test_user}';
                    """
                )

            except Exception as e:
                print('teardown EXCEPTION!!', e)

    print('[test_model] after yield finished')
    md.close_db()   # used but not tested


def test_appusers():
    rr = md.read_users()
    print(type(rr))
    for r in rr:
        print(r)
    assert test_user in [r[1] for r in rr]

def test_read_user():
    u = md.read_user(test_user)  # with test_user
    assert (
        (u.uid is not None) 
        and (u.uname == test_user) 
        and (u.udtcreated == dt.date(2020, 1, 1))
        and (u.udtout == dt.date(2021, 1, 1))
        and (u.upasswd == hash_test_user_pw)  
    )

def test_create_user():
    u = md.create_user(uname=new_user, pw=hash_new_user_pw)
    assert (
        (u.uid is not None) 
        and (u.uname == new_user) 
        and (u.udtcreated == today_dt)  # must be today
        and (u.udtout is None)
        and (u.upasswd == hash_new_user_pw)
    )

def test_update_user():
    due_date = dt.date(2021, 1, 20)
    upw = 'ntu_upd_pw'
    hash_upw = hashlib.md5(upw.encode()).hexdigest()
    u = md.update_user(uname=new_user, pw=hash_upw, udtout=due_date)
    assert (
        (u.uid is not None) 
        and (u.uname == new_user) 
        and (u.udtcreated == today_dt)  # must be today
        and (u.udtout == due_date)
        and (u.upasswd == hash_upw)
    )

def test_delete_user():
    rows_deleted = md.delete_user(uname=new_user)
    # print(f'rows_deleted:{rows_deleted}')
    u = md.read_user(new_user)
    # print(uinfo)
    assert u.uid == None and rows_deleted == 1

def test_read_tlists_empty():
    l = md.read_tlists(uname='sergii.kozoriezov')
    assert len(l) == 0

def test_read_tlists_test_user():
    l = md.read_tlists(uname=test_user)
    # print(l)
    assert(
        len(l) == 2 
        and l[0].tluname == test_user
        and l[0].tltcount == 0  # task count for tlist 1
        and l[0].tlpri == 127  # pri for tlist1
        and l[1].tltcount == 2  # task count for tlist 2
        and l[1].tlpri == 0  # pri for tlist2
    )

def test_read_tlist_empty():
    tlist = md.read_tlist(99999)
    assert tlist == md.TLIST_EMPTY

def test_read_tlist_testu_testtl():
    tl = md.read_tlist(_new_tlid1)
    assert (
        tl.tluid == _test_uid 
        and tl.tlid == _new_tlid1
        and tl.tlname == 'Список 1'
        and tl.tldtcreated == today_dt
        and tl.tlactive == True
        and tl.tlpri == 0
        and tl.tltcount == 2 # task count
    )

def test_create_tlist_empty():
    nouser = 'no_such_user'
    tlname =  f'new_tlist for {nouser}'
    tl = md.create_tlist(nouser, tlname)
    assert tl == md.TLIST_EMPTY

_tl_id = None

def test_create_tlist():
    global _tl_id
    name =  f'new_tlist for {test_user}'
    tl = md.create_tlist(test_user, tlname=name)
    _tl_id = tl.tlid
    assert (
        tl.tluid == _test_uid
        and tl.tlid is not None
        and tl.tlname == name[:30]
        and tl.tldtcreated == today_dt
        and tl.tlactive == True
        and tl.tlpri == 0
        and tl.tltcount == 0
    )

def test_update_tlist():
    utlname =  f'updated new_tlist for {test_user}'
    tlactive = False
    tlpri = -100
    tl = md.update_tlist(_tl_id, tlname=utlname, tlactive=tlactive, tlpri=tlpri)
    assert (
        tl.tluid == _test_uid
        and tl.tlid == _tl_id
        and tl.tlname == utlname[:30]
        and tl.tldtcreated == today_dt
        and tl.tlactive == tlactive
        and tl.tlpri == tlpri
        and tl.tltcount == 0
    )

def test_delete_tlist():
    deleted = md.delete_tlist(_tl_id)
    assert deleted == 1

def test_read_tasks():
    ts = md.read_tasks(_new_tlid1)
    assert (
        len(ts) == 2
        and ts[0].tid == _new_tid1_1
        and ts[0].ttlid == _new_tlid1
        and ts[0].tname == 'test task 1'
        and ts[0].tdesc == f'task for <{test_user}, {_new_tlid1}>'
        and ts[0].tdtdue == dt.date(2021, 12, 1)
        and ts[0].tcompleted == True
        and ts[0].tpri == 0
    )

def test_read_tasks_empty():
    tasks = md.read_tasks(99999)
    assert tasks == ()

def test_read_task_empty():
    tid = 7777
    task = md.read_task(tid)
    assert task == md.TASK_EMPTY

def test_read_task():
    tid = _new_tid1_1
    t = md.read_task(tid)    
    assert (
        t is not md.TASK_EMPTY 
        and t.tid == tid
        and t.ttlid == _new_tlid1
        and t.tname == 'test task 1'
        and t.tdesc == f'task for <{test_user}, {_new_tlid1}>'
        and t.tdtdue == dt.date(2021, 12, 1)
        and t.tcompleted == True
        and t.tdtcompleted == None
        and t.tpri == 0
    )

_task_id = None

def test_create_task():
    global _task_id
    t_tlid = _new_tlid2
    t_name='test task created by pytest'
    t_desc='something about ...'
    t_dtdue=dt.date(2222, 2, 2)
    t_completed=False
    t_dtcompleted=None
    t_pri = 0    
    t = md.create_task(
        tlid=t_tlid, 
        name=t_name,
        desc=t_desc,
        dtdue=t_dtdue,
        completed=t_completed,
        dtcompleted=t_dtcompleted,
        pri=t_pri
        )
    assert(
        t is not md.TASK_EMPTY 
        # and task[0] == _new_tid1_1
        and t[1] == t_tlid
        and t.tname == t_name[:30]
        and t.tdesc == t_desc[:60]
        and t.tdtdue == t_dtdue
        and t.tcompleted == t_completed 
        and t.tdtcompleted == t_dtcompleted 
        and t.tpri == t_pri
    )
    _task_id = t.tid
    # print(f'[create_task] _task_id: {_task_id}')

def test_update_task():
    t_tid = _new_tid1_2 if _task_id is None else _task_id
    t = md.read_task(t_tid) 
    t_tlid = t.ttlid
    t_name = '!!' + t.tname + '!!'
    t_desc = '!!' + t.tdesc + '!!'
    t_dtdue = t.tdtdue
    t_completed = not t.tcompleted
    t_dtcompleted = t.tdtcompleted
    t_pri = t.tpri - 100
    tu = md.update_task(
        tid=t_tid,
        tlid=t_tlid, 
        name=t_name,
        desc=t_desc,
        dtdue=t_dtdue,
        completed=t_completed,
        dtcompleted=t_dtcompleted,
        pri=t_pri
        )
    assert(
        tu is not md.TASK_EMPTY 
        and tu.tid == t_tid
        and tu.ttlid == t_tlid
        and tu.tname == t_name[:30]
        and tu.tdesc == t_desc[:60]
        and tu.tdtdue == t_dtdue
        and tu.tcompleted == t_completed
        and tu.tdtcompleted == t_dtcompleted 
        and tu.tpri == t_pri
    )

def test_delete_task():
    tid = _new_tid1_2 if _task_id is None else _task_id
    rows_deleted = md.delete_task(tid)
    assert rows_deleted == 1    

def test_delete_task_zero():
    tid = 999999
    rows_deleted = md.delete_task(tid)
    assert rows_deleted == 0   

@pytest.mark.skip()
def test_create_task_dtdue_emptystr():
    global _task_id
    t_tlid = _new_tlid2
    t_name='test task with tduedate None/NULL'
    t_desc='something about ...'
    t_dtdue=''  # should be date or None, not empty string
    t_completed=False
    t_dtcompleted=None    
    task = md.create_task(
        tlid=t_tlid, 
        name=t_name,
        desc=t_desc,
        dtdue=t_dtdue,
        completed=t_completed,
        dtcompleted=t_dtcompleted
        )
    assert(
        task is not md.TASK_EMPTY 
        # and task[0] == _new_tid1_1
        and task.ttlid == t_tlid
        and task.tname == t_name[:30]
        and task.tdesc == t_desc[:60]
        and task.tdtdue == t_dtdue
        and task.tcompleted == t_completed 
        and task.tdtcompleted == t_dtcompleted 
    )
    _task_id = task.tid

