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

    if( session.TreeViewer.treeType == 'grafted' ):
        
        for ( collapsedNodeId, collapsedNodeData ) in columnInfo.collapsedNodeStorage.items():

            if( util.isAncestor( prunedCladeRow, collapsedNodeData ) ):

                del columnInfo.collapsedNodeStorage[ collapsedNodeId ]

                if( ( ( len( treeState.columns ) - 1 ) > columnIndex ) and \
                      ( collapsedNodeId == treeState.columns[ columnIndex + 1 ].rootNodeId ) ):
                                       
                    while( ( len( treeState.columns ) - 1 ) > columnIndex ):
                        treeState.columns.pop()

    graftUtil.postPruneDBUpdate( db, session, request, auth, tree, prunedCladeRow )

    return dict() 
