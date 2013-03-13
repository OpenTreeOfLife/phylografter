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

q = ((db.otu.ottol_name==db.ottol_name.id)&
     (db.otu.ottol_name!=None))
t = db.ottol_name
used = db(q).select(t.id, t.preottol_taxid, distinct=True)

## q = ('select distinct ottol_name.id, ottol_name.preottol_taxid '
##      'from ottol_name, otu '
##      'where otu.ottol_name = ottol_name.id '
##      'and otu.ottol_name is not null')
## used_preids = db.executesql(q)

# update used records that map to new ottol uids
for row in used:
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
v = tuple([ x.id for x in used ])
q = 'delete from ottol_name where id not in %s ;' % (v,)
## with open('/tmp/tmp.sql','w') as f:
##     f.write(q)
db.executesql(q)

used_uids = set(pre2uid.values())
# insert new unused records
for uid, row in uid2row.items():
    if uid not in used_uids:
        (uid, parent_uid, name, rank, source, sourceid,
         sourcepid, uniqname, preottol_id) = row
        t.insert(uid=uid, parent_uid=parent_uid,
                 name=name, unique_name = uniqname or name,
                 rank=rank)
    
