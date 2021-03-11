import sys 
print('---test_admodel/1---', sys.path)

from pf.adminapp import adminapp_model as mda   # The code to test
from pf.db import CONN as _CONN

import datetime as dt
# import hashlib

import pytest

def exec_sql_oneres(sql):
    cur = _CONN.cursor()
    try:
        cur.execute(sql)
        one_res = cur.fetchone()[0]
    except:
        one_res = None
    _CONN.commit()
    cur.close()
    return one_res

def exec_sql_manyres(sql):
    cur = _CONN.cursor()
    try:
        cur.execute(sql)
        many_res = cur.fetchall()
    except:
        many_res = None
    _CONN.commit()
    cur.close()
    return many_res

def prepare_test_data(nuser=2, nint=1):
    # !!! nint > 0
    lint = nuser // nint
    print("<<=====SQL======")
    for i in range(nuser):
        # (uid) uname, udtcreated::timestamp, upasswd, udtout::date
        # test-user<n>, now()..now()-days(nuser-1), 'passwd', NULL
        sql1 = f"""INSERT INTO appuser (uname, udtcreated, upasswd)
                  VALUES ('test-user@{str(i)}', '{dt.datetime.now()-dt.timedelta(days=nuser-i)}', 'passwd{str(i)}')
                  RETURNING uid, udtcreated; """ 
        print(sql1)
        uid, udtcreated = exec_sql_manyres(sql1)[0]
        print(f'returning: uid={uid}, udtctreated={udtcreated}')
        if i==0 or nuser % lint == 0 :
            for j in range(4):
                # tluid, (tlid) tlname, tldtcreated::timestamp, tlactive, tlpri, tlcolor
                #               tl-test-<uid,j>, udtcreated, True, j*5, 'white' 
                sql2 = f"""INSERT INTO tlist (tluid, tlname, tldtcreated, tlactive, tlpri, tlcolor)
                    VALUES ({uid}, 'tl-test-<{str(uid)},{str(j)}>', '{udtcreated}', TRUE, {j*5}, 'white')
                    RETURNING tlid; """
                print(sql2)
                tlid = exec_sql_oneres(sql2)
                print(f'returning: tlid={tlid}')
                for k in range(4):
                    # (tid) ttlid, tname, tdesc, tdtdue::date, tcompleted, tdtcompleted::date, tpri
                    #       tlid, task-test-<uid,tlid,k>, desc-<uid,tlid,k>, NULL, False, NULL, -5*k
                    sql3 = f"""INSERT INTO task (ttlid, tname, tdesc, tdtdue, tcompleted, tdtcompleted, tpri)
                        VALUES ({tlid}, 'task-test-<{uid},{tlid},{k}>', 'desc-<{uid},{tlid},{k}>', NULL, false, NULL, {-5*k})
                        RETURNING tid; """
                    print(sql3)
                    tid = exec_sql_oneres(sql3)
                    print(f'returning: tid={tid}')
    print("=====SQL======>>")


def delete_test_data():

    print()
    print("<<=====SQL======")

    sql1 = "DELETE FROM task WHERE tname LIKE 'task-test-%%' RETURNING *;"
    n = len(exec_sql_manyres(sql1))
    print(f'--deleted--{n}--tasks')

    sql1 = "DELETE FROM tlist WHERE tlname LIKE 'tl-test-%%' RETURNING *;"
    n = len(exec_sql_manyres(sql1))
    print(f'--deleted--{n}--tlists')

    sql1 = "DELETE FROM appuser WHERE uname LIKE 'test-user%%' RETURNING *;"
    n = len(exec_sql_manyres(sql1))
    print(f'--deleted--{n}--users')

    _CONN.commit()
    print("=====SQL======>>")


print('---test_admodel/2---')

auname = 'pfadmin'

@pytest.fixture(scope='module', autouse=True)
def setup_db():
    print('---test_admodel/setup_db/init---')
    prepare_test_data(nuser=100, nint=5)
    yield
    delete_test_data()
    print('---test_admodel/setup_db/close---')

def test_read_adminuser_emp():
    au = mda.read_adminuser()  
    assert au == mda.USER_EMPTY

def test_read_adminuser_notau():
    au = mda.read_adminuser("auname@c.com")  
    assert au == mda.USER_EMPTY

def test_read_adminuser():
    au = mda.read_adminuser(auname)  
    assert (
        au.uid is not None
        and au.uname == auname
    )

def test_count_user_all():
    sql = "SELECT count(*) from appuser;"
    u_count_db = exec_sql_oneres(sql)
    u_count_mda = mda.count_user("all")
    assert u_count_db == u_count_mda

def test_count_user_24h():
    sql = "SELECT * from appuser;"
    users = exec_sql_manyres(sql)
    c_db = len([u for u in users if u[2]>dt.datetime.now()-dt.timedelta(hours=24)])
    c_mda = mda.count_user("24h")
    assert c_db == c_mda

def test_count_tl_all():
    sql = "SELECT count(*) from tlist;"
    tl_count_db = exec_sql_oneres(sql)
    tl_count_mda = mda.count_tlist("all")
    assert tl_count_db == tl_count_mda

def test_count_tl_24h():    
    sql = "SELECT * from tlist;"
    tlists = exec_sql_manyres(sql)
    c_db = len([tl for tl in tlists if tl[3]>dt.datetime.now()-dt.timedelta(hours=24)])
    c_mda = mda.count_user("24h")
    assert c_db == c_mda

def test_readuserspg_first():
    pass

def test_read_userspg_last():
    pass

def test_read_userspg_middle():
    pass


