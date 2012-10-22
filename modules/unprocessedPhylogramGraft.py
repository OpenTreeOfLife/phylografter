import math, sys, build
from gluon.storage import Storage
import plugin_treeViewer as util
import plugin_treeGrafter as graftUtil
reload( graftUtil )
import unprocessedPhylogram as super

def pruneClade( db, session, request, auth ):

    nodeIdToPrune = int( request.vars.nodeId )
    columnIndex = int( request.vars.columnIndex )

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]
    columnInfo = treeState.columns[ columnIndex ]

    prunedCladeRow = db( db[ session.TreeViewer.strNodeTable ].id == nodeIdToPrune ).select()[ 0 ]

    tree = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, session, treeState.columns[ 0 ].rootNodeId, Storage() )

    graftUtil.pruneClade( tree, nodeIdToPrune )

    for ( collapsedNodeId, collapsedNodeData ) in columnInfo.collapsedNodeStorage.items():

        if( util.isAncestor( prunedCladeRow, collapsedNodeData ) ):

            if( collapsedNodeId not in treeState.formerlyCollapsedNodeStorage ):
                treeState.formerlyCollapsedNodeStorage[ collapsedNodeId ] = columnInfo.collapsedNodeStorage[ collapsedNodeId ]

            del columnInfo.collapsedNodeStorage[ collapsedNodeId ]

    graftUtil.postPruneDBUpdate( db, session, request, auth, tree, prunedCladeRow )

    return dict() 
