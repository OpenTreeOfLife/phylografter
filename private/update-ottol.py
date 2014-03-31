import os, re, csv
import graph_tool.all as gt
from collections import defaultdict
from itertools import imap, ifilter, izip
dump_name = 'taxonomy.tsv'
dump_loc = '/home/rree/ott2.4/ott'
dump_path = os.path.join(dump_loc, dump_name)

sql = []

# load taxonomy.tsv into a list of rows
data = []
n = 0
split = lambda s: (
    [ x.strip() or None for x in s.split('|')][:-1] if s[-2]=='\t'
    else [ x.strip() or None for x in s.split('|')]
)
c2p = dict() # map child uid to parent uid
with open(dump_path) as f:
    fields = split(f.readline())
    for v in imap(split, f):
        # convert uid and parent_uid to ints
        for i in 0,1: v[i] = int(v[i] or 0)
        taxid = v[0]
        data.append(v)
        c2p[taxid] = v[1]
        print n, '\r',
        n += 1
    print 'done'

deprecated = {} # maps old uid to None (if decommissioned) or a new uid
with open(os.path.join(dump_loc,'deprecated.tsv')) as f:
    f.next()
    for s in f:
        w = s.split('\t')
        k = int(w[0])
        v = int(w[5]) if (w[5] and w[5].strip() != '*') else None
        if v: assert v in c2p, v
        deprecated[k] = v

# synonyms
uid2synrows = defaultdict(list)
with open(os.path.join(dump_loc,'synonyms.tsv')) as f:
    fields = split(f.readline())
    for v in imap(split, f):
        uid = int(v[1])
        uid2synrows[uid].append(v)

uid2sqlid = {}
uid2syn_sqlids = defaultdict(list)
syn_sqlid2uid = {}
# file has tab-separated id, uid, accepted_uid rows
with open('ottol_name.csv') as f:
    fields = f.next().strip().split('\t')
    for s in f:
        sqlid, uid, acuid = [ int(x or 0) for x in s.strip().split('\t') ]
        if uid == acuid:
            uid2sqlid[uid] = sqlid
        else:
            uid2syn_sqlids[acuid].append(sqlid)
            syn_sqlid2uid[sqlid] = acuid

# change otus and snodes pointing to synonym rows to point to accepted
# taxon rows
# sqlid, accepted_uid, unique_name of ottol_name rows used in otu and snode
with open('used_ottol_name.csv') as f:
    fields = f.next().strip().split('\t')
    for s in f:
        sqlid, uid, unique_name = s.strip().split('\t')
        sqlid = int(sqlid)
        uid = int(uid)
        if uid in deprecated:
            newuid = deprecated[uid]
            if newuid:
                acc_sqlid = uid2sqlid[newuid]
                s = 'update {} set ottol_name = {} where ottol_name = {}'
                sql.append(s.format('otu', acc_sqlid, sqlid))
                sql.append(s.format('snode', acc_sqlid, sqlid))
            else:
                s = 'update {} set ottol_name = NULL where ottol_name = {}'
                sql.append(s.format('otu', sqlid))
                sql.append(s.format('snode', sqlid))
            continue
        if sqlid in syn_sqlid2uid:
            acc_sqlid = uid2sqlid[uid]
            s = 'update {} set ottol_name = {} where ottol_name = {}'
            sql.append(s.format('otu', acc_sqlid, sqlid))
            sql.append(s.format('snode', acc_sqlid, sqlid))


def ivy_taxonomy_tree():
    import ivy
    Node = ivy.tree.Node
    nodes = [ Node(**dict(izip(fields, row))) for row in data ]
    uid2node = dict([ (n.uid, n) for n in nodes ])
    r = nodes[0]
    r.isroot = True
    for n in nodes[1:]:
        p = uid2node[n.parent_uid]
        p.add_child(n)

    for n in nodes:
        n.suppress = 0
        if not n.children: n.isleaf = True
        else: n.isleaf = False
        n.label = n.uniqname or n.name
        if not n.flags: n.flags = ''
        if not n.sourceinfo: n.sourceinfo = ''

    def suppress(n):
        labels = [
            'Deltavirus',
            'Viruses',
            'vectors',
            'Satellite Viruses',
            'Tobacco leaf curl Japan beta',
            'Viroids',
            'artificial sequences',
            'organismal metagenomes',
            'eukaryotic vectors'
            ]
        name = n.name.lower()
        if (('viral' in n.flags) or
            ('unclassified' in n.flags) or
            ('not_otu' in n.flags) or
            ('hidden' in n.flags) or
            ('barren' in n.flags) or
            ('major_rank_conflict' in n.flags) or
            ('extinct' in n.flags) or
            ('incertae_sedis' in n.flags) or
            ('tattered' in n.flags) or
            ('metagenome' in name) or
            ('artificial' in name) or
            ('unallocated' in name) or
            (' phage ' in name) or
            (' vector ' in name) or
            (('environmental' in name) and ('ncbi' not in n.sourceinfo)) or
            (n.name in labels)):
            n.suppress = 1
    for n in nodes: suppress(n)

    v = [ x for x in nodes if x.suppress ]
    def prune(x):
        try:
            x.parent.children.remove(x)
        except:
            pass
        x.parent = None
        x.children = []
    map(prune, v)

    v = [ x for x in r if not x.isleaf and not x.children ]
    while v:
        print 'pruning', len(v)
        map(prune, v)
        v = [ x for x in r if not x.isleaf and not x.children ]

    v = []
    for n in r:
        name = n.name.lower()
        if (name.startswith('basal ') or
            name.startswith('stem ') or
            name.startswith('early diverging ')):
            v.append(n)
    for n in v: n.collapse()
    assert len([ x for x in r if not x.isleaf and not x.children ])==0
    
    ivy.tree.index(r, n=1)
    return r

r = ivy_taxonomy_tree()


class Traverser(gt.DFSVisitor):
    def __init__(self, pre=None, post=None):
        # function to call on each vertex, preorder
        if not pre: pre = lambda x:None
        self.pre = pre
        if not post: post = lambda x:None
        self.post = post # postorder

    def discover_vertex(self, v):
        self.pre(v)

    def finish_vertex(self, v):
        self.post(v)

def get_or_create_vp(g, name, ptype):
    p = g.vp.get(name)
    if not p:
        p = g.new_vertex_property(ptype)
        g.vp[name] = p
    return p

def get_or_create_ep(g, name, ptype):
    p = g.ep.get(name)
    if not p:
        p = g.new_edge_property(ptype)
        g.ep[name] = p
    return p

def _attach_funcs(g):
    def taxid_name(taxid):
        v = g.taxid_vertex.get(taxid)
        if v: return g.vertex_name[v]
    g.taxid_name = taxid_name

    ## def taxid_dubious(taxid):
    ##     v = g.taxid_vertex.get(taxid)
    ##     if v: return g.dubious[v]
    ## g.taxid_dubious = taxid_dubious

    def taxid_hindex(taxid):
        v = g.taxid_vertex.get(taxid)
        if v: return g.hindex[v]
        else: print 'no hindex:', taxid
    g.taxid_hindex = taxid_hindex

def index_graph(g, reindex=False):
    '''
    create a vertex property map with hierarchical (left, right)
    indices
    '''
    if 'hindex' in g.vp and 'depth' in g.vp and not reindex:
        return g
    v = g.vertex(0) # root
    hindex = get_or_create_vp(g, 'hindex', 'vector<int>')
    depth = get_or_create_vp(g, 'depth', 'int')
    n = [g.num_vertices()]
    def traverse(p, left, dep):
        depth[p] = dep
        if p.out_degree():
            l0 = left
            for c in p.out_neighbours():
                l, r = traverse(c, left+1, dep+1)
                left = r
            lr = (l0, r+1)
        else:
            lr = (left, left+1)
        hindex[p] = lr
        ## print g.vertex_name[p], lr
        print n[0], '\r',
        n[0] -= 1
        return lr
    g.hindex = hindex
    traverse(v, 1, 0)
    print 'done'

def _filter(g):
    # higher taxa that should be removed (nodes collapsed), and their
    # immmediate children flagged incertae sedis and linked back to
    # the parent of collapsed node
    incertae_keywords = [
        'endophyte','scgc','libraries','samples','metagenome','unclassified',
        'other','unidentified','mitosporic','uncultured','incertae',
        'environmental']

    # taxa that are not clades, and should be removed (collapsed) -
    # children linked to parent of collapsed node
    collapse_keywords = ['basal ','stem ','early diverging ']

    # higher taxa that should be removed along with all of their children
    remove_keywords = ['viroids','virus','viruses','viral','artificial']

    print 'removing'
    rm = g.collapsed
    def f(x): rm[x] = 1
    T = Traverser(post=f)
    for v in ifilter(lambda x:x.out_degree(), g.vertices()):
        name = g.vertex_name[v].lower()
        s = name.split()
        for kw in remove_keywords:
            if kw in s:
                gt.dfs_search(g, v, T)
                break

        for kw in incertae_keywords:
            if kw in s:
                gt.dfs_search(g, v, T)
                ## rm[v] = 1
                ## for c in v.out_neighbours():
                ##     g.incertae_sedis[c] = 1
                break

        s = name.replace('-', ' ')
        for w in collapse_keywords:
            if s.startswith(w):
                rm[v] = 1
                break

    g.set_vertex_filter(rm, inverted=True)
    # assume root == vertex 0
    outer = [ v for v in g.vertices()
              if int(v) and v.in_degree()==0 ]
    g.set_vertex_filter(None)

    for v in outer:
        p = v.in_neighbours().next()
        while rm[p]:
            p = p.in_neighbours().next()
        g.edge_in_taxonomy[g.add_edge(p, v)] = 1
    print 'done'

    g.set_vertex_filter(rm, inverted=True)

    for v in g.vertices():
        if int(v): assert v.in_degree()==1

def create_taxonomy_graph():
    g = gt.Graph()
    g.vertex_taxid = get_or_create_vp(g, 'taxid', 'int')
    g.vertex_name = get_or_create_vp(g, 'name', 'string')
    g.vertex_unique_name = get_or_create_vp(g, 'unique_name', 'string')
    g.vertex_rank = get_or_create_vp(g, 'rank', 'string')
    g.vertex_ncbi = get_or_create_vp(g, 'ncbi', 'int')
    g.vertex_gbif = get_or_create_vp(g, 'gbif', 'int')
    g.vertex_silva = get_or_create_vp(g, 'silva', 'string')
    g.vertex_irmng = get_or_create_vp(g, 'irmng', 'int')
    g.edge_in_taxonomy = get_or_create_ep(g, 'istaxon', 'bool')
    g.vertex_in_taxonomy = get_or_create_vp(g, 'istaxon', 'bool')
    g.vertex_flags = get_or_create_vp(g, 'flags', 'string')
    g.incertae_sedis = get_or_create_vp(g, 'incertae_sedis', 'bool')
    g.collapsed = get_or_create_vp(g, 'collapsed', 'bool')
    g.taxid_vertex = {}

    taxid2vid = {}
    data = []
    n = 0
    split = lambda s: (
        [ x.strip() or None for x in s.split('|')][:-1] if s[-2]=='\t'
        else [ x.strip() or None for x in s.split('|')]
    )
    with open(dump_path) as f:
        f.readline()
        for v in imap(split, f):
            # convert uid and parent_uid to ints
            for i in 0,1: v[i] = int(v[i] or 0)
            taxid = v[0]
            taxid2vid[taxid] = n
            data.append(v)
            print n, '\r',
            n += 1
        print 'done'

    g.add_vertex(n)
    for i, row in enumerate(data):
        taxid = row[0]
        parent = row[1]
        name = row[2]
        rank = row[3]
        sinfo = row[4]
        try:
            d = dict([ (x or '').split(':') for x in (sinfo or '').split(',') ])
            ncbi = int(d.get('ncbi') or 0)
            gbif = int(d.get('gbif') or 0)
            silva = d.get('silva')
            irmng = int(d.get('irmng') or 0)
        except ValueError:
            ncbi = gbif = irmng = 0
        uniqname = row[5]
        flags = row[6]

        v = g.vertex(i)
        g.vertex_taxid[v] = taxid
        g.vertex_name[v] = name
        if uniqname: g.vertex_unique_name[v] = uniqname
        if rank: g.vertex_rank[v] = rank
        if ncbi: g.vertex_ncbi[v] = ncbi
        if gbif: g.vertex_gbif[v] = gbif
        if silva: g.vertex_silva[v] = silva
        if irmng: g.vertex_irmng[v] = irmng
        if flags: g.vertex_flags[v] = flags
        g.vertex_in_taxonomy[v] = 1
        g.taxid_vertex[taxid] = v

        #if row[-1] and 'D' in row[-1]: g.dubious[v] = 1

        if parent:
            pv = g.vertex(taxid2vid[parent])
            e = g.add_edge(pv, v)
            g.edge_in_taxonomy[e] = 1
        print i, '\r',
    print 'done'

    _filter(g)
    index_graph(g)
    _attach_funcs(g)

    g.root = g.vertex(0)
    return g

g = create_taxonomy_graph()
g.save('ott24.xml.gz')

## # map uids to dictionaries of row data
## uid2row = {}
## with open(dump_path) as f:
##     fields = split(f.next())
##     UID = fields.index('uid')
##     NAME = fields.index('name')
##     UNIQNAME = fields.index('uniqname')
##     for row in imap(split, f):
##         uid = int(row[UID])
##         row = [ x or None for x in row ]
##         d = dict(zip(fields, row))
##         sinfo = d.get('sourceinfo')
##         if sinfo:
##             sd = dict([ (x or '').split(':')
##                         for x in (sinfo or '').split(',') ])
##             ncbi = int(sd.get('ncbi') or 0) or None
##             gbif = int(sd.get('gbif') or 0) or None
##         else:
##             ncbi = gbif = None
##         d['ncbi_taxid'] = ncbi; d['gbif_taxid'] = gbif
##         del d['sourceinfo']
##         uid2row[uid] = d

uname2uid = {}
for v in g.vertices():
    n = g.vertex_unique_name[v] or g.vertex_name[v]
    assert n not in uname2uid, n
    uname2uid[n] = g.vertex_taxid[v]

uid2syn = defaultdict(list)
with open(os.path.join(dump_loc,'synonyms.tsv')) as f:
    f.next()
    for name, uid, typ, uniqname in imap(split, f):
        uid = int(uid)
        uid2syn[uid].append((name, uniqname))
        if uniqname not in uname2uid:
            uname2uid[uniqname] = uid
        else:
            print 'non-unique name:', uniqname, uid, uname2uid[uniqname]

insert = open('insert.sql','w')
update = open('update.sql','w')
delete = []
uids_seen = set()
unique_names_seen = set()
with open('ottol_name.csv') as f:
    fields = f.next().strip().split('\t')
    NAME = fields.index('name')
    UNIQUE_NAME = fields.index('unique_name')

    def write_update(sqlid, uid, unique_name):
        v = g.taxid_vertex[uid]
        nxt, bck = g.hindex[v]
        d = {}
        ## d['id'] = sqlid
        d['accepted_uid'] = uid
        d['name'] = g.vertex_name[v]
        d['unique_name'] = unique_name
        d['next'] = nxt; d['back'] = bck
        d['ncbi_taxid'] = g.vertex_ncbi[v] or None
        d['gbif_taxid'] = g.vertex_gbif[v] or None
        d['rank'] = g.vertex_rank[v] or None

        s = 'update ottol_name set %s where id = %s;'
        u = []
        for k,v in d.items():
            if v is not None:
                if isinstance(v,(str,unicode)):
                    v = v.replace('"', r'\"').replace("'", r"\'")
                    v = '"%s"' % v
                u.append('%s = %s' % (k,v))
        s = s % (', '.join(u), sqlid)
        update.write('%s\n' % s)

    for s in f:
        v = s.strip().split('\t')
        sqlid = int(v[0])

        uid = int(v[3] or 0)
        if uid: uids_seen.add(uid)

        unique_name = v[UNIQUE_NAME]
        if unique_name in uname2uid:
            unique_names_seen.add(unique_name)

        # delete rows that are deprecated and not used
        if uid and uid in deprecated and sqlid not in used_sqlids:
            delete.append(sqlid)
            continue

        # delete rows that have no uid and are not used
        if (not uid) and (sqlid not in used_sqlids):
            delete.append(sqlid)
            continue

        # used name, no uid, in OTT; can be updated
        if (not uid) and (sqlid in used_sqlids) and uname2uid.get(unique_name):
            uid = uname2uid[unique_name]
            try: write_update(sqlid, uid, unique_name)
            except ValueError:
                if sqlid not in used_sqlids:
                    uids_seen.remove(uid)
                    unique_names_seen.remove(unique_names_seen)
                    delete.append(sqlid)
            continue

        # update rows where uid and unique_name match OTT
        if (unique_name and (unique_name in uname2uid) and uid
            and uname2uid[unique_name] == uid):
            try: write_update(sqlid, uid, unique_name)
            except ValueError:
                if sqlid not in used_sqlids:
                    uids_seen.remove(uid)
                    unique_names_seen.remove(unique_name)
                    delete.append(sqlid)
            continue

        if sqlid not in used_sqlids:
            delete.append(sqlid)

with open('delete.sql','w') as f:
    f.write('delete from ottol_name where id in (%s);' %
            ','.join(map(str, sorted(set(delete)))))

for v in g.vertices():
    uid = g.vertex_taxid[v]
    d = {}
    if uid not in uids_seen:
        nxt, bck = g.hindex[v]
        d['uid'] = uid
        d['accepted_uid'] = uid
        d['name'] = g.vertex_name[v]
        d['unique_name'] = g.vertex_unique_name[v] or g.vertex_name[v]
        d['next'] = nxt; d['back'] = bck
        d['ncbi_taxid'] = g.vertex_ncbi[v] or None
        d['gbif_taxid'] = g.vertex_gbif[v] or None
        d['rank'] = g.vertex_rank[v] or None

        s = 'insert into ottol_name (%s) values (%s);'
        flds = []; vals = []
        for k,v in d.items():
            if v is not None:
                flds.append(k)
                if isinstance(v,(str,unicode)):
                    v = v.replace('"', r'\"').replace("'", r"\'")
                    v = '"%s"' % v
                vals.append(v)
        s = s % (', '.join(flds), ', '.join(map(str, vals)))
        insert.write('%s\n' % s)

for uid, syns in uid2syn.iteritems():
    for name, uname in syns:
        if uname not in unique_names_seen:
            v = g.taxid_vertex[uid]
            #assert v
            d = {}
            try:
                nxt, bck = g.hindex[v]
            except ValueError:
                continue
            d['uid'] = uid
            d['accepted_uid'] = uid
            d['name'] = name
            d['unique_name'] = unique_name
            d['next'] = nxt; d['back'] = bck
            d['ncbi_taxid'] = g.vertex_ncbi[v] or None
            d['gbif_taxid'] = g.vertex_gbif[v] or None
            d['rank'] = g.vertex_rank[v] or None

            s = 'insert into ottol_name (%s) values (%s);'
            flds = []; vals = []
            for k,v in d.items():
                if v is not None:
                    flds.append(k)
                    if isinstance(v,(str,unicode)):
                        v = v.replace('"', r'\"')
                        v = '"%s"' % v
                    vals.append(v)
            s = s % (', '.join(flds), ', '.join(map(str, vals)))
            insert.write('%s\n' % s)
    
insert.close(); update.close()

######################################################
name2none = {}
for r in db(t.uid==None).select():
    name2none[r.unique_name] = r
print 'names without uids:', len(name2none)

## with open('/tmp/synonym-multiple-uids.txt','w') as f:
##     for k, v in sorted(syn2uid.items()):
##         if len(v)>1: f.write('%s\t%s\n' % (k, sorted(v)))

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
