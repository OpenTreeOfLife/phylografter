import math, sys, build
from gluon.storage import Storage
import plugin_treeViewer as util
import plugin_treeGrafter as graftUtil


def pruneClade( db, session, request, auth ):

    nodeIdToPrune = int( request.vars.nodeId )
    columnIndex = int( request.vars.columnIndex )

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeId ]
    columnInfo = treeState.columns[ columnIndex ]

    tree = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, columnInfo.rootNodeId, columnInfo.collapsedNodeStorage )

    prunedClade = graftUtil.pruneClade( tree, nodeIdToPrune )

    graftUtil.postPruneDBUpdate( db, session, request, auth, tree, prunedClade )

    for ( collapsedNodeId, collapsedNodeData ) in columnInfo.collapsedNodeStorage.items():
        
        if( util.isAncestor( prunedClade, collapsedNodeData ) ):
            
            if( nodeIdToPrune not in treeState.formerlyCollapsedNodeStorage ):
                treeState.formerlyCollapsedNodeStorage[ collapsedNodeId ] = columnInfo.collapsedNodeStorage[ collapsedNodeId ]

        del columnInfo.collapsedNodeStorage[ collapsedNodeId ]


    return getRenderResponse( \
        tree,
        session,
        columnInfo )

