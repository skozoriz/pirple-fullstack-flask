import psycopg2 as pg

CONNECT_STRING = "host=localhost dbname=pf user=pf password=pf"

# Connect to postgres DB
CONN = pg.connect(CONNECT_STRING)  # GLOBALLY AVAILABLE   

# _CONN.autocommit = 'True' 