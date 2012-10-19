Below here are notes on installing phylografter on installing phylografter on Mac.

#ivy and dependencies
for module in matplotlib scipy numpy biopython pyparsing ipython lxml PIL ivy
do
    pip install --upgrade "$module" 
done






1. Install MySQL
I'm assuming below that it is installed in /usr/local/mysql 
I used MySQL-5.5.27

2. Configure SQL
Create an SQL user ( 'tester' in our example)
Assign the user a password ('abc123' in our example)
Create an SQL database called something ('phylografter' in our example)
Give the user privileges to modify the database

################################################################################
$ mysql -u root --password=<sqluserspassword>
mysql> CREATE USER 'tester'@'localhost' IDENTIFIED BY 'abc123' ;
mysql> CREATE database phylografter ;
mysql> GRANT ALL ON phylografter.* to 'tester'@'localhost' ;
################################################################################

3. Configure Phylografter
Set the phylografter/private/config to contain:
################################################################################
[db]
host = localhost
user = tester
password = abc123
dbname = phylografter
################################################################################

4. Install MySQLdb (
Downloadable from http://sourceforge.net/projects/mysql-python/ 
I used version 1.2.3
lxml
################################################################################
$ export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/usr/local/mysql/lib
$ cd <directory in which you've unpacked MySQLdb>
$ python setup.py install 
################################################################################

5. lxml
################################################################################
$ pip install lxml
################################################################################


[6. deprecated Tweak phylografter to use MySQLdb in the DAL.
In phylografter/models/dp.py before the line (32) which states:
################################################################################
db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=False ) 
################################################################################
insert the snippet:
################################################################################
if 'USE_MY_SQL_ADAPTOR' in os.environ:
    # see http://stackoverflow.com/questions/10055441/web2py-doesnt-connect-to-mysql
    import MySQLdb
    from gluon.dal import MySQLAdapter
    MySQLAdapter.driver = globals().get('MySQLdb',None)
]

################################################################################

6. Download and unpack the source code version of web2py

http://www.web2py.com/examples/default/download
I used Version 1.99.7

7. Register phylografter as a web2py app by creating a symbolic link
################################################################################
$ cd web2py/appications
$ ln -s /full/path/to/phylografterv2 .
################################################################################


8. Bootstrap the DB tables for phylografter
Set the parameter migrate to True ( by modifying or adding to the call so that 
it includes ", migrate=True" in the DAL code in phylografter/models/db.py 
specific fragments to be modified are the creation of the DAL and define_tables
calls:
################################################################################
db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=False ) 
...
auth.define_tables( migrate=False )                           # creates all needed tables
...
define_tables(db)
################################################################################

9. Launch web2py
You'll be prompted to enter a password for the web2py admin account.
################################################################################
$ export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/usr/local/mysql/lib
$ export USE_MY_SQL_ADAPTOR=1
$ python web2py.py --nogui
################################################################################

10. Direct a browser to http://127.0.0.1:8000/phylografterv2/stree/index
(should display a "Source trees" table).



11. Kill the server in your terminal

12. Revert the migrate=True changes applied in the "Bootstrap the DB tables" step


13. To relaunch the server in the future, with the same admin password:
################################################################################
$ python web2py.py --nogui -a '<recycle>'
################################################################################


14. Direct a browser to http://127.0.0.1:8000/phylografterv2/study/index


15. Log in 

16. quit web2py

17. log in to mysql, add a contributor group and put your login in that group in
    the membership table:

###############################################################################
$ mysql -u test -p abc123

mysql> use phylografter
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

mysql> SELECT * from auth_membership ;

mysql> SELECT * from auth_group ;
+----+-------------+---------------------+
| id | role        | description         |
+----+-------------+---------------------+
|  1 | user_1      |                     |
+----+-------------+---------------------+

mysql> SELECT * from auth_user ;
+----+------------+-------------+--------------------+----------+------------------+--------------------+-------------------------------------------------------+
| id | first_name | last_name   | email              | password | registration_key | reset_password_key | registration_id                                       |
+----+------------+-------------+--------------------+----------+------------------+--------------------+-------------------------------------------------------+
|  1 | Bogus      | McTestsALot | bogus@gmail.com    | NULL     |                  |                    | https://www.google.com/profiles/23456363iaieuiay621a  |
+----+------------+-------------+--------------------+----------+------------------+--------------------+-------------------------------------------------------+

mysql> INSERT INTO auth_membership VALUES ('2', 'contributor', 'contrib description') ;
Query OK, 1 row affected (0.00 sec)

mysql> SELECT * from auth_group ;
+----+-------------+---------------------+
| id | role        | description         |
+----+-------------+---------------------+
|  1 | user_1      |                     |
|  2 | contributor | contrib description |
+----+-------------+---------------------+
2 rows in set (0.00 sec)

mysql> INSERT INTO auth_membership VALUES ('2', '1', '2') ;
Query OK, 1 row affected (0.00 sec)

mysql> SELECT * from auth_membership ;
+----+---------+----------+
| id | user_id | group_id |
+----+---------+----------+
|  1 |       1 |        1 |
|  2 |       1 |        2 |
+----+---------+----------+
2 rows in set (0.00 sec)
###############################################################################

18. Relaunch the server in the future, with the same admin password:
################################################################################
$ python web2py.py --nogui -a '<recycle>'
################################################################################

19. To load a SQL dump: launch the mysql daemon with large packet sizes:
    mysqld_safe --max_allowed_pack=32M
Edit the dump to put the Table structure for ottol_node to be above the structure for ottol_name
    


