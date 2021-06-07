Pirple Full Stack Web Development with Flask 

1. Application folder structure:

adminapp/               adminapp blueprint
    __init__.py
    adminapp.py
    adminapp_model.py
    templates/
        adminapp/
            *.html
dbdump/                 dump-files of DB (examples), cron row, delete old backups shell script
etc/                    some config files for uwsgi and nginx services
test/
    __init__.py
    test_admodel.py
    test_model.py
static/
templates/
    *.html

__init__.py             task list application
config.py
db.py                   db connection (postgresql 12)
model.py                db operations on data
pf.ini                  uwsgi config file
pf.py                   routes, views
requirements.txt        dependecies
README.md               this file

pf_DDL*.txt DDL operators for postgresql (12.5) - to create DB schema


2. How to start app:

    >cd <app folder>

--Directly (host and port hard coded in app code, see if __name__ == __main__ part):

    >python pf.py

--Under uwsgi, config file pf.ini is used, only 1 worker (?more workers are not working with current db conection template?):

    >uwsgi --socket 0.0.0.0:5000 --protocol=http -w pf:app

--Via Flask run (it's not working in current version):

    >export FLASK_APP=pf
    >export FLASK_DEBUG=1

    >flask run


3. Tests / pytest

For data base operations only (for models).

    >pytest test/test_admodel.py -l -v
    >pytest test/test_model.py -l -v

Test data for pytest scrips are prepared by test script itself.

Test data for manual testing (as sql script) - to be prepared.

4. DB 

Posgresql 12.5

No SQLAlchemie, communication through pg2 python lib/driver.

DDL operations to create db schema: pf_DDL_*.txt.
Can be ran through psql.

Connect string - see DB.py


5. Other technologies

For application frontend Twitter Bootstrap 5 is utilized.

For admin blueprint frontend Materialized CSS 1.0 is utilized.





