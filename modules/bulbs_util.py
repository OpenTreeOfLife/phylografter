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
    label = rec.label
    if leaf.rec.ottol_name:
        if leaf.rec.ottol_name.ncbi_taxid:
            taxid = str(leaf.rec.ottol_name.ncbi_taxid)
            return ncbi_node_idx.get('taxid', taxid)[0]
        else:
            label = leaf.rec.ottol_name.name
    name = label.replace('_', ' ')
    v = ncbi_name_idx.get('name', name)
    if len(v)==1:
        return v[0].get_single_related_node(OUTGOING, 'NAME_OF')


def insert_stree(db, rec):
    root = build.stree(db, rec.id)
    for n in root.leaves():
        node = None
        if n.rec.ottol_name:
            ottol_name = db.ottol_name(n.rec.ottol_name)
            if ottol_name.ncbi_taxid:
                taxid = ottol_name.ncbi_taxid
                node = ncbi_node_idx.get_unique(taxid=taxid)
            else:
                name = n.rec.ottol_name.name
                v = list(ncbi_name_idx.lookup(name=name))
                if len(v)==1:
                    node = v[0].outV('NAME_OF').next()
                elif len(v)>1:
                    print len(v), 'synonyms of ottol_name', name
                else: print 'ottol_name', name, 'not found'
        else:
            name = n.rec.label
            v = list(ncbi_name_idx.lookup(name=name))
            if len(v)==1:
                node = v[0].outV('NAME_OF').next()
            elif len(v)>1:
                print len(v), 'synonyms of label', name
            else: print 'label', name, 'not found'
        n.ncbi_node = node
    nodes = [ n.ncbi_node for n in root.leaves() ]

    q = """
    leaves = g.v%(leaves)s
    v = []
    leaves.each() {
        leaf -> v.add(leaf.out('CHILD_OF').loop(1){true}{true}*.id)
    }
    v
    """ % dict(leaves=tuple([ x.eid for x in nodes ]))
    resp = G.gremlin.execute(q).content

