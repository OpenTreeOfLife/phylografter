import datetime, socket, os, sys
from ConfigParser import SafeConfigParser

defaults = dict(host="localhost", user="guest", password="guest", dbname="phylografter")

conf = SafeConfigParser(defaults)

user = password = dbname = host = ''

#db = DAL("sqlite://phylografter.db")
#db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=False ) 

if os.path.isfile("applications/%s/private/localconfig" % request.application):
    conf.read("applications/%s/private/localconfig" % request.application)
    host = conf.get("db", "host")
    user = conf.get("db", "user")
    password = conf.get("db", "password")
    dbname = conf.get("db", "dbname")

else:
    conf.read("applications/%s/private/config" % request.application)
    host = conf.get("db", "host")
    user = conf.get("db", "user")
    password = conf.get("db", "password")
    dbname = conf.get("db", "dbname")

db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=False ) 
#db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=False, fake_migrate_all=True, migrate_enabled=False ) 


from gluon.tools import *
## mail = Mail()                    # mailer
auth = Auth(globals(),db)           # authentication/authorization
crud = Crud(globals(),db)           # for CRUD helpers using auth
service = Service(globals())        # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

## mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
## mail.settings.sender = 'you@gmail.com'         # your email
## mail.settings.login = 'username:password'      # your credentials or None
## auth.settings.hmac_key = '<your secret key>'   # before define_tables()
auth.define_tables( migrate=False )                           # creates all needed tables
## auth.settings.mailer = mail                 # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
host = socket.gethostname()
if host == "rickroll":
    host = "www.reelab.net"
else:
    host = "localhost:8000"
from gluon.contrib.login_methods.rpx_account import RPXAccount
auth.settings.actions_disabled=['register','change_password','request_reset_password']
auth.settings.login_form = RPXAccount(
    request, api_key='9435bcb6253fa24c4680cbbd0d4e75a0accde8b3',
    domain='phylografter',
    url = "http://%s/%s/default/user/login" % (host, request.application)
    )

if request.controller=='default' and request.function=='user' and request.args(0)=='login':
    auth.settings.login_next = session._next or URL('index')
else:
    session._next = request.env.path_info

## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None                      # =auth to enforce authorization on crud

# from http://www.web2pyslices.com/main/slices/take_slice/8
clienttools = local_import('clienttools')
page = clienttools.PageManager(globals())
event = clienttools.EventManager(page)
js = clienttools.ScriptManager(page) # javascript helpers
jq = clienttools.JQuery # don't instantiate, just to shorten

define_tables(db)

def delete_stree(i, otu=False):
    rec = db.stree(i)
    assert rec
    snodes = db(db.snode.tree==i)
    if otu:
        q = ((db.snode.tree==db.stree.id)&
             (db.snode.otu==db.otu.id)&
             (db.stree.id==i))
        otus = [ x.id for x in db(q).select(db.otu.id) ]
        db(db.otu.id.belongs(otus)).delete()
    snodes.delete()
    rec.delete_record()

def upload_fasta(study, fname):
    from Bio import SeqIO
    study = db.study(int(study))
    assert study
    recs = SeqIO.parse(fname, "fasta")
    
def insert_ncbi_node(taxid, email):
    from ivy import genbank
    genbank.email = email
    d = genbank.fetchtax(taxid)
    assert d
    parent_taxid = int(d["LineageEx"][-1]["TaxId"])
    t = db.ncbi_node
    p = db(t.taxid==parent_taxid).select().first()
    assert p
    # make room for new node
    b = p.back
    db(t.back>=p.back).update(next=t.next+2, back=t.back+2)
    name = d['ScientificName']; rank = d['Rank']
    i = t.insert(taxid=taxid, name=name, rank=rank,
                 next=b, back=b+1, parent=p.id)
    print "Inserted %s into ncbi_node: %s" % (name, i)
    #insert taxon record
    q = (db.taxon.name==name)&(db.taxon.ncbi_taxid==taxid)
    if not db(q).select().first():
        i = db.taxon.insert(name=name, rank=rank, ncbi_taxid=taxid)
        print "Inserted %s into taxon: %s" % (name, i)
    if d['OtherNames'] and d['OtherNames']['GenbankSynonym']:
        for syn in d['OtherNames']['GenbankSynonym']:
            q = (db.taxon.name==syn)&(db.taxon.ncbi_taxid==taxid)
            if not db(q).select().first():
                i = db.taxon.insert(name=syn, rank=rank, ncbi_taxid=taxid)
                print "Inserted %s into taxon: %s" % (syn, i)
    
        
