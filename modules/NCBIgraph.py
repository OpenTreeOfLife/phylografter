import build
from collections import defaultdict
from pprint import pprint

def connect(uri='http://localhost:7474/db/data/'):
    from bulbs.neo4jserver import Graph, Vertex, ExactIndex
    from bulbs.config import Config
    config = Config(uri)
    config.autoindex = False
    G = Graph(config)
    G.ncbi_node_idx = G.factory.get_index(Vertex, ExactIndex, 'ncbi_node')
    G.ncbi_name_idx = G.factory.get_index(Vertex, ExactIndex, 'ncbi_name')
    stree = G.vertices.index.get_unique(proxy='stree')
    if not stree:
        stree = G.vertices.create(proxy='stree')
        G.vertices.index.put(stree.eid, proxy='stree')
    G.stree = stree
    return G

def get_ncbi_node(G, leaf):
    label = leaf.rec.label
    if leaf.rec.ottol_name:
        if leaf.rec.ottol_name.ncbi_taxid:
            taxid = str(leaf.rec.ottol_name.ncbi_taxid)
            return G.ncbi_node_idx.get_unique(taxid=taxid)
        else:
            label = leaf.rec.ottol_name.name
    name = label.replace('_', ' ')
    if G.ncbi_name_idx.count(name=name) == 1:
        return G.ncbi_name_idx.get_unique(name=name).outV('NCBI_NAME_OF').next()

def ncbi_subtree(G, leaves, fetchnodes=True):
    import NCBIscripts as scripts
    eid2n = dict([ (x.eid, x) for x in leaves ])
    leafids = eid2n.keys()
    d = G.gremlin.execute(scripts.ncbi_subtree, dict(leafids=leafids)).content
    nodes = dict([ (x, build.Node(isleaf=True, eid=x)) for x in leafids ])
    for k,(e,(v,)) in d.items():
        k = int(k)
        c = nodes.get(k) or build.Node(eid=k)
        c.edge_eid = e
        p = nodes.get(v) or build.Node(eid=v, edge_eid=None)
        p.add_child(c)
        nodes[c.eid] = c; nodes[p.eid] = p
    root = None
    for n in nodes.values():
        if fetchnodes:
            n.ncbi_node = eid2n.get(n.eid) or G.vertices.get(n.eid)
            n.label = n.ncbi_node.name
        if not n.parent:
            n.isroot = True
            root = n
    while len(root.children)==1: root = root.children[0]
    root.parent = None
    return root

def leaf_eids(root):
    d = defaultdict(list)
    for n in root.postiter():
        if n.isleaf and n.ncbi_node:
            n.leaf_eids = frozenset([n.ncbi_node.eid])
        else:
            if len(n.children)==1: n.leaf_eids = n.children[0].leaf_eids
            else: n.leaf_eids = reduce(
                lambda a,b:a|b, [ x.leaf_eids for x in n.children ])
        d[n.leaf_eids].append(n)
    return d

def map_taxonomy(G, root):
    for lf in root.leaves(): lf.ncbi_node = get_ncbi_node(G, lf)
    leaves = [ x.ncbi_node for x in root.leaves() if x.ncbi_node ]
    leaf_eids(root)
    taxroot = ncbi_subtree(G, leaves)
    leafset2taxnodes = leaf_eids(taxroot)

    nodes = list(root.postiter())
    for n in nodes:
        n.ncbi_node = None
        n.conflicts = []
        v = leafset2taxnodes.get(n.leaf_eids)
        if v:
            taxnode = v[0]
            n.eid = taxnode.eid
            n.edge_eid = taxnode.edge_eid
            n.ncbi_node = taxnode.ncbi_node
            n.label = taxnode.ncbi_node.name
            ref = n
            for taxnode in v[1:]:
                newnode = build.Node(rec=n.rec, conflicts=[], type='snode',
                                     edge_eid=taxnode.edge_eid,
                                     ncbi_node=taxnode.ncbi_node,
                                     label=taxnode.ncbi_node.name,
                                     leaf_eids=ref.leaf_eids)
                p = ref.prune()
                newnode.add_child(ref)
                p.add_child(newnode)
                ref = newnode
        else:
            # this clade cannot be assigned to any taxon
            # does it conflict with any taxa?
            s1 = n.leaf_eids
            for t in taxroot:
                s2 = t.leaf_eids
                if (not s1.isdisjoint(s2) and not s1.issubset(s2)
                    and not s1.issuperset(s2)):
                    n.conflicts.append(t.ncbi_node)

def taxhash(n):
    def collect_taxa(n):
        v = []
        def traverse(x):
            for c in x.children:
                if c.ncbi_node: v.append(c.ncbi_node)
                else: traverse(c)
        traverse(n)
        return v
    v = [ str(i) for i in sorted([ x.taxid for x in collect_taxa(n) ]) ]
    return '|%s|' % '|'.join(v)

def insert_mapped_stree(G, root):
    created_nodes = []
    created_edges = []
    for n in root:
        if n.ncbi_node:
            vtx = n.ncbi_node
        else:
            k = taxhash(n)
            vtx = G.vertices.index.get_unique(ingroup=k)
            if not vtx:
                vtx = G.vertices.create(type='snode', ingroup=k)
                G.vertices.index.put(vtx.eid, ingroup=k)
                print 'created snode', vtx.eid
                created_nodes.append(vtx)

        stree = vtx.get('stree')
        if not stree: stree = [n.rec.tree]
        else:
            i = n.rec.tree
            if i not in stree: stree.append(i)
        snode = vtx.get('snode')
        if not snode: snode = [n.rec.id]
        else:
            i = n.rec.id
            if i not in snode: snode.append(i)

        vtx.stree=stree
        vtx.snode=snode
        vtx.save()
        n.vtx = vtx

        if n.parent:
            e = [ x for x in vtx.outE('SNODE_CHILD_OF') or []
                  if x._inV == n.parent.vtx.eid ]
            if e:
                e = e[0]
            else:
                e = G.edges.create(vtx, 'SNODE_CHILD_OF', n.parent.vtx,
                                   stree=[n.rec.tree], snode=[n.rec.id])
                print 'created SNODE_CHILD_OF', e._outV, e.eid, e._inV
                created_edges.append(e)
            e.stree=stree
            e.snode=snode
            e.save()

            G.edges.index.put(e.eid, stree=n.rec.tree)
            G.edges.index.put(e.eid, snode=n.rec.id)
        for c in n.conflicts:
            e = G.edges.create(vtx, 'CONFLICTS_WITH', c,
                               stree=n.rec.tree, snode=n.rec.id)
            G.edges.index.put(e.eid, stree_conflicts=n.rec.tree)
            print 'created CONFLICTS_WITH', e._outV, e.eid, e._inV
            created_edges.append(e)
        
    G.edges.create(G.stree, 'ROOT', root.vtx, stree=root.rec.tree)
    return created_nodes, created_edges

def stree_subgraph(G, stree_id):
    import graph_tool.all as gt
    from ivy import layout_polar
    from ivy.tree import Node
    edges = G.edges.index.lookup(stree=stree_id)
    sg = gt.Graph() # graph-tool graph representing subgraph of G
    sg.etype = sg.new_edge_property("string")
    sg.vcolor = sg.new_vertex_property("string")
    sg.vtext = sg.new_vertex_property("string")
    sg.ecolor = sg.new_edge_property("string")
    sg.ewidth = sg.new_edge_property("int")
    sg.eweight = sg.new_edge_property("int")
    sg.stree = sg.new_edge_property("bool")
    pos = sg.new_vertex_property("vector<double>")
    pin = sg.new_vertex_property("bool")
    eid2vtx = {} # map G vertex eids to G vertices
    eid2sgv = {} # map G vertex eids to subgraph vertices
    eid2sge = {} # map G edge eids to subgraph edges
    eid2n = {} # map G vertex eids to stree nodes
    se_created = set()
    leaves = []
    c2p = {}
    # build the subgraph
    for e in edges:
        # get/create+store subgraph vertices
        osgv = eid2sgv.get(e._outV) or sg.add_vertex()
        eid2sgv[e._outV] = osgv
        pin[osgv] = True
        isgv = eid2sgv.get(e._inV) or sg.add_vertex()
        eid2sgv[e._inV] = isgv
        pin[isgv] = True

        # get/fetch+store G vertices
        ovtx = eid2vtx.get(e._outV) or e.outV()
        eid2vtx[e._outV] = ovtx
        if not [ x for x in ovtx.inE('SNODE_CHILD_OF') or []
                 if stree_id in (x.get('stree') or []) ]:
            leaves.append(ovtx)
        ivtx = eid2vtx.get(e._inV) or e.inV()
        eid2vtx[e._inV] = ivtx

        # create subgraph edges
        se = sg.add_edge(osgv, isgv)
        eid2sge[e.eid] = se
        se_created.add((e._outV, e._inV))
        sg.etype[se] = e.label()
        sg.ecolor[se] = 'green'
        sg.ewidth[se] = 4
        sg.eweight[se] = 4
        sg.stree[se] = True

        c = eid2n.get(ovtx.eid) or Node(vtx=ovtx, sgv=osgv)
        eid2n[ovtx.eid] = c
        p = eid2n.get(ivtx.eid) or Node(vtx=ivtx, sgv=isgv)
        eid2n[ivtx.eid] = p
        p.add_child(c)
        c2p[c] = p

    root = None
    for c, p in c2p.items():
        if not p.parent:
            p.isroot = True
            root = p
        if not c.children: c.isleaf = True
    n2c = layout_polar.calc_node_positions(root, radius=1000)
    for n in root:
        k = n.sgv; v = n2c[n]
        pos[k] = [v.x, v.y]

    for eid, sgv in eid2sgv.items():
        vtx = eid2vtx[eid]
        if vtx.get('name'):
            sg.vcolor[sgv] = 'blue'
            sg.vtext[sgv] = vtx.name
        else: sg.vcolor[sgv] = 'green'

    taxtree = ncbi_subtree(G, leaves, fetchnodes=False)
    for n in taxtree:
        if n.parent:
            osgv = eid2sgv.get(n.eid)
            if not osgv:
                osgv = sg.add_vertex()
                sg.vcolor[osgv] = 'red'
                ovtx = G.vertices.get(n.eid)
                sg.vtext[osgv] = ovtx.name
                eid2sgv[n.eid] = osgv
                eid2vtx[n.eid] = ovtx
                pos[osgv] = [0.0, 0.0]
                pin[osgv] = False
            isgv = eid2sgv.get(n.parent.eid)
            if not isgv:
                isgv = sg.add_vertex()
                sg.vcolor[isgv] = 'red'
                ivtx = G.vertices.get(n.eid)
                sg.vtext[isgv] = ivtx.name
                eid2sgv[n.parent.eid] = isgv
                eid2vtx[n.parent.eid] = ivtx
                pos[isgv] = [0.0, 0.0]
                pin[isgv] = False
                
            ## if not (n.eid, n.parent.eid) in se_created:
            if not n.edge_eid in eid2sge:
                se = sg.add_edge(osgv, isgv)
                eid2sge[n.edge_eid] = se
                sg.ecolor[se] = 'blue'
                sg.ewidth[se] = 1
                sg.eweight[se] = 0
                sg.stree[se] = False
                se_created.add((n.eid, n.parent.eid))
    return sg

def draw_stree_subgraph(sg):
    sg.set_edge_filter(sg.stree)
    p1 = gt.sfdp_layout(sg, p=1.5, pos=pos)
    sg.stash_filter()
    p2 = gt.sfdp_layout(sg,
                        p=1.5,
                        ## C=1.0,
                        ## theta=1.2,
                        pin=pin, pos=p1)
    sg.set_reversed(True)
    gt.graph_draw(sg, pos=p2,
                  vertex_fill_color=sg.vcolor, vertex_text=sg.vtext,
                  vertex_text_position=0, edge_color=sg.ecolor,
                  edge_pen_width=sg.ewidth, sg.eweight=sg.eweight,
                  font_size=10)


G = connect()
rec = db.stree(3)
root = build.stree(db, rec.id)
map_taxonomy(G, root)
newnodes, newedges = insert_mapped_stree(G, root)
stree_subgraph(G, 3)

#g = new Neo4jGraph('/home/rree/ncbitax/phylografter.db')
