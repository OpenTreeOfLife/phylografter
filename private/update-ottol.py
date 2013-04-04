import os, re
from itertools import imap, ifilter
dump_name = 'ottol_dump_w_uniquenames_preottol_ids'
dump_loc = '/home/rree/SparkleShare/documents'
p = os.path.join(dump_loc, dump_name)
t = db.ottol_name
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

# select used preottol names
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
db.commit()

# delete unused ottol_name records
v = tuple(sorted(used))
q = 'delete from ottol_name where id not in %s ;' % (v,)
## with open('/tmp/tmp.sql','w') as f:
##     f.write(q)
db.executesql(q)
print 'done\n'

# deal with cases of multiple preottol_ids-->one ottol uid:
q = ('select uid from ottol_name '
     'group by unique_name, uid having (count(uid)>1)')
dup_uids = [ x[0] for x in db.executesql(q) ]
for uid in dup_uids:
    rows = list(db(t.uid==uid).select())
    i = rows[0].id
    print rows[0].name
    for r in rows[1:]:
        r.otu.update(ottol_name=i)
        r.snode.update(ottol_name=i)
        db(db.study.focal_clade_ottol==r.id).update(focal_clade_ottol=i)
        r.delete_record()

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

## # insert synonym records
p = '/home/rree/SparkleShare/documents/ottol_dump.synonyms'
p = '/home/rree/ottol_dump.synonyms'
def filt(x, yearpat=re.compile(r'\d{4}')):
    s = x[3]; name = x[2]; uid = int(x[0])
    c = db(t.name==name).count()
    return ((s in (#'synonym', 'genbank synonym', 'equivalent name',
                   'anamorph', 'teleomorph')) and
            (not s[0] in '"\'') and
            (db(t.uid==uid).count()==0) and
            ## (not yearpat.search(name)) and
            (c == 0))

inserted = 0
with open(p) as f:
    fields = split(f.next())
    for r in ifilter(filt, imap(split, f)):
        uid, accepted_uid, name, nametype, source = r
        row = db(t.uid==accepted_uid).select().first()
        comments = 'synonym of %s (uid:%s; %s)' % (row.name, row.uid, source)
        t.insert(uid=uid, accepted_uid=accepted_uid, name=name, rank=row.rank,
                 gbif_taxid=row.gbif_taxid, ncbi_taxid=row.ncbi_taxid,
                 treebase_taxid=row.treebase_taxid,
                 namebank_taxid=row.namebank_taxid,
                 unique_name=name, comments=comments)
        inserted += 1
print inserted

## # duplicate unique_names?
## q = ('select id, uid, name, unique_name from ottol_name '
##      'where unique_name is not null '
##      'group by unique_name having (count(unique_name)>1) '
##      'order by unique_name '
##      )
## v = db.executesql(q)

## for r in db(t.uid==None).select():
##     q = db((t.name==r.name)&(t.uid!=None))
##     if q.count() == 1:
##         x = q.select().first()
        
# clean up - delete name variants differing only in quotes
rows = db((t.name.startswith('"')|t.name.startswith("'"))&
          (t.uid!=t.accepted_uid)&
          (t.name==t.unique_name)).select()
for r in rows:
    s = r.name.replace('"','').replace("'",'')
    c = db((t.name==s)&(t.accepted_uid==r.accepted_uid)).count()
    if c: r.delete_record()
        
# clean up - figure out unmapped, used preottol names
rows = list(db(t.uid==None).select())
for r in rows:
    q = db((t.uid!=None)&(t.unique_name==r.name))
    if q.count()==1:
        r2 = q.select().first()
        r.update_record(uid=r2.uid, accepted_uid=r2.accepted_uid, rank=r2.rank,
                        gbif_taxid=r2.gbif_taxid, ncbi_taxid=r2.ncbi_taxid,
                        comments=r2.comments)
        if (r2.otu.count()==0 and r2.snode.count()==0 and
            db(db.study.focal_clade_ottol==r2.id).count()==0):
            print r.name
            r2.delete_record()


rows = list(db(t.uid==None).select())
for r in rows:
    for otu in r.otu.select():
        q = db((t.uid!=None)&(t.unique_name==otu.label))
        if q.count()==1:
            print otu.label
            i = q.select(t.id).first().id
            r.otu.update(ottol_name=i)
            r.snode.update(ottol_name=i)
            r.study.update(focal_clade_ottol=i)

    ## r.otu.update(ottol_name=i)
    ## r.snode.update(ottol_name=i)
    ## r.study.update(focal_clade_ottol=i)
    
rows = db(t.uid==None).select()
with open('unmapped-preottol.csv','w') as f:
    rows.export_to_csv_file(f)
