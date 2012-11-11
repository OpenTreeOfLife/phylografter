from lxml import etree, objectify
from urllib2 import urlopen
from base64 import b64decode
from ivy.storage import Storage

NCBI = 100

def serialize(e):
    d = {}
    for x in e.iter():
        s = (x.text or "").strip()
        if s:
            tl = x.tag.lower()
            if tl.endswith("title") or tl.endswith("string"):
                s = b64decode(x.text)
            d[x.tag] = s
    return d

def search_namebank(term, keycode):
    params = dict(function="namebank_search",
                  searchName=term,
                  sci=1,
                  keyCode=keycode)
    url = ("http://www.ubio.org/webservices/service.php" + "?" +
           "&".join("%s=%s" % (k,v) for k, v in params.items()))
    
    e = etree.parse(url)
    v = []
    for rec in e.findall("scientificNames/value"):
        d = Storage()
        for c in rec.iterchildren():
            s = c.text
            if c.tag in ("nameString", "fullNameString"):
                s = b64decode(s)
            d[c.tag] = s
        v.append(d)
    return v

def fetch_name(namebank_id, keycode):
    params = dict(function="namebank_object",
                  namebankID=namebank_id,
                  keyCode=keycode)
    url = ("http://www.ubio.org/webservices/service.php" + "?" +
           "&".join("%s=%s" % (k,v) for k, v in params.items()))
    e = etree.parse(url)
    return e

def search_classification(namebank_id, keycode, class_id=None):
    params = dict(function="classificationbank_search",
                  namebankID=namebank_id,
                  keyCode=keycode)
    if class_id:
        params["classificationTitleID"] = class_id
        
    url = ("http://www.ubio.org/webservices/service.php" + "?" +
           "&".join("%s=%s" % (k,v) for k, v in params.items()))
    
    e = etree.parse(url)
    return e
    
def fetch_classification(classificationbank_id, keycode):
    params = dict(function="classificationbank_object",
                  hierarchiesID=classificationbank_id,
                  keyCode=keycode)
    url = ("http://www.ubio.org/webservices/service.php" + "?" +
           "&".join("%s=%s" % (k,v) for k, v in params.items()))
    e = etree.parse(url)
    return e
