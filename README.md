Pirple Full Stack Web Development with Flask 

1. Application folder structure:

adminapp/               adminapp blueprint
    __init__.py
    adminapp.py
    adminapp_model.py
    templates/
        adminapp/
            *.html
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
pf.py                   routes, views
requirements.txt        dependecies
README.md

pf_DDL*.txt DDL operators for postgresql (12.5) - to create DB schema


2. How to start app:

>cd <app folder>

>export FLASK_APP=pf
>export FLASK_DEBUG=1

>flask run

App cannot be ran by "python3 pf.py" command.


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

For application frontend Twitter Bootstrap 4 is utilized.

For admin blueprint frontend Materialized CSS is utilized.





