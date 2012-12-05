ncbi_subtree = """
c2p = [:]
leafids.each() { lf -> 
    c = g.v(lf)
    e = c.outE('NCBI_CHILD_OF').next()
    c2p[c.id] = [e.id, e.inV.id]
    
    //c.out('NCBI_CHILD_OF').loop(1){!(it.object.id in c2p)}{true}.each() { n ->
    c.out('NCBI_CHILD_OF').loop(1){true}{true}.each() { n ->
        e = n.outE('NCBI_CHILD_OF')
        if (e) { e = e.next(); c2p[n.id] = [e.id, e.inV.id] }
    }
}
c2p
"""

fetch_stree = """
g.v(n).outE('ROOT').filter{it.getProperty('stree')==i}.inV.as('n').inE('SNODE_CHILD_OF').filter{i in it.getProperty('stree')}.outV.loop('n'){true}{true}.outE('SNODE_CHILD_OF').filter{i in it.getProperty('stree')}.dedup()
"""

find_name = """
g.v(n).in('NCBI_CHILD_OF').loop(1){it.object.name!=name}{it.object.name==name}
"""

ncbi_anc_in_rootpath = """
g.v(n).out('NCBI_CHILD_OF').loop(1){it.object.id != anc}{it.object.id==anc}
"""

stree_rootpath = """
g.v(lf).as('x').out('SNODE_CHILD_OF').filter{i in it.stree}.loop('x'){it.object.id!=r}{true}
"""

named_neighborhood = """
v = []
root = g.v(n)
root_strees = root.stree.toList()
for (lf in root.as('root').inE('SNODE_CHILD_OF').outV.loop('root'){!it.object.has('type','ncbi_node')}.dedup()) {
    for (anc in lf.as('lf').outE('SNODE_CHILD_OF').inV.loop('lf'){it.object!=root}{true}) {
        for (e in anc.inE('SNODE_CHILD_OF')) {
            //strees = e.stree.toList()
            //strees.retainAll(root_strees)
            //if (strees) v.add(e)
            v.add(e)
        }
    }
}
v._().dedup()
"""

named_neighborhood_leaves = """
g.v(n).as('root').inE('SNODE_CHILD_OF').outV.loop('root'){!it.object.has('type','ncbi_node')}.dedup()
"""

q = """
start lf=node({n}), root=node({r})
match lf-[edges:SNODE_CHILD_OF*]->root
where all(e in edges where {i} in e.stree)
return edges
"""
