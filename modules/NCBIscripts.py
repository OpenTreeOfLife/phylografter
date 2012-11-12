ncbi_subtree = """
c2p = [:]
leafids.each() { lf -> 
    c = g.v(lf)
    e = c.outE('NCBI_CHILD_OF').next()
    c2p[c.id] = [e.id, e.inV.id]
    
    c.out('NCBI_CHILD_OF').loop(1){!(it.object.id in c2p)}{true}.each() { n ->
        e = n.outE('NCBI_CHILD_OF')
        if (e) { e = e.next(); c2p[n.id] = [e.id, e.inV.id] }
    }
}
c2p
"""

rootpath = """
g.v(n).out('NCBI_CHILD_OF').loop(1) {
    it.object.id != anc } { it.object.id==anc }.id
"""
