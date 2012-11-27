import NCBIgraph
from collections import defaultdict

def index():
    return dict()

def fan():
    taxid = request.args(0) or '91827' # core eudicots
    G = NCBIgraph.connect()
    n = G.ncbi_node_idx.get_unique(taxid=taxid)
    sg = NCBIgraph.named_neighborhood_subgraph(G, n.eid)
    pos = NCBIgraph.fan_layout(sg)

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

    nodes = []
    for v in sg.vertices():
        n = sg.sgv2vtx[v]
        if n.type=='ncbi_node': c='blue'
        elif len(n.stree)==1: c = stree_colors[n.stree[0]]
        else: c = 'yellow'
        vtx = sg.sgv2vtx[v]
        x, y = pos[v]
        nodes.append(dict(eid=vtx.eid, x=x, y=y, color=c,
                          label=vtx.get('name') or ''))

    return dict(nodes=nodes, edges=edges)
        
    
