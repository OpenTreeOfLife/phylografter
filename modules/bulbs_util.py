import build
from bulbs.neo4jserver import Graph, VertexIndexProxy, ExactIndex
from bulbs.config import Config

config = Config('http://localhost:7474/db/data/')
config.autoindex = False
try:
    G = Graph(config)
    exact_node_indexes = VertexIndexProxy(ExactIndex, G.client)
    ncbi_node_idx = exact_node_indexes.get('ncbi_node')
    ncbi_name_idx = exact_node_indexes.get('ncbi_name')
except Exception as e:
    print 'neo4j server not found:', e

def get_ncbi_node(leaf):
    label = leaf.rec.label
    if leaf.rec.ottol_name:
        if leaf.rec.ottol_name.ncbi_taxid:
            taxid = str(leaf.rec.ottol_name.ncbi_taxid)
            return ncbi_node_idx.lookup(taxid=taxid).next()
        else:
            label = leaf.rec.ottol_name.name
    name = label.replace('_', ' ')
    v = list(ncbi_name_idx.lookup(name=name))
    if len(v)==1:
        return v[0].outV('NAME_OF').next()

rec = db.stree(3)
root = build.stree(db, rec.id)
for lf in root.leaves(): lf.ncbi_node = get_ncbi_node(lf)

q = """
ncbi_node_idx = g.idx('ncbi_node')
root = ncbi_node_idx.get('taxid',1).next()
root.in('CHILD_OF').loop(1){it.loops<3}.tree.cap
"""

q = """
ncbi_node_idx = g.idx('ncbi_node')
root = ncbi_node_idx.get('taxid',1).next()
v = []
leafids.each() {
    leaf -> v.add(g.v(leaf).out('CHILD_OF').loop(1){true}{true}*.id)
}
v = v[1..-1].inject(v[0]) {a,b -> (a as Set)+(b as Set)}
root.as('x').in('CHILD_OF').filter{it.id in v}.gather.scatter.loop('x'){true}{true}
"""
leafids = [ x.ncbi_node.eid for x in root.leaves() if x.ncbi_node ]
resp = G.gremlin.execute(q, dict(leafids=leafids)).content

