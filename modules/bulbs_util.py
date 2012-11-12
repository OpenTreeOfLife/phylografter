import build

def connect(uri='http://localhost:7474/db/data/'):
    from bulbs.neo4jserver import Graph, VertexIndexProxy, ExactIndex
    from bulbs.config import Config
    config = Config(uri)
    config.autoindex = False
    G = Graph(config)
    exact_node_indexes = VertexIndexProxy(ExactIndex, G.client)
    G.ncbi_node_idx = exact_node_indexes.get('ncbi_node')
    G.ncbi_name_idx = exact_node_indexes.get('ncbi_name')
    return G

def get_ncbi_node(G, leaf):
    label = leaf.rec.label
    if leaf.rec.ottol_name:
        if leaf.rec.ottol_name.ncbi_taxid:
            taxid = str(leaf.rec.ottol_name.ncbi_taxid)
            return G.ncbi_node_idx.lookup(taxid=taxid).next()
        else:
            label = leaf.rec.ottol_name.name
    name = label.replace('_', ' ')
    v = list(G.ncbi_name_idx.lookup(name=name))
    if len(v)==1:
        return v[0].outV('NAME_OF').next()

def ncbi_subtree(G, leafids):
    from ivy.tree import Node
    q = """
    c2p = [:]
    leafids.each() { lf -> 
        c = g.v(lf); p = c.out('CHILD_OF').next()
        c2p[c.id] = p.id
        c.out('CHILD_OF').loop(1){!(it.object.id in c2p)}{true}.each() { n ->
            p = n.out('CHILD_OF')
            if (p) { c2p[n.id] = p.next().id }
        }
    }
    c2n
    """
    d = G.gremlin.execute(q, dict(leafids=leafids)).content
    nodes = dict([ (x, Node(isleaf=True, gid=x)) for x in leafids ])
    

rec = db.stree(3)
root = build.stree(db, rec.id)
for lf in root.leaves(): lf.ncbi_node = get_ncbi_node(lf)
leafids = [ x.ncbi_node.eid for x in root.leaves() if x.ncbi_node ]


#g = new Neo4jGraph('/home/rree/ncbitax/phylografter.db')
