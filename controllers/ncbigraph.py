import NCBIgraph
from collections import defaultdict

def index():
    return dict()

def fan():
    G = NCBIgraph.connect()
    ## taxid = request.args(0) or '91827' # core eudicots
    taxid='71275'
    n = G.ncbi_node_idx.get_unique(taxid=taxid)
    sg = NCBIgraph.named_neighborhood_subgraph(G, n.eid)

    ## rosids = G.ncbi_node_idx.get_unique(taxid='71275')
    ## NCBIgraph.named_neighborhood_subgraph(G, rosids.eid, sg)
    
    ## pos = NCBIgraph.fan_layout(sg, start=-45, end=45, radius=1000)
    pos = NCBIgraph.fan_layout(sg, start=-45, end=45, radius=1000)

    t = NCBIgraph.tango()
    stree_colors = defaultdict(lambda:'#%02x%02x%02x'% tuple(
        [ int(x*255) for x in t.next()[:-1] ]))

    edges = []
    for e in sg.edges():
        c = stree_colors[sg.edge2stree[e]]
        src = sg.sgv2vtx[e.source()].eid
        tgt = sg.sgv2vtx[e.target()].eid
        stree = sg.edge2stree[e]
        edges.append(dict(source=src, target=tgt, stree=stree, color=c))

    nodes = {}
    for v in sg.vertices():
        n = sg.sgv2vtx[v]
        if n.type=='ncbi_node': c='blue'
        elif len(n.stree)==1: c = stree_colors[n.stree[0]]
        else: c = 'yellow'
        text_anchor = 'start' if v.out_degree()==0 else 'end'
        vtx = sg.sgv2vtx[v]
        x, y = pos[v]
        radius = 1.0 if (len(n.stree)>1 or n.type=='ncbi_node') else 0.5
        nodes[vtx.eid] = dict(x=x, y=-y, color=c, text_anchor=text_anchor,
                              radius=radius,
                              eid=vtx.eid, taxid=vtx.get('taxid') or None,
                              label=vtx.get('name') or '')

    print edges
    return dict(nodes=nodes, edges=edges)
        
    
