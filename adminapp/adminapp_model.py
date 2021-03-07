from pf.db import CONN as _CONN 
 
from pf.model import User, USER_EMPTY    

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

# count users registered 
def count_user(case='all'):
    if case not in ('all', '24h'): 
        return None
    sql = "SELECT count(*) FROM appuser "
    sql2 = "WHERE udtcreated>(CURRENT_TIMESTAMP - interval '24h')" if case == '24h' else ""
    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute(sql+sql2+";",())
            res = cur.fetchone()[0]
    return res 

# count tlists registered 
def count_tlist(case='all'):
    if case not in ('all', '24h'): 
        return None
    sql = "SELECT count(*) FROM tlist "
    sql2 = "WHERE tldtcreated>(CURRENT_TIMESTAMP - interval '24h')" if case == '24h' else ""
    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute(sql+sql2+";",())            
            res = cur.fetchone()[0]
    return res 
