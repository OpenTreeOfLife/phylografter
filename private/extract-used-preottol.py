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

rows = db(t.id.belongs(used)).select()
with open('/tmp/preottol-used.csv', 'w') as f:
    rows.export_to_csv_file(f)
