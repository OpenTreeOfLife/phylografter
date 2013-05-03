Below here are notes on installing phylografter on installing phylografter on Mac.

(1) Install prerequisites. You can get pip from http://www.pip-installer.org/en/latest/

<pre>
for module in matplotlib numpy scipy biopython pyparsing ipython lxml PIL requests
do
    pip install --upgrade "$module" 
done
</pre>
This builds from source, make sure a fortran compiler is installed.  May have problem where numpy doesn't load correctly and scipy install fails - try building numpy from github source.[PEM]

Alternately, the included **requirements.txt** file lists known-good versions of all the
required python modules for phylografter and opentree, plus a few convenience
modules. To [install these modules using pip](http://www.pip-installer.org/en/latest/cookbook.html#requirements-files), 

<pre>
pip install -r requirements.txt
</pre>

_TODO: Add [installation instructions](http://pythonhosted.org/pyenchant/tutorial.html#installing-pyenchant) for **pyenchant** and **libenchant**._

(2) Install MySQL.

I'm assuming below that it is installed in /usr/local/mysql.
I used MySQL-5.5.27

(3) Configure SQL.

Create an SQL user ( 'tester' in our example) <br/>
Assign the user a password ('abc123' in our example) <br/>
Create an SQL database called something ('phylografter' in our example) <br/>
Give the user privileges to modify the database

<pre>
 $ /usr/local/mysql/bin/mysql -u root --password=sqluserspassword
mysql> CREATE USER 'tester'@'localhost' IDENTIFIED BY 'abc123' ;
mysql> CREATE database phylografter ;
mysql> GRANT ALL ON phylografter.* to 'tester'@'localhost' ;
mysql> FLUSH PRIVILEGES;
</pre>

(4) Configure Phylografter

Set the phylografter/private/config to contain:

<pre>
[db]
host = localhost
user = tester
password = abc123
dbname = phylografter
</pre>

(5) lxml  [you probably already did this, see above]

<pre>
pip install lxml
</pre>

(6) Download and unpack the source code version of web2py from 
http://www.web2py.com/examples/default/download .  I used Version 1.99.7


(7) Register phylografter as a web2py app by creating a symbolic link

<pre>
cd web2py/applications
ln -s /full/path/to/phylografter .
</pre>

where the phylografter directory above is the one where you found this
README file.


(8) Bootstrap the DB tables for phylografter. Download new mysql dump from
http://reelab.net/~rree/phylografter.sql.gz 
To load a SQL dump: launch the mysql daemon with large packet sizes:

<pre>
sudo /usr/local/mysql/bin/mysqld_safe --max_allowed_pack=32M

curl "http://reelab.net/~rree/phylografter.sql.gz" >phylografter.sql.gz
gunzip -c phylografter.sql.gz | \
  /usr/local/mysql/bin/mysql --user=tester --password=abc123 --max_allowed_packet=300M --connect_timeout=6000 phylografter
</pre>

This took 900 seconds (15 minutes) when I [JAR] did it on a 2011 MacBook Air.


(9) Launch web2py (you can use -a &lt;recycle&gt; to re-use the admin password):

<pre>
python web2py.py --nogui -a '&lt;recycle&gt;'
</pre>


(10) Direct a browser to http://127.0.0.1:8000/phylografter/stree/index
(should display a "Source trees" table).

    
Authorizing users to upload
--------------

You can authorize users to upload trees as follows:

1. From http://127.0.0.1:8000/admin/default/site
1. Under phylografter click 'Edit'
1. Under Models click 'database administration'
1. Under db.auth\_membership click 'insert new auth\_membership'
1. Choose your user and the 'contributor' group (id 3) and click submit


Experimental features
=====================

Support for 2nexml functionality, and discussion of launching external processes
---------------
If you add a section similar to:

<pre>
[external]
dir = /tmp/phylografter_external_tools/
2nexml = /usr/local/bin/2nexml
</pre>

to the private/config file, then you should be able to use the NEXUS to NeXML 
conversion facility. The "dir" setting in the "external" section
specifies a directory on the filesystem that will be the parent of the scratch
directory used when invoking external processes.  

The "2nexml" setting in the "external" section is the absolute path of the 2nexml
executable on the server's filesystem. Consult https://github.com/OpenTreeOfLife/2nexml
for details on how to install the 2nexml tool.

The URL for invoking this controller is:
DOMAIN/phylografter/study/to_nexml/ID
where the ID is the filename that web2py generates for a file that is uploaded
as part of a study. This is the same ID scheme used in the study/download/ID 
URLs, so this filename should be unique.

When the controller is invoked, phylografter will try to find a row in the
study_file table that has a file field that matches the ID.  If it finds this row,
phylografter will trigger a newly implemented system for invoking an external process.
 In this case, it will invoke the 2nexml command-line tool.


NEXUS to NeXML conversion is typically fast, so the call to the external process
blocks.
