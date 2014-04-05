import ivy_local as ivy

def mrca(t, tids):
    db = t._db
    q = "select min(next), max(back) from {} where id in ({})".format(
        t._tablename, ','.join([ str(x) for x in tids ]))
    min_next, max_back = db.executesql(q)[0]
    q = (t.next<min_next)&(t.back>max_back)
    return db(q).select(orderby=t.back,limitby=(0,1)).first()

def subtree(t, tids):
    """
    return an ivy tree (root node) representing the taxonomy subtree having
    tids (list of taxon uids) at its tips
    """
    db = t._db
    Node = ivy.tree.Node
    q = "select next, back from {} where id in ({}) order by next asc".format(
        t._tablename, ','.join([ str(x) for x in tids ]))
    v = db.executesql(q)
    q = "select id, parent, name from ott_node where ({}) order by next asc"
    v = [ "(next <= {} and back >= {})".format(nxt, bck) for nxt, bck in v ]
    q = q.format(" or ".join(v))
    rows = db.executesql(q)
    nodes = [ Node(id=i, pid=p, name=n, label=n) for i, p, n in rows ]
    nodes[0].isroot = True
    id2node = dict([ (n.id, n) for n in nodes ])
    for n in nodes[1:]: id2node[n.pid].add_child(n)
    for n in nodes:
        if not n.children: n.isleaf = True
    
