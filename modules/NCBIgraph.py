import build
import graph_tool.all as gt
import NCBIscripts as scripts
from collections import defaultdict, Counter
from itertools import ifilter
from bulbs.neo4jserver import Graph, Vertex, ExactIndex
from pprint import pprint

def connect(uri='http://localhost:7474/db/data/'):
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

def stree_inserted(G, stree_id):
    return G.edges.index.count(stree=stree_id) > 0

def fetch_stree_root(G, stree_id):
    q = "g.v(n).outE.and(_().has('stree', T.eq, i)).outV"
    x = G.gremlin.query(q, dict(n=G.stree.eid, i=stree_id))
    if x: return x.next()

def inserted_strees(G):
    ## q = "g.v(n).outE.stree"
    ## return G.gremlin.execute(q, dict(n=G.stree.eid)).content
    return [ x.stree for x in (G.stree.outE() or []) ]

def ncbi_subtree(G, leaves, fetchnodes=True):
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

def map_taxonomy(G, root):
    def leaf_eids(root):
        d = defaultdict(list)
        for n in root.postiter():
            if n.isleaf:
                if n.ncbi_node: n.leaf_eids = frozenset([n.ncbi_node.eid])
                else: n.leaf_eids = frozenset()
            else:
                if len(n.children)==1: n.leaf_eids = n.children[0].leaf_eids
                else: n.leaf_eids = reduce(
                    lambda a,b:a|b, [ x.leaf_eids for x in n.children ])
            d[n.leaf_eids].append(n)
        return d

    def get_ncbi_node(leaf):
        label = leaf.rec.label
        if leaf.rec.ottol_name:
            if leaf.rec.ottol_name.ncbi_taxid:
                taxid = str(leaf.rec.ottol_name.ncbi_taxid)
                return G.ncbi_node_idx.get_unique(taxid=taxid)
            else:
                label = leaf.rec.ottol_name.name
        name = label.replace('_', ' ')
        ambig = G.ncbi_name_idx.lookup(name=name) or []
        if ambig:
            v = [ x.outV('NCBI_NAME_OF').next() for x in ambig ]
            if len(v)==1: return v[0]
            else: return v

    lvs = root.leaves()
    unmapped = []; ambig = []
    for lf in lvs:
        lf.ncbi_node = get_ncbi_node(lf)
        if not lf.ncbi_node: unmapped.append(lf)
        elif not isinstance(lf.ncbi_node, Vertex): ambig.append(lf)
        else: pass
    leaves = [ x.ncbi_node for x in lvs
               if x.ncbi_node and isinstance(x.ncbi_node, Vertex) ]
    taxroot = ncbi_subtree(G, leaves)
    ## print 'taxroot 1', taxroot.ncbi_node.name, taxroot.ncbi_node.taxid
    if ambig:
        for lf in ambig:
            print 'ambig', lf
            found = None
            for n in lf.ncbi_node:
                anc = taxroot.ncbi_node
                params = dict(n=n.eid, anc=anc.eid)
                if G.gremlin.execute(scripts.rootpath, params).content:
                    print 'found %s (%s) in %s' % (n.name, n.taxid, anc.name)
                    found = n
                    break
            if found: lf.ncbi_node = found
            else: lf.ncbi_node = None
        leaf_eids(root)
        leaves = [ x.ncbi_node for x in lvs if x.ncbi_node ]
        taxroot = ncbi_subtree(G, leaves)
        ## print 'taxroot 2', taxroot.ncbi_node.name, taxroot.ncbi_node.taxid
    unmapped = [ x for x in lvs if not x.ncbi_node ]
    assert (not unmapped), unmapped
    v = [ x.eid for x in leaves ]
    assert len(v)==len(set(v)), 'multiple tips, same taxon not implemented yet'
    leaf_eids(root)
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

def insert_stree(G, stree_id):
    assert not stree_inserted(G, stree_id)
    r = build.stree(db, stree_id)
    map_taxonomy(G, r)
    newnodes, newedges = insert_mapped_stree(G, r)
    return r

def stree_subgraph(G):
    sg = gt.Graph() # graph-tool graph representing subgraph of G
    sg.eid2vtx = {} # map G vertex eids to G vertices
    sg.eid2sgv = {} # map G vertex eids to subgraph vertices
    sg.eid2sge = {} # map G edge eids to subgraph edges
    sg.eid2n = {} # map G vertex eids to stree nodes
    sg.eid2leaf = {} # map G vertex eids to stree leaves
    sg.stree = {} # map stree_id to root (ivy) node
    sg.sgv2vtx = {} # map sg vertices to G vertices
    sg.ncbi_color = 'blue'
    sg.snode_overlap_color = 'yellow'
    sg.vtext = sg.new_vertex_property("string")
    sg.isleaf = sg.new_vertex_property("bool")
    sg.snode = sg.new_vertex_property("bool")
    sg.snode_edge = sg.new_edge_property("bool")
    sg.ncbi_node = sg.new_vertex_property("bool")
    sg.ncbi_edge = sg.new_edge_property("bool")
    sg.edge2stree = sg.new_edge_property("int")
    sg.se_created = set()
    sg.vtx_leaves = []
    sg.root = None

    def add(stree_id):
        c2p = {}
        sg.eid2n[stree_id] = {}
        sg.eid2leaf[stree_id] = {}
        # build the subgraph
        edges = G.edges.index.lookup(stree=stree_id)
        assert edges
        for e in edges:
            # get/create+store subgraph vertices
            osgv = sg.eid2sgv.get(e._outV)
            if not osgv:
                osgv = sg.add_vertex()
                sg.eid2sgv[e._outV] = osgv
            sg.snode[osgv] = 1
            sg.ncbi_node[osgv] = 0

            isgv = sg.eid2sgv.get(e._inV)
            if not isgv:
                isgv = sg.add_vertex()
                sg.eid2sgv[e._inV] = isgv
            sg.snode[isgv] = 1
            sg.ncbi_node[isgv] = 0

            # get/fetch+store G vertices
            ovtx = sg.eid2vtx.get(e._outV) or e.outV()
            sg.vtext[osgv] = ovtx.get('name') or ''
            sg.isleaf[osgv] = 0
            sg.eid2vtx[e._outV] = ovtx
            sg.sgv2vtx[osgv] = ovtx
            ivtx = sg.eid2vtx.get(e._inV) or e.inV()
            sg.vtext[isgv] = ivtx.get('name') or ''
            sg.isleaf[isgv] = 0
            sg.eid2vtx[e._inV] = ivtx
            sg.sgv2vtx[isgv] = ivtx

            # is ovtx a leaf?
            if not [ x for x in ovtx.inE('SNODE_CHILD_OF') or []
                     if stree_id in (x.get('stree') or []) ]:
                sg.isleaf[osgv] = 1
                sg.vtx_leaves.append(ovtx)
                sg.eid2leaf[stree_id][e._outV] = osgv

            # create subgraph edges
            se = sg.add_edge(osgv, isgv)
            sg.se_created.add((ovtx.eid, ivtx.eid))
            sg.eid2sge[e.eid] = se
            sg.snode_edge[se] = 1
            sg.ncbi_edge[se] = 0
            assert not sg.edge2stree[se]
            sg.edge2stree[se] = stree_id

            c = (sg.eid2n[stree_id].get(ovtx.eid) or
                 build.Node(vtx=ovtx, sgv=osgv))
            sg.eid2n[stree_id][ovtx.eid] = c
            c.sge = se
            p = (sg.eid2n[stree_id].get(ivtx.eid) or
                 build.Node(vtx=ivtx, sgv=isgv))
            sg.eid2n[stree_id][ivtx.eid] = p
            p.add_child(c)
            c2p[c] = p

        for c, p in c2p.items():
            if not p.parent:
                p.isroot = True
                p.sge = None
                sg.stree[stree_id] = p
            if not c.children: c.isleaf = True
        assert sg.stree.get(stree_id)

        if not sg.root: sg.root = sg.stree[stree_id]
        else:
            params = dict(anc=sg.stree[stree_id].vtx.eid, n=sg.root.vtx.eid)
            if G.gremlin.execute(scripts.rootpath, params).content:
                sg.root = sg.stree[stree_id]
                ## print ('setting new sg root to', sg.stree[stree_id],
                ##        sg.vtext[sg.stree[stree_id].sgv] or '')

        taxtree = ncbi_subtree(G, sg.vtx_leaves, fetchnodes=False)
        for n in taxtree:
            if n.parent:
                osgv = sg.eid2sgv.get(n.eid)
                if not osgv:
                    osgv = sg.add_vertex()
                    ovtx = G.vertices.get(n.eid)
                    sg.sgv2vtx[osgv] = ovtx
                    sg.eid2sgv[n.eid] = osgv
                    sg.eid2vtx[n.eid] = ovtx
                    sg.ncbi_node[osgv] = 1
                    sg.vtext[osgv] = ovtx.name
                    sg.snode[osgv] = 0
                isgv = sg.eid2sgv.get(n.parent.eid)
                if not isgv:
                    isgv = sg.add_vertex()
                    ivtx = G.vertices.get(n.parent.eid)
                    sg.sgv2vtx[isgv] = ivtx
                    sg.eid2sgv[n.parent.eid] = isgv
                    sg.eid2vtx[n.parent.eid] = ivtx
                    sg.ncbi_node[isgv] = 1
                    sg.snode[isgv] = 0
                    sg.vtext[isgv] = ivtx.name

                if not (n.eid, n.parent.eid) in sg.se_created:
                ## if not n.edge_eid in sg.eid2sge:
                    se = sg.add_edge(osgv, isgv)
                    sg.se_created.add((n.eid, n.parent.eid))
                    sg.eid2sge[n.edge_eid] = se
                    sg.ncbi_edge[se] = 1
                    sg.snode_edge[se] = 0

        return sg

    def trim():
        sg.set_vertex_filter(sg.snode)
        sg.set_edge_filter(sg.snode_edge)

        def collect_leaves():
            leaves = []
            for x in ifilter(lambda x:x.in_degree()==0, sg.vertices()):
                y = list(set(x.out_neighbours()))
                if (len(y)==1 and
                    len(set(y[0].out_neighbours()))==1 and
                    len(set(y[0].in_neighbours()))==1 and
                    sg.sgv2vtx[y[0]].get('name')) :
                    leaves.append(x)
            return leaves

        leaves = collect_leaves()
        while leaves:
            for x in leaves:
                y = x.out_neighbours().next()
                vtx = sg.sgv2vtx[x]
                print 'trimming', vtx.name, 'to', sg.sgv2vtx[y].name
                sg.snode[x] = 0
                sg.isleaf[x] = 0
                sg.isleaf[y] = 1
            leaves = collect_leaves()
        return sg

    sg.add = add
    sg.trim = trim
    return sg

def radial_traverse(sg):
    found = []
    seen = set()
    def traverse(vertex):
        if sg.snode[vertex]:
            if vertex not in seen:
                for x in vertex.in_neighbours(): traverse(x)
            if vertex not in found and vertex.in_degree()==0:
                found.append(vertex)
                ## print vertex, sg.sgv2vtx[vertex].get('name')
            seen.add(vertex)
    traverse(sg.root.sgv)
    return found

def snode_bfs(sg, vertices, seen=None, iterations=1):
    stree_counts = Counter()
    if not seen: seen = set()
    for i in range(iterations):
        found = set()
        for x in vertices:
            for e in ifilter(lambda edge:sg.snode_edge[edge], x.in_edges()):
                e.source(), e.target()
                

def draw_stree_subgraph(sg, stree_colors=None):
    import math
    sg.set_vertex_filter(sg.snode)
    sg.set_edge_filter(sg.snode_edge)

    ## pos = sg.new_vertex_property('vector<double>')
    ## pin = sg.new_vertex_property('bool')
    ## for x in sg.vertices():
    ##     pos[x] = [0.0, 0.0]
    ##     pin[x] = False
    ## pos[sg.root.sgv] = [0.0, 0.0]
    ## pin[sg.root.sgv] = True
    ## lvs = radial_traverse(sg)
    ## angle = 0
    ## unit = 360.0/len(lvs)
    ## for lf in lvs:
    ##     x = math.cos(math.radians(angle))*1000
    ##     y = math.sin(math.radians(angle))*1000
    ##     angle += unit
    ##     pos[lf] = [x,y]
    ##     pin[lf] = True

    if not stree_colors: stree_colors = defaultdict(lambda:'gray')
   
    vcolor = sg.new_vertex_property("string")
    ecolor = sg.new_edge_property("string")
    ewidth = sg.new_edge_property("int")
    eweight = sg.new_edge_property("double")
    for v in sg.vertices():
        vcolor[v] = 'red' if sg.ncbi_node[v] else 'gray'
    for e in sg.edges():
        ecolor[e] = 'red' if sg.ncbi_edge[e] else 'gray'
        ewidth[e] = 1
    seen = set()
    for stid, root in sg.stree.items():
        c = stree_colors[stid]
        for n in root:
            if n.sgv not in seen:
                vcolor[n.sgv] = c
                seen.add(n.sgv)
            else:
                vcolor[n.sgv] = sg.snode_overlap_color
            if n.vtx.type=='ncbi_node':
                vcolor[n.sgv] = sg.ncbi_color
            if n.parent:
                if n.sge not in seen:
                    ecolor[n.sge] = c
                    ewidth[n.sge] = 4
                    seen.add(n.sge)
            
    pin = pos = None
    p1 = gt.sfdp_layout(sg,
                        C=0.001,
                        gamma=2.0,
                        pin=pin,
                        pos=pos)

    for v in sg.vertices():
        if len(set(v.in_neighbours()))==1 and len(set(v.out_neighbours()))==1:
            sg.vtext[v] = ''

    sg.set_reversed(True)
    gt.graph_draw(sg,
                  pos=p1,
                  vertex_fill_color=vcolor,
                  vertex_text=sg.vtext,
                  vertex_text_position=3.1415,
                  ## vertex_halo=sg.halo,
                  ## vertex_halo_color='green',
                  edge_color=ecolor,
                  edge_pen_width=ewidth,
                  ## eweight=sg.eweight
                  )
    sg.set_vertex_filter(None)
    sg.set_edge_filter(None)

def draw_stree(G, stree_id, color='green'):
    import math
    from ivy import layout, layout_polar
    sg = stree_subgraph(G, stree_id)

    pos = sg.new_vertex_property('vector<double>')
    pin = sg.new_vertex_property('bool')
    for x in sg.vertices():
        pos[x] = [0.0, 0.0]
        pin[x] = False
    pos[sg.root.sgv] = [0.0, 0.0]
    pin[sg.root.sgv] = True
    root = sg.stree[stree_id]
    root.ladderize()
    n2c = layout_polar.calc_node_positions(root, radius=1000)
    for n in root:
        k = n.sgv; v = n2c[n]
        pos[k] = [v.x, v.y]
        if n.isleaf: pin[k] = True
    ## leaves = root.leaves()
    ## angle = 0
    ## unit = 360.0/len(leaves)
    ## for lf in leaves:
    ##     x = math.cos(math.radians(angle))*1000
    ##     y = math.sin(math.radians(angle))*1000
    ##     angle += unit
    ##     pos[lf.sgv] = [x,y]
    ##     pin[lf.sgv] = True

    vcolor = sg.new_vertex_property("string")
    ecolor = sg.new_edge_property("string")
    ewidth = sg.new_edge_property("int")
    eweight = sg.new_edge_property("int")
    for v in sg.vertices():
        vcolor[v] = 'red' if sg.ncbi_node[v] else 'gray'
    for e in sg.edges():
        ecolor[e] = sg.ncbi_color if sg.ncbi_edge[e] else 'gray'
        ewidth[e] = 1

    seen = set()
    for n in root:
        if n.sgv not in seen:
            vcolor[n.sgv] = color
            seen.add(n.sgv)
        else:
            vcolor[n.sgv] = sg.snode_overlap_color
        if n.vtx.type=='ncbi_node':
            vcolor[n.sgv] = sg.ncbi_color
        if n.parent:
            if n.sge not in seen:
                ecolor[n.sge] = color
                ewidth[n.sge] = 4
                seen.add(n.sge)
            
    sg.set_vertex_filter(sg.snode)
    sg.set_edge_filter(sg.snode_edge)
    p1 = gt.sfdp_layout(sg,
                        p=1,
                        C=0.00001,
                        pin=pin,
                        pos=pos)
    sg.set_vertex_filter(None)
    sg.set_edge_filter(None)
    p2 = gt.sfdp_layout(sg,
                        ## p=0,
                        ## C=0.0001,
                        ## gamma=2.0,
                        ## theta=1.2,
                        pin=sg.snode,
                        pos=p1)
    sg.set_reversed(True)
    gt.graph_draw(sg,
                  pos=p2,
                  pin=pin,
                  vertex_fill_color=vcolor,
                  vertex_text=sg.vtext,
                  vertex_text_position=3.1415,
                  ## vertex_halo=sg.halo,
                  ## vertex_halo_color='green',
                  edge_color=ecolor,
                  edge_pen_width=ewidth,
                  ## eweight=sg.eweight
                  )
    sg.set_vertex_filter(None)
    sg.set_edge_filter(None)


g = connect()
sg = stree_subgraph(g)
for i in 2, 3, 4, 9: sg.add(i)
sg.trim()
draw_stree_subgraph(sg, {2:'green',3:'purple',4:'orange',9:'blue'})

## rec = db.stree(3)
## root = build.stree(db, rec.id)
## map_taxonomy(G, root)
## newnodes, newedges = insert_mapped_stree(G, root)
## sg = stree_subgraph(G, 3)
## sg = stree_subgraph(G, 212, sg)
## draw_stree_subgraph(sg, {212:'green',3:'purple'})
#g = new Neo4jGraph('/home/rree/ncbitax/phylografter.db')
