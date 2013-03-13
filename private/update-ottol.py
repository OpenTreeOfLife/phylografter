from itertools import imap
p = '/home/rree/SparkleShare/documents/ottol_dump_w_uniquenames_preottol_ids'
delim = '\t|\t'
split = lambda x: x.split(delim)[:-1]
pre2uid = {}
uid2row = {}
with open(p) as f:
    fields = split(f.next())
    PRE = fields.index('preottol_id')
    UID = fields.index('uid')
    for row in imap(split, f):
        prevals = [ int(x or 0) for x in row[PRE].split(',') ]
        uid = int(row[UID])
        uid2row[uid] = row
        for pre in filter(None, prevals):
            assert pre not in pre2uid, pre
            pre2uid[pre] = uid

t = db.ottol_name

q = ((db.otu.ottol_name==db.ottol_name.id)&
     (db.otu.ottol_name!=None))
otu_used = set([ x.id for x in db(q).select(t.id, distinct=True) ])

q = ((db.snode.ottol_name==db.ottol_name.id)&
     (db.snode.ottol_name!=None))
snode_used = set([ x.id for x in db(q).select(t.id, distinct=True) ])

q = ((db.study.focal_clade_ottol==db.ottol_name.id)&
     (db.study.focal_ottol_name!=None))
study_used = set([ x.id for x in db(q).select(t.id, distinct=True) ])

used = otu_used | snode_used | study_used

# update used records that map to new ottol uids
for i in used:
    row = t[i]
    pre = row.preottol_taxid
    if pre in pre2uid:
        uid = pre2uid[pre]
        (uid, parent_uid, name, rank, source, sourceid,
         sourcepid, uniqname, preottol_id) = uid2row[uid]
        row.update_record(uid=uid, parent_uid=parent_uid,
                          name=name, unique_name = uniqname or name,
                          rank=rank)
        print pre, row.id

# delete unused records
v = tuple(sorted(used))
q = 'delete from ottol_name where id not in %s ;' % (v,)
## with open('/tmp/tmp.sql','w') as f:
##     f.write(q)
db.executesql(q)

# insert new unused records
for uid, row in uid2row.items():
    if uid not in used_uids:
        (uid, parent_uid, name, rank, source, sourceid,
         sourcepid, uniqname, preottol_id) = row
        t.insert(uid=uid, parent_uid=parent_uid,
                 name=name, unique_name = uniqname or name,
                 rank=rank)
    
