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

Download new mysql dump from https://dl.dropbox.com/u/1939917/phylografter.sql.gz

To load a SQL dump: launch the mysql daemon with large packet sizes:
    mysqld_safe --max_allowed_pack=32M
Edit the dump to put the Table structure for ottol_node to be above the structure for ottol_name


9. Launch web2py (you can use -a <recycle> to re-use the admin password:
################################################################################
$ python web2py.py --nogui -a '<recycle>'
################################################################################

10. Direct a browser to http://127.0.0.1:8000/phylografterv2/stree/index
(should display a "Source trees" table).

    


