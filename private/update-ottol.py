import os, re
from collections import defaultdict
from itertools import imap, ifilter
dump_name = 'taxonomy'
dump_loc = '/tmp/ott2.0'
p = os.path.join(dump_loc, dump_name)
t = db.ottol_name
delim = '\t|\t'
split = lambda x: x.split(delim)[:-1]
NCBI = re.compile(r'ncbi:\(\d+\)')
GBIF = re.compile(r'gbif:\(\d+\)')

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
db.commit()

def split_sourceinfo(s):
    for x in s.split(','):
        a, b = x.split(':')
        yield (a+'_taxid', int(b))

existing_uids = set([ x.accepted_uid for x in
                      db(t.id>0).select(t.accepted_uid, distinct=True) ])

# update and insert name data
for row in uid2row.values():
    uid = int(row[0])
    parent_uid = int(row[1]) or 0
    name = row[2]
    rank = row[3]
    sourceinfo = row[4]
    unique_name = row[5] or name
    
    d = dict(uid=uid, accepted_uid=uid, parent_uid=parent_uid,
             name=name, rank=rank, unique_name=unique_name)
    for k, v in split_sourceinfo(sourceinfo): d[k] = v
    if (uid in existing_uids):
        db(t.uid==uid).update(**d)
    elif unique_name in name2none:
        rec = name2none[unique_name]
        rec.update_record(**d)
    else:
        t.insert(**d)
db.commit()

# deal with ottol_name records without uids
rows = db(t.uid==None).select()
for r in rows:
    name = r.unique_name
    v = syn2uid.get(name)
    if v and len(v)==1:
        uid = v.pop()
        parent_uid = int(row[1])
        name = row[2]
        rank = row[3]
        sourceinfo = row[4]
        unique_name = row[5] or name

        d = dict(uid=uid, accepted_uid=uid,
                 parent_uid=parent_uid, name=name, rank=rank,
                 unique_name=unique_name)
        for kp, vp in split_sourceinfo(sourceinfo): d[kp] = vp
        row = uid2row[uid]
        r.update_record(**d)
db.commit()

# delete unused deprecated names
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
db(q).count()

print 'names without uids:', db(t.uid==None).count()
