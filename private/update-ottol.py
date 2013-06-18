import os, re
from collections import defaultdict
from itertools import imap, ifilter
dump_name = 'taxonomy'
dump_loc = '/tmp/ott2.0'
p = os.path.join(dump_loc, dump_name)
t = db.ottol_name
delim = '\t|\t'
split = lambda x: x.split(delim)[:-1]

def query_used(fld='accepted_uid'):
    q = ((db.otu.ottol_name==db.ottol_name.id)&
         (db.otu.ottol_name!=None))
    otu_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

    q = ((db.snode.ottol_name==db.ottol_name.id)&
         (db.snode.ottol_name!=None))
    snode_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

    q = ((db.study.focal_clade_ottol==db.ottol_name.id)&
         (db.study.focal_clade_ottol!=None))
    study_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

    used = otu_used | snode_used | study_used
    return used

name2none = {}
for r in db(t.uid==None).select():
    name2none[r.unique_name] = r
print 'names without uids:', len(name2none)

with open(os.path.join(dump_loc,'deprecated')) as f:
    deprecated = [ int(x.split()[0]) for x in f ]

syn2uid = defaultdict(list)
with open(os.path.join(dump_loc,'synonyms')) as f:
    for row in imap(split, f):
        k = row[0]; v = row[1]
        syn2uid[k].append(int(v))

## with open('/tmp/synonym-multiple-uids.txt','w') as f:
##     for k, v in sorted(syn2uid.items()):
##         if len(v)>1: f.write('%s\t%s\n' % (k, sorted(v)))

uid2row = {}
name2row = {}
with open(p) as f:
    fields = split(f.next())
    UID = fields.index('uid')
    for row in imap(split, f):
        uid = int(row[UID])
        uid2row[uid] = row
        name = row[5] or row[2]
        name2row[name] = row

# select used preottol names
fld = 'accepted_uid'
q = ((db.otu.ottol_name==db.ottol_name.id)&
     (db.otu.ottol_name!=None))
otu_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

q = ((db.snode.ottol_name==db.ottol_name.id)&
     (db.snode.ottol_name!=None))
snode_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

q = ((db.study.focal_clade_ottol==db.ottol_name.id)&
     (db.study.focal_clade_ottol!=None))
study_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

used = otu_used | snode_used | study_used

# update used deprecated names
q = t.accepted_uid.belongs(deprecated) & t.accepted_uid.belongs(used)
used_deprecated = db(q).select(t.id, t.name)
n = len(used_deprecated)
print 'used_deprecated:', n
i = 0; j = 0
for row in used_deprecated:
    k = row.name; v = syn2uid.get(row.name)
    if not v: # name does not have a synonym
        i += 1
    elif v and len(v)>1: # name has a synonym matching multiple uids
        j += 1
    else: # update the record
        #row.update_record(accepted_uid=v.pop())
        new_uid = v.pop()
        row.update_record(accepted_uid=new_uid)
        print '%s\r' % n
    n -= 1
db.commit()

## V = open('/tmp/update-ottol.sql','w')

def split_sourceinfo(s):
    for x in s.split(','):
        a, b = x.split(':')
        yield (a+'_taxid', int(b))

existing_uids = set([ x.accepted_uid for x in
                      db(t.id>0).select(t.accepted_uid, distinct=True) ])

# update and insert name data
print 'updating name data'
n = len(uid2row)
for row in uid2row.values():
    uid = int(row[0])
    parent_uid = int(row[1] or 0)
    name = row[2]
    rank = row[3] or None
    sourceinfo = row[4]
    unique_name = row[5] or name
    
    d = dict(uid=uid, accepted_uid=uid, parent_uid=parent_uid,
             name=name, rank=rank, unique_name=unique_name)
    for k, v in split_sourceinfo(sourceinfo): d[k] = v
    if uid in existing_uids:
        db(t.uid==uid).update(**d)
        ## V.write('%s\n' % db(t.uid==uid)._update(**d))
    elif unique_name in name2none:
        rec = name2none[unique_name]
        rec.update_record(**d)
        ## V.write('%s\n' % db(t.id==rec.id)._update(**d))
    else:
        t.insert(**d)
        ## V.write('%s\n' % t._insert(**d))
    print '%s\r' % n
    n -= 1
db.commit()

# deal with ottol_name records without uids
print 'updating names without uids'
rows = db(t.uid==None).select()
n = len(rows)
for r in rows:
    name = r.unique_name
    v = syn2uid.get(name)
    if v and len(v)==1:
        uid = v.pop()
        print name, uid
        parent_uid = int(row[1])
        name = row[2]
        rank = row[3] or None
        sourceinfo = row[4]
        unique_name = row[5] or name

        d = dict(uid=uid, accepted_uid=uid,
                 parent_uid=parent_uid, name=name, rank=rank,
                 unique_name=unique_name)
        for kp, vp in split_sourceinfo(sourceinfo): d[kp] = vp
        row = uid2row[uid]
        r.update_record(**d)
        ## V.write('%s\n' % db(t.id==r.id)._update(**d))
    elif name in name2row:
        uid = int(name2row[name][0])
        eid = db(t.accepted_uid==uid).select(t.id).first().id
        print 'replacing', name, 'with', uid, eid
        db(db.otu.ottol_name==r.id).update(ottol_name=eid)
        db(db.snode.ottol_name==r.id).update(ottol_name=eid)
        db(db.study.focal_clade_ottol==r.id).update(focal_clade_ottol=eid)
        ## V.write('%s\n' % db(db.otu.ottol_name==r.id)._update(ottol_name=eid))
        ## V.write('%s\n' % db(db.snode.ottol_name==r.id)._update(ottol_name=eid))
        ## V.write('%s\n' % db(db.study.focal_clade_ottol==r.id)._update(focal_clade_ottol=eid))
    ## print '%s\r' % n
    n -= 1
## db.commit()

# delete unused deprecated names
## print 'deleting unused deprecated names'
q = ((db.otu.ottol_name==db.ottol_name.id)&
     (db.otu.ottol_name!=None))
otu_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

q = ((db.snode.ottol_name==db.ottol_name.id)&
     (db.snode.ottol_name!=None))
snode_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

q = ((db.study.focal_clade_ottol==db.ottol_name.id)&
     (db.study.focal_clade_ottol!=None))
study_used = set([ x[fld] for x in db(q).select(t[fld], distinct=True) ])

used = otu_used | snode_used | study_used

q =(t.accepted_uid.belongs(deprecated))&(~t.accepted_uid.belongs(used)) 
## db(q).delete()
## V.write('%s\n' % db(q)._delete())
## print 'names without uids:', db(t.uid==None).count()
## V.close()

# find uid by ncbi taxid
q = ('select distinct ncbi_taxid, accepted_uid from ottol_name '
     'where accepted_uid is not null and ncbi_taxid is not null')
taxid2uid = dict(db.executesql(q))

for r in db(t.uid==None)(t.ncbi_taxid!=None).select():
    uid = taxid2uid.get(r.ncbi_taxid)
    if uid:
        print r.unique_name, r.ncbi_taxid, uid
        r.update_record(accepted_uid=uid)

q = ('select distinct gbif_taxid, accepted_uid from ottol_name '
     'where accepted_uid is not null and gbif_taxid is not null')
taxid2uid = dict(db.executesql(q))

for r in db(t.uid==None)(t.gbif_taxid!=None).select():
    uid = taxid2uid.get(r.gbif_taxid)
    if uid:
        print r.unique_name, r.gbif_taxid, uid
        #r.update_record(accepted_uid=uid)
    
# find duplicate uids
q = ('select unique_name, count(*) c from ottol_name '
     ## 'where uid is not null '
     'group by unique_name having c > 1')
v = [ x[0] for x in db.executesql(q) ]
w = db(t.unique_name.belongs(v)).select(orderby=t.unique_name)
i = 0
todel = []
for x in w:
    uid = x.uid
    if ((x.unique_name not in syn2uid) and
        (x.uid not in uid2row) and
        (x.parent_uid is None) and
        (x.otu.isempty() and x.snode.isempty() and x.study.isempty())):
        todel.append(x.id)
        i += 1
    elif (x.accepted_uid not in uid2row):
        print x.uid, x.accepted_uid, x.unique_name
    elif ((x.accepted_uid not in uid2row) and
          (x.otu.isempty() and x.snode.isempty() and x.study.isempty())):
        print x.uid, x.accepted_uid, x.unique_name
        del t[x.id]
    elif ((x.accepted_uid not in uid2row) and
          not (x.otu.isempty() and x.snode.isempty() and x.study.isempty())):
        q = (t.unique_name==x.unique_name)&(t.accepted_uid!=x.accepted_uid)
        r = db(q).select().first()
        print x.uid, x.accepted_uid, x.unique_name, r.accepted_uid
        x.otu.update(ottol_name=r.id)
        x.snode.update(ottol_name=r.id)
        x.study.update(focal_clade_ottol=r.id)
    else:
        if x.unique_name in syn2uid and x.parent_uid is None:
            u = syn2uid[x.unique_name][0]
            realname = db(t.uid==u).select().first()
            assert realname, str([x.unique_name, u])
            s = '%s (synonym of %s)' % (x.unique_name, realname.unique_name)
            print s
            x.update_record(unique_name=s)
#db(t.accepted_uid.belongs(todel)).delete()
