import math, sys, build
from gluon.storage import Storage
import plugin_treeViewer as util
import plugin_treeGrafter as graftUtil
import unprocessedPhylogram as super

def pruneClade( db, session, request, auth ):

    nodeIdToPrune = int( request.vars.nodeId )
    columnIndex = int( request.vars.columnIndex )

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeId ]
    columnInfo = treeState.columns[ columnIndex ]

    prunedCladeRow = db( db[ session.TreeViewer.strNodeTable ].id == nodeIdToPrune ).select()[ 0 ]

    tree = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, treeState.columns[ 0 ].rootNodeId, columnInfo.collapsedNodeStorage )

    graftUtil.pruneClade( tree, nodeIdToPrune )

    graftUtil.postPruneDBUpdate( db, session, request, auth, tree, prunedCladeRow )

    return dict() 
