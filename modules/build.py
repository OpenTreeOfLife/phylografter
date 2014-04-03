"""
module for building trees of ivy.tree.Nodes from database tables
"""
from ivy_local.tree import Node
from collections import defaultdict
from gluon.storage import Storage

#the tree viewer is deprecating this function
def node2tree( db, session, nodeId ):
    if session.TreeViewer.treeType == 'source':
        return sourceClade( db, session, nodeId, session.collapsedNodeStorage[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ] )
    else:
        return graftedClade( db, session, nodeId, session.collapsedNodeStorage[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ] )

   
def getRootRecord( db, strNodeTable, rootNodeId ):

    return db( db[ strNodeTable ].id == rootNodeId ).select()[0]


def getCladeSqlString( nodeTable, rootRec, collapsedNodeStorage, extra = Storage() ):

    joinString = pruneClause = ''

    if( nodeTable == 'snode' ):

        joinString = 'FROM snode LEFT JOIN ott_node on snode.ott_node = ott_node.id '

        pruneClause = ''

    elif( nodeTable == 'gnode' ):

        joinString = ''.join( [ 'FROM gnode LEFT JOIN snode on gnode.snode = snode.id ',
                                'LEFT JOIN ott_node on snode.ott_node = ott_node.id ' ] )

        if( 'pruned' in extra and extra['pruned'] == True ):

            pruneClause = ''.join( [ 'gnode.pruned = "T" AND prune_detail.gtree_edit = ', str( extra['editId'] ), ' AND ' ] )

            joinString = ''.join( [ joinString, 'JOIN prune_detail on gnode.id = prune_detail.pruned_gnode ' ] )

        else:
            pruneClause = 'gnode.pruned = "F" AND '

    stringList = [ \
        'SELECT ', nodeTable, '.id, ',
                   nodeTable, '.next, ',
                   nodeTable, '.back, ',
                   nodeTable, '.length, ',
                   nodeTable, '.label, ',
                   'ott_node.name ',
        joinString,
        'WHERE ', nodeTable, '.tree = ', str( rootRec.tree ), ' AND ',
        pruneClause, 
        nodeTable, '.next >= ', str( rootRec.next ), ' AND ',
        nodeTable, '.back <= ', str( rootRec.back ) ]


    if( len( collapsedNodeStorage ) ):

        for ( nodeId, collapsedNodeData ) in collapsedNodeStorage.items():

            stringList.append( \
                ''.join( [ \
                    ' AND NOT ( ( ', nodeTable, '.next > ', str( collapsedNodeData['next'] ), ' ) ',
                           'AND ( ', nodeTable, '.back < ', str( collapsedNodeData['back'] ), ' ) )' ] ) )

    stringList.append( ''.join( [ ' ORDER BY ', nodeTable, '.next;' ] ) )

    ## print ''.join( stringList )

    return ''.join( stringList ) 


def getIvyTreeFromNodeList( resultList ):

    parentStack = []

    cladeRoot = getNodeFromRowData( resultList[0] ) 
    cladeRoot.depth = 0
    parentStack.append( cladeRoot )

    for row in resultList[1:]:

        node = getNodeFromRowData( row )
        node.depth = len( parentStack );

        while( node.back > parentStack[ -1 ].back ):
            parentStack.pop() 

        node.parent = parentStack[ -1 ]
        parentStack[ -1 ].add_child( node )
        parentStack.append( node )
    
    return cladeRoot


def graftedClade( db, rootNodeId, collapsedNodeStorage, extra = Storage() ):

    rootRec = getRootRecord( db, 'gnode', rootNodeId )

    resultList = db.executesql( getCladeSqlString( 'gnode', rootRec, collapsedNodeStorage, extra ) )

    print resultList

    return getIvyTreeFromNodeList( resultList )


def sourceClade( db, rootNodeId, collapsedNodeStorage, extra = Storage() ):

    rootRec = getRootRecord( db, 'snode', rootNodeId )

    resultList = db.executesql( getCladeSqlString( 'snode', rootRec, collapsedNodeStorage ) )
   
    return getIvyTreeFromNodeList( resultList )


def getNodeFromRowData( row ):

    node = Node()

    node.id = row[0]; node.next = row[1]; node.back = row[2]; node.length = row[3]; node.label = row[4]
    node.taxon = row[5];

    return node


# chris baron - I don't think we need these anymore - at least not for the tree viewer #
# RR - I restored a few that I'm using
def root_snode(db, tree):
    "return the root snode record for stree id 'tree'"
    t = db.snode
    q = (t.tree==tree)&(t.next==1)
    v = db(q).select()
    assert len(v)==1
    return v[0]

## def leaves(t, rec):
##     db = t._db
##     q = (t.next>rec.next)&(t.back<rec.back)&(t.next==t.back-1)
##     return list(db(q).select(orderby=t.next))

## def mrca(t, recs):
##     db = t._db
##     n = min([ x.next for x in recs ])
##     b = max([ x.back for x in recs ])
##     q = (t.next<n)&(t.back>b)
##     return db(q).select(orderby=t.back,limitby=(0,1)).first()

def stree(db, i, lim=0, maxdepth=None):
    "build a tree of ivy.tree.Nodes for db.stree.id==i"
    t = db.snode
    q = t.tree==i
    r = root_snode(db, i)
    root = nextbacktree(db.snode, r.id, q, lim=lim, maxdepth=maxdepth)
    for n in root: n.label = n.rec.label
    return root

## def snode2tree(db, i, q=None, lim=0, maxdepth=None):
##     """
##     build a tree of ivy.tree.Nodes from root db.snode.id==i,
##     filtered by query q
##     """
##     t = db.snode
##     r = t[int(i)]
##     if q: q &= (t.tree==r.tree)
##     else: q = (t.tree==r.tree)
##     root = nextbacktree(db.snode, r.id, q, lim=lim, maxdepth=maxdepth)
##     for n in root:
##         n.label = n.rec.label
##     return root

## def gnode2tree(db, i, q=None, lim=0, maxdepth=None):
##     """
##     build a tree of ivy.tree.Nodes from root db.snode.id==i,
##     filtered by query q
##     """
##     t = db.gnode
##     r = t[int(i)]
##     if q: q &= (t.tree==r.tree)
##     else: q = (t.tree==r.tree) & ( t.pruned==False )
##     root = nextbackgtree(db.gnode, r.id, q, lim=lim, maxdepth=maxdepth)
##     for n in root:
##         n.label = n.rec.label
##     return root

## def ncbi2tree(db, i, lim=0, maxdepth=None):
##     root = nextbacktree(db.ncbi_taxon, i, lim=lim, maxdepth=maxdepth)
##     for n in root:
##         n.label = n.rec.name
##     return root

def nextbacktree(t, i, q=None, lim=0, maxdepth=None):
    """
    create a tree of ivy.tree.Nodes from table t, with
    records having fields next, back, parent, and depth
    """
    db = t._db
    r = t[int(i)]
    limits = dict(orderby=t.next)
    limits['orderby'] = t.next
    if lim: limits["limitby"] = (0,lim)
    q2 = (t.next>r.next)&(t.back<r.back)
    if maxdepth:
        q2 &= (t.depth <= maxdepth)
    recs = db(q)(q2).select(**limits)
    
    root = Node(); root.isroot = True
    root.rec = r; root.id = r.id; root.next = r.next; root.back = r.back;

    i2n = {}; i2n[r.id] = root
    for r in recs:
        n = Node()
        n.rec = r; n.id = r.id; n.next = r.next; n.back = r.back; n.parent = i2n[r.parent];
        if (((not maxdepth) and (r.next==r.back-1)) or
            (maxdepth and (n.depth == maxdepth))):
            n.isleaf = True
        i2n[r.id] = n
        i2n[r.parent].add_child(n)
    return root

## def nextbackgtree(t, i, q=None, lim=0, maxdepth=None):
##     """
##     create a tree of ivy.tree.Nodes from table t, with
##     records having fields next, back, parent, and depth
##     """
##     db = t._db
##     r = t[int(i)]
##     limits = dict(orderby=t.next)
##     if lim: limits["limitby"] = (0,lim)
##     q2 = (t.next>r.next)&(t.back<r.back)
##     if maxdepth:
##         q2 &= (t.depth <= maxdepth)
##     recs = db(q)(q2).select(**limits)
   
##     #Node = ivy.tree.Node
##     root = Node(); root.isroot = True
##     root.rec = r; root.id = r.id; root.next = r.next; root.back = r.back; root.stree = r.stree; root.snode = r.snode 

##     i2n = {}; i2n[r.id] = root

##     for r in recs:
    
##         n = Node()

##         if( not hasattr( r, 'id' ) ):
##             r = r.gnode

##         n.rec = r; n.id = r.id; n.next = r.next; n.back = r.back; n.stree = r.stree; n.snode = r.snode
##         if (((not maxdepth) and (r.next==r.back-1)) or
##             (maxdepth and (n.depth == maxdepth))):
##             n.isleaf = True
##         i2n[r.id] = n
##         i2n[r.parent].add_child(n)
##     return root

## def add_child(t, parent, child):
##     """
##     'parent' and 'child' are assumed to be ivy.tree.Nodes with 'rec'
##     attributes
##     """
##     db = t._db
    
##     child_next = parent.back
    
##     pass

## def prune(t, rec):
##     "for a tree table with next, back and parent fields, prune a subtree"
##     db = t._db
##     assert rec.parent
##     parent = t[rec.parent]
##     ## children = db(t.parent==parent.id).select(orderby=t.next)

## def recurse(table, rec, d=None):
##     """
##     recursively create a tree of ivy.tree.Nodes from table, with root
##     rec, using parent references only
##     """
##     db = table._db
##     isroot = False
##     if not d:
##         d = defaultdict(list)
##         isroot = True
##     children = db(table.parent==rec.id).select()
##     for c in children:
##         recurse(table, c, d)
##         d[rec.id].append(c)
##     if isroot:
##         r = ivy.tree.Node(); r.isroot=True; r.rec = rec
##         r.label = rec.name
##         def f(n):
##             for x in d[n.id]:
##                 c = ivy.tree.Node(); c.rec = x; c.label = x.name
##                 n.add_child(c)
##                 f(c)
##         f(r)
##         for x in r:
##             if not x.children:
##                 x.isleaf = True
##         return r

## def gtree(db, i, lim=0, maxdepth=None):
##     "build a tree of ivy.tree.Nodes for db.gtree.id==i"
##     t = db.gnode
##     q = ( t.tree==i ) & ( t.pruned == False )
##     r = root_gnode(db, i)
##     root = nextbackgtree(db.gnode, r.id, q, lim=lim, maxdepth=maxdepth)
##     #for n in root:
##         #n.label = n.rec.label
##     return root

## def root_gnode(db, tree):
##     "return the root gnode record for stree id 'tree'"
##     t = db.gnode
##     q = (t.tree==tree)&(t.next==1)
##     v = db(q).select()
##     assert len(v)==1
##     return v[0]

## def rootpath(t, r, q=None, d=None):
##     "return a list of records leading up to record 'r'"
##     db = t._db
##     q2 = (t.next<r.next)&(t.back>r.back)
##     return list(db(q)(q2).select(orderby=~t.next))
