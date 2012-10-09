"""
module for building trees of ivy.tree.Nodes from database tables
"""
from ivy.tree import Node, index
from collections import defaultdict

## def root_taxon(db):
##     "return the root taxon record for taxon table"
##     t = db.taxon
##     q = (t.parent==None)
##     v = db(q).select()
##     assert len(v)==1
##     return v[0]

def root_snode(db, tree):
    "return the root snode record for stree id 'tree'"
    t = db.snode
    q = (t.tree==tree)&(t.next==1)
    v = db(q).select()
    assert len(v)==1
    return v[0]

def leaves(t, rec):
    db = t._db
    q = (t.next>rec.next)&(t.back<rec.back)&(t.next==t.back-1)
    return list(db(q).select(orderby=t.next))

def mrca(t, recs):
    db = t._db
    n = min([ x.next for x in recs ])
    b = max([ x.back for x in recs ])
    q = (t.next<n)&(t.back>b)
    return db(q).select(orderby=t.back,limitby=(0,1)).first()

def stree(db, i, lim=0, maxdepth=None):
    "build a tree of ivy.tree.Nodes for db.stree.id==i"
    t = db.snode
    q = t.tree==i
    r = root_snode(db, i)
    root = nextbacktree(db.snode, r.id, q, lim=lim, maxdepth=maxdepth)
    for n in root:
        n.label = n.rec.label
    return root

def snode2tree(db, i, q=None, lim=0, maxdepth=None):
    """
    build a tree of ivy.tree.Nodes from root db.snode.id==i,
    filtered by query q
    """
    t = db.snode
    r = t[int(i)]
    if q: q &= (t.tree==r.tree)
    else: q = (t.tree==r.tree)
    root = nextbacktree(db.snode, r.id, q, lim=lim, maxdepth=maxdepth)
    for n in root:
        n.label = n.rec.label
    return root

def gnode2tree(db, i, q=None, lim=0, maxdepth=None):
    """
    build a tree of ivy.tree.Nodes from root db.snode.id==i,
    filtered by query q
    """
    t = db.gnode
    r = t[int(i)]
    if q: q &= (t.tree==r.tree)
    else: q = (t.tree==r.tree)
    root = nextbackgtree(db.gnode, r.id, q, lim=lim, maxdepth=maxdepth)
    for n in root:
        n.label = n.rec.label
    return root

## def taxa2tree(db, i, lim=0, maxdepth=None):
##     root = nextbacktree(db.taxon, i, lim=lim, maxdepth=maxdepth)
##     for n in root:
##         n.label = n.rec.name
##     return root

def ncbi2tree(db, i, lim=0, maxdepth=None):
    root = nextbacktree(db.ncbi_taxon, i, lim=lim, maxdepth=maxdepth)
    for n in root:
        n.label = n.rec.name
    return root

def nextbacktree(t, i, q=None, lim=0, maxdepth=None):
    """
    create a tree of ivy.tree.Nodes from table t, with
    records having fields next, back, parent, and depth
    """
    db = t._db
    r = t[int(i)]
    limits = dict(orderby=t.next)
    if lim: limits["limitby"] = (0,lim)
    q2 = (t.next>r.next)&(t.back<r.back)
    if maxdepth:
        q2 &= (t.depth <= maxdepth)
    recs = db(q)(q2).select(**limits)
    
    #Node = ivy.tree.Node
    root = Node(); root.isroot = True
    root.rec = r; root.id = r.id

    i2n = {}; i2n[r.id] = root
    for r in recs:
        n = Node()
        n.rec = r; n.id = r.id; n.next = r.next; n.back = r.back
        if (((not maxdepth) and (r.next==r.back-1)) or
            (maxdepth and (n.depth == maxdepth))):
            n.isleaf = True
        i2n[r.id] = n
        i2n[r.parent].add_child(n)
    return root

def nextbackgtree(t, i, q=None, lim=0, maxdepth=None):
    """
    create a tree of ivy.tree.Nodes from table t, with
    records having fields next, back, parent, and depth
    """
    db = t._db
    r = t[int(i)]
    limits = dict(orderby=t.next)
    if lim: limits["limitby"] = (0,lim)
    q2 = (t.next>r.next)&(t.back<r.back)
    if maxdepth:
        q2 &= (t.depth <= maxdepth)
    recs = db(q)(q2).select(**limits)
   
    #Node = ivy.tree.Node
    root = Node(); root.isroot = True
    root.rec = r; root.id = r.id; root.next = r.next; root.back = r.back; root.stree = r.stree; root.snode = r.snode 

    i2n = {}; i2n[r.id] = root

    for r in recs:
    
        n = Node()

        if( not hasattr( r, 'id' ) ):
            r = r.gnode

        n.rec = r; n.id = r.id; n.next = r.next; n.back = r.back; n.stree = r.stree; n.snode = r.snode
        if (((not maxdepth) and (r.next==r.back-1)) or
            (maxdepth and (n.depth == maxdepth))):
            n.isleaf = True
        i2n[r.id] = n
        i2n[r.parent].add_child(n)
    return root

def add_child(t, parent, child):
    """
    'parent' and 'child' are assumed to be ivy.tree.Nodes with 'rec'
    attributes
    """
    db = t._db
    
    child_next = parent.back
    
    pass

## def prune(t, rec):
##     "for a tree table with next, back and parent fields, prune a subtree"
##     db = t._db
##     assert rec.parent
##     parent = t[rec.parent]
##     ## children = db(t.parent==parent.id).select(orderby=t.next)

def recurse(table, rec, d=None):
    """
    recursively create a tree of ivy.tree.Nodes from table, with root
    rec, using parent references only
    """
    db = table._db
    isroot = False
    if not d:
        d = defaultdict(list)
        isroot = True
    children = db(table.parent==rec.id).select()
    for c in children:
        recurse(table, c, d)
        d[rec.id].append(c)
    if isroot:
        r = ivy.tree.Node(); r.isroot=True; r.rec = rec
        r.label = rec.name
        def f(n):
            for x in d[n.id]:
                c = ivy.tree.Node(); c.rec = x; c.label = x.name
                n.add_child(c)
                f(c)
        f(r)
        for x in r:
            if not x.children:
                x.isleaf = True
        return r

def gtree(db, i, lim=0, maxdepth=None):
    "build a tree of ivy.tree.Nodes for db.gtree.id==i"
    t = db.gnode
    q = ( t.tree==i ) & ( t.pruned == False )
    r = root_gnode(db, i)
    root = nextbackgtree(db.gnode, r.id, q, lim=lim, maxdepth=maxdepth)
    for n in root:
        n.label = n.rec.label
    return root

def root_gnode(db, tree):
    "return the root gnode record for stree id 'tree'"
    t = db.gnode
    q = (t.tree==tree)&(t.next==1)
    v = db(q).select()
    assert len(v)==1
    return v[0]

def rootpath(t, r, q=None, d=None):
    "return a list of records leading up to record 'r'"
    db = t._db
    q2 = (t.next<r.next)&(t.back>r.back)
    return list(db(q)(q2).select(orderby=~t.next))

def children(t, r):
    db = t._db
    return list(db(t.parent==r.id).select(orderby=t.next))

def insert_child(t, r, data):
    db = t._db
    b = r.back; d = r.depth; pid = r.id
    db(t.back>=b).update(back=t.back+2)
    db(t.next>b).update(next=t.next+2)
    data['next'] = b
    data['back'] = b+1
    data['depth'] = d+1
    data['parent'] = pid
    return t.insert(**data)

def delete_subtree(t, r):
    db = t._db
    n = r.next; b = r.back
    w = b-n+1
    parent = t(r.parent)
    q = (t.next>=n)&(t.back<=b)
    ## c = db(q).count()
    db(q).delete()
    db(t.back>b).update(back=t.back-w)
    db(t.next>b).update(next=t.next-w)
    return parent

def move_subtree(t, r, parent):
    db = t._db
    n = r.next; b = r.back;
    w = b-n+1
    q = (t.next>=n)&(t.back<=b)
    subtree = db(q).select(t.id)
    db(t.back>b).update(back=t.back-w)
    db(t.next>b).update(next=t.next-w)
    p = t(parent.id)
    db((t.back>=p.back)&(~t.id.belongs(subtree))).update(back=t.back+w)
    db((t.next>p.back)&(~t.id.belongs(subtree))).update(next=t.next+w)
    delta = t(parent.id).back - b
    delta_depth = p.depth - r.depth + 1
    r.update_record(parent=parent)
    db(t.id.belongs(subtree)).update(next=t.next+delta-1, back=t.back+delta-1,
                                     depth=t.depth+delta_depth)

def descendants(t, r):
    db = t._db
    q = (t.next>=r.next)&(t.back<=r.back)
    return list(db(q).select(orderby=t.next))

def print_nodes(t, r):
    db = t._db
    q = (t.next>=r.next)&(t.back<=r.back)
    for n in db(q).select(orderby=t.next):
        print '%s%s (%s) [%s,%s]' % ('  '*(n.depth-r.depth), n.name, n.id,
                                     n.next, n.back)

def reindex_from_parents(t):
    db = t._db
    rec2node = dict([ (rec.id, Node(rec=rec, isleaf=True)) for rec in
                      db(t.id>0).select() ])
    root = None
    for r, n in rec2node.items():
        if n.rec.parent is not None:
            p = rec2node[n.rec.parent]
            p.add_child(n)
            p.isleaf = False
        else:
            root = n
    index(root)
    for n in root: n.rec.update_record(next=n.next, back=n.back, depth=n.depth)
    return root
