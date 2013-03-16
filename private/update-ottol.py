from itertools import imap
p = '/home/rree/SparkleShare/documents/ottol_dump_w_uniquenames_preottol_ids'
delim = '\t|\t'
split = lambda x: x.split(delim)[:-1]
pre2uid = {}
uid2row = {}
pre_many2one = {}
with open(p) as f:
    fields = split(f.next())
    PRE = fields.index('preottol_id')
    UID = fields.index('uid')
    for row in imap(split, f):
        prevals = filter(None, [ int(x or 0) for x in row[PRE].split(',') ])
        uid = int(row[UID])
        if len(prevals)>1:
            pre_many2one[tuple(prevals)] = uid
        uid2row[uid] = row
        for pre in prevals:
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
     (db.study.focal_clade_ottol!=None))
study_used = set([ x.id for x in db(q).select(t.id, distinct=True) ])

used = otu_used | snode_used | study_used

used_uids = set()
# update used ottol_name records that map to new ottol uids
for i in used:
    row = t[i]
    pre = row.preottol_taxid
    if pre in pre2uid:
        uid = pre2uid[pre]
        used_uids.add(uid)
        (uid, parent_uid, name, rank, source, sourceid,
         sourcepid, uniqname, preottol_id) = uid2row[uid]
        gbif = sourceid if source == 'gbif' else None
        ncbi = sourceid if source == 'ncbi' else None
        row.update_record(uid=uid, parent_uid=parent_uid,
                          name=name, unique_name = uniqname or name,
                          rank=rank, ncbi_taxid=ncbi, gbif_taxid=gbif)
        print pre, row.id

# delete unused ottol_name records
v = tuple(sorted(used))
q = 'delete from ottol_name where id not in %s ;' % (v,)
## with open('/tmp/tmp.sql','w') as f:
##     f.write(q)
db.executesql(q)

# deal with cases of multiple preottol_ids-->one ottol uid:

# insert new (unused) ottol_name records from taxomachine dump
for uid, row in uid2row.items():
    if uid not in used_uids:
        (uid, parent_uid, name, rank, source, sourceid,
         sourcepid, uniqname, preottol_id) = row
        gbif = sourceid if source == 'gbif' else None
        ncbi = sourceid if source == 'ncbi' else None
        t.insert(uid=uid, parent_uid=parent_uid,
                 name=name, unique_name = uniqname or name,
                 rank=rank, ncbi_taxid=ncbi, gbif_taxid=gbif)
    
# insert synonym records
p = '/home/rree/SparkleShare/documents/ottol_dump.synonyms'
with open(p) as f:
    fields = split(f.next())
    for row in imap(split, f):
        uid, accepted_uid, name, nametype, source = row
