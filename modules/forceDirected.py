def getRenderResponse( clade, groupId, session ):
    
    collapsedNodeInfo = clade.collapsedNodeInfo.keys() if hasattr( clade, 'collapsedNodeInfo' ) else [ ]

    nodeDict = clade.preCollapseMeta.nodeDict if hasattr( clade, 'preCollapseMeta' ) else clade.meta.nodeDict

    rv = dict( nodes = [ ], links = [ ], longestLabel = clade.meta.longestTipLabel * session.textWidthMetric, rootId = clade.id, depth = clade.meta.depth )

    getRenderResponseRecurse( clade, groupId, rv, collapsedNodeInfo, -1, clade.meta.depth, session, nodeDict )

    return rv


def getRenderResponseRecurse( clade, groupId, rv, collapsedNodeInfo, parentId, currentDepth, session, nodeDict ):

    rv['nodes'].append( dict( name = clade.label,
                              nodeId = clade.id,
                              group = groupId,
                              value = nodeDict[ clade.id ].descendantCount,
                              children = [ child.id for child in clade.children ],
                              collapsed = clade.id in collapsedNodeInfo ) )

    currentIndex = len( rv['nodes'] ) - 1
        
    if( parentId != -1 ):
        rv['links'].append( dict( source = parentId, target = currentIndex, currentDepth = currentDepth ) )


    for child in clade.children:
        getRenderResponseRecurse( child, groupId, rv, collapsedNodeInfo, currentIndex, currentDepth - 1, session, nodeDict )
