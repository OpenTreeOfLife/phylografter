"""
functions for linking nodes to taxa
"""

def taxa2ncbi(db):
    t = db.taxon
    q = t.id>0
    tax2id = dict([ (x.name, x.id) for x in db(q).select(t.id, t.name) ])
    t = db.ncbi_taxon
    q = t.name.belongs(tax2id.keys())
    ncbi2id = dict([ (x.name, x.id) for x in db(q).select(t.id, t.name) ])
    t = db.taxon
    for n, i in ncbi2id.items():
        j = tax2id[n]
        t[j].update_record(ncbi_taxon=i)
    db.commit()

def suggest(db, root):
    import build, ivy
    leaves = root.leaves()
    d = {}
    tips = ivy.storage.CDict(set)
    for lf in leaves:
        v = lf.rootpath()
        ancs = set()
        name = None
        for i, n in enumerate(v):
            if n.rec.taxon:
                r = db.taxon[int(n.rec.taxon)]
                name = r.name
                ancs = [ (x.next, x.id, x.name) for x in
                         build.rootpath(db.taxon, r) ]
            if n in d:
                d[n] = d[n] & set(ancs)
            else:
                d[n] = set(ancs)
            if name:
                tips[n].add(name)
    return d, tips
