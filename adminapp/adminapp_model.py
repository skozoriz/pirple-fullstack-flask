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

# read users with offset and limit: pagination ready
def read_users_ol(offset=0, limit=20):
    off = 0 if offset is None or offset < 0 else offset
    lim = 0 if limit is None or limit < 0 else limit
    sql = """SELECT uid, uname, udtcreated::date, udtout, upasswd 
        FROM appuser ORDER BY udtcreated DESC
        OFFSET %s LIMIT %s ;"""
    print(f"--[read_users_ol] off:{off}, lim:{lim}, sql:'{sql}'")
    with _CONN:
        with _CONN.cursor() as cur:
            cur.execute(sql, (off, lim))            
            if (ds := cur.fetchall()) :
                users = tuple( map(User._make, ds) )
            else:
                users = ()
            print(f"--[read_users_ol] users:{users}")
    return users 

# read page of data from appuser
# pagenum = 1..pagesn
# pagelen > 0
def read_users_page(pagenum='1', pagelen=12):

    usersn = count_user(case='all')
    
    if pagelen == 0 :
        pagesn = 1
    else :
        pagesn = (usersn // pagelen) + 1 if (usersn % pagelen) > 0 else 0
    
    if pagenum == 'first':
        pg = 1
    elif pagenum == 'last':
        pg = pagesn
    else :
        pn = int(pagenum)
        pg = pagesn if pn > pagesn else pn
    
    return read_users_ol(offset=(pg-1)*pagelen, limit=pagelen)

