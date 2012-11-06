Below here are notes on installing phylografter on installing phylografter on Mac.

(1) Install Ivy. You can get pip from http://www.pip-installer.org/en/latest/

<pre>
for module in matplotlib scipy numpy biopython pyparsing ipython lxml PIL ivy-phylo
do
    pip install --upgrade "$module" 
done
</pre>

(2) Install MySQL.

I'm assuming below that it is installed in /usr/local/mysql 
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
https://dl.dropbox.com/u/1939917/phylografter.sql.gz 
To load a SQL dump: launch the mysql daemon with large packet sizes:

<pre>
sudo /usr/local/mysql/bin/mysqld_safe --max_allowed_pack=32M

curl "http://reelab.net/~rree/phylografter.sql.gz" >phylografter.sql.gz
gunzip -c phylografter.sql.gz | \
  /usr/local/mysql/bin/mysql --user=tester --password=abc123 --max_allowed_packet=300M --connect_timeout=6000 phylografter
</pre>

This took 900 seconds (15 minutes) when I [JAR] did it on a 2011 MacBook Air.


(9) Launch web2py (you can use -a &lt;recycle&gt; to re-use the admin password:

<pre>
python web2py.py --nogui -a '&lt;recycle&gt;'
</pre>


(10) Direct a browser to http://127.0.0.1:8000/phylografter/stree/index
(should display a "Source trees" table).

    


