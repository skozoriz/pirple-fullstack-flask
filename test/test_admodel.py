import sys 
print('---test_admodel/1---', sys.path)

from pf.adminapp import adminapp_model as mda   # The code to test
from pf.db import CONN as _CONN

import datetime as dt
# import hashlib

import pytest

def exec_sql_one(sql):
    cur = _CONN.cursor()
    try:
        cur.execute(sql)
        one_res = cur.fetchone()[0]
    except:
        one_res = None
    cur.close()
    _CONN.commit
    return one_res

def exec_sql_many(sql):
    cur = _CONN.cursor()
    try:
        cur.execute(sql)
        many_res = cur.fetchall()
    except:
        many_res = None
    cur.close()
    _CONN.commit
    return many_res

print('---test_admodel/2---')

auname = 'pfadmin'

@pytest.fixture(scope='module', autouse=True)
def setup_db():
    print('---test_admodel/setup_db/init---')
    yield
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
    u_count_db = exec_sql_one(sql)
    u_count_mda = mda.count_user("all")
    assert u_count_db == u_count_mda

def test_count_user_24h():
    sql = "SELECT * from appuser;"
    users = exec_sql_many(sql)
    c_db = len([u for u in users if u[2]>dt.datetime.now()-dt.timedelta(hours=24)])
    c_mda = mda.count_user("24h")
    assert c_db == c_mda

def test_count_tl_all():
    sql = "SELECT count(*) from tlist;"
    tl_count_db = exec_sql_one(sql)
    tl_count_mda = mda.count_tlist("all")
    assert tl_count_db == tl_count_mda

def test_count_tl_24h():    
    sql = "SELECT * from tlist;"
    tlists = exec_sql_many(sql)
    c_db = len([tl for tl in tlists if tl[3]>dt.datetime.now()-dt.timedelta(hours=24)])
    c_mda = mda.count_user("24h")
    assert c_db == c_mda

def test_readuserspg_first():
    pass

def test_read_userspg_last():
    pass

def test_read_userspg_middle():
    pass


