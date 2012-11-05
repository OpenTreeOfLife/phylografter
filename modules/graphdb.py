from py2neo import neo4j, cypher
INCOMING = neo4j.Direction.INCOMING
OUTGOING = neo4j.Direction.OUTGOING

try:
    G = neo4j.GraphDatabaseService('http://localhost:7474/db/data')
    refnode = G.get_reference_node()
    ncbi_node_idx = G.get_or_create_index(
        neo4j.Node, 'ncbi_node', config={'type':'exact'})
    ncbi_name_idx = G.get_or_create_index(
        neo4j.Node, 'ncbi_name', config={'type':'exact'})
    ## stree_idx = G.get_or_create_index(
    ##     neo4j.Node, 'stree', config={'type':'exact'})
    ## stree_ref = refnode.get_single_related_node(OUTGOING, 'STREE_REF')
    ## if not stree_ref:
    ##     stree_ref = G.create({}, (refnode, 'STREE_REF', 0))[0]
except Exception as e:
    print 'neo4j server not found:', e

def bulbs_connect(uri='http://localhost:7474/db/data'):
    from bulbs.neo4jserver import Graph
    from bulbs.config import Config
    config = Config(uri)
    config.autoindex = False
    G = Graph(config)
    return G

def insert_stree(db, rec):
    root = build.stree(db, rec.id)
    for n in root.leaves():
        node = None
        if n.rec.ottol_name:
            ottol_name = db.ottol_name(n.rec.ottol_name)
            if ottol_name.ncbi_taxid:
                taxid = ottol_name.ncbi_taxid
                node = ncbi_node_idx.get('taxid', str(taxid))[0]
            else:
                name = n.rec.ottol_name.name
                v = ncbi_name_idx.get('name', name)
                if len(v)==1:
                    node = v[0].get_single_related_node(OUTGOING, 'NAME_OF')
                elif len(v)>1:
                    print len(v), 'synonyms of ottol_name', name
                else: print 'ottol_name', name, 'not found'
        else:
            name = n.rec.label
            v = ncbi_name_idx.get('name', name)
            if len(v)==1:
                node = v[0].get_single_related_node(OUTGOING, 'NAME_OF')
            elif len(v)>1:
                print len(v), 'synonyms of label', name
            else: print 'label', name, 'not found'
        n.ncbi_node = node
    nodes = [ n.ncbi_node for n in root.leaves() ]
    q = """
    leaves = %s
    v = []
    leaves.each() {
        leaf -> v.add(leaf.out('CHILD_OF').loop(1){true}{true}*.id)
    }
    v
    """ % [ x.eid for x in nodes ]
    resp = bulbs_connect().gremlin.execute(q).content
