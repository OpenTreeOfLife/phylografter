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

    tree = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, treeState.columns[ 0 ].rootNodeId, Storage() )

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



def replaceClade( db, session, request, auth ):

    replacedNodeId = int( request.vars.replacedNodeId )
    replacingNodeId = int( request.vars.replacingNodeId )
    replacingNodeTreeId = int( request.vars.replacingNodeTreeId )

    columnIndex = int( request.vars.columnIndex )
    
    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]
    columnInfo = treeState.columns[ columnIndex ]

    replacedCladeRow = db( db[ session.TreeViewer.strNodeTable ].id == replacedNodeId ).select()[ 0 ]

    tree = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, treeState.columns[ 0 ].rootNodeId, Storage() )
    replacingClade = getattr( build, ''.join( [ request.vars.replacingNodeTreeType, 'Clade' ] ) )( db, replacingNodeId, Storage() )

    graftUtil.replaceClade( tree, replacedNodeId, replacingClade )

    if( session.TreeViewer.treeType == 'grafted' ):
        
        for ( collapsedNodeId, collapsedNodeData ) in columnInfo.collapsedNodeStorage.items():

            if( util.isAncestor( replacedCladeRow, collapsedNodeData ) ):

                del columnInfo.collapsedNodeStorage[ collapsedNodeId ]

                if( ( ( len( treeState.columns ) - 1 ) > columnIndex ) and \
                      ( collapsedNodeId == treeState.columns[ columnIndex + 1 ].rootNodeId ) ):
                                       
                    while( ( len( treeState.columns ) - 1 ) > columnIndex ):
                        treeState.columns.pop()

    graftUtil.postReplaceDBUpdate( db, session, request, auth, tree, replacedCladeRow, replacingClade )

    return dict()


def graftClade( db, session, request, auth ):

    graftingOntoNodeId = int( request.vars.graftingOntoNodeId )
    graftingNodeId = int( request.vars.graftingNodeId )
    graftingNodeTreeId = int( request.vars.graftingNodeTreeId )

    columnIndex = int( request.vars.columnIndex )
    
    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]
    columnInfo = treeState.columns[ columnIndex ]

    tree = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, treeState.columns[ 0 ].rootNodeId, Storage() )
    graftingClade = getattr( build, ''.join( [ request.vars.graftingNodeTreeType, 'Clade' ] ) )( db, graftingNodeId, Storage() )

    graftUtil.graftClade( tree, graftingOntoNodeId, graftingClade )

    graftUtil.postGraftDBUpdate( db, session, request, auth, tree, graftingOntoNodeId, graftingClade )

    return dict()
