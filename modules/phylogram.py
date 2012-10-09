import bisect, math, sys
from gluon.storage import Storage
import plugin_treeViewer as util


def getUnprocessedRenderResponse( tree, session, collapsedNodes=[] ):
   
    mode = session.TreeViewer.viewInfo['mode'].capitalize()

    renderInfo = getattr( sys.modules[__name__], ''.join( [ 'getRenderInfoFor', mode, 'Mode' ] ) )( tree )

    getattr( sys.modules[__name__], ''.join( [ 'determineTreeToRenderFor', mode, 'Mode' ] ) )( tree, renderInfo, session, collapsedNodes )

    return getUnprocessedCladeResponse( session, tree, renderInfo, collapsedNodes )


def getRenderInfoForNavigateMode( tree ):

    renderInfo = \
        Storage( depth = 0,
                 longestTraversal = 0,
                 nodeInfo = dict(),
                 nodeRef = Storage(),
                 longestLabelAtDepth = Storage(),
                 collapseOrder = Storage( weights = [], ids = [] ) )

    renderInfo.longestTraversal = recurseForInfoNavigateMode( renderInfo, tree, Storage( generation = 1 ) ).longsestTraversal

    return renderInfo


def recurseForInfoNavigateMode( renderInfo, node, recurseInfo ):
    """
    A recursive function that does the work for gatherTreeInfo
    """

    if( renderInfo.depth < recurseInfo.generation ):
        renderInfo.depth = recurseInfo.generation

    currentIterationInfo = Storage( \
        longestTraversal = 0,
        distanceFromLeaf = 0,
        descendantTipCount = 0,
        closestDescendantLabel = '',
        hasDescendantLabel = False,
        descendantLabelCount = 0 )
   
    text = node.taxon if node.taxon else node.label if node.label else ''

    nodeInfo = renderInfo.nodeInfo[ node.id ] = dict( text = text, next = node.next, back = node.back, nodeId = node.id, children = [ child.id for child in node.children ], parent = node.parent.id if node.parent else '' )
    renderInfo.nodeRef[ node.id ] = node
    
    if node.children:

        for child in node.children:

            recursiveIterationInfo = \
                recurseForInfoNavigateMode( renderInfo, child, Storage( generation = recurseInfo.generation + 1 ) )

            currentIterationInfo.descendantTipCount += recursiveIterationInfo.descendantTipCount
            currentIterationInfo.descendantLabelCount += recursiveIterationInfo.descendantLabelCount

            if( recursiveIterationInfo.distanceFromLeaf >= currentIterationInfo.distanceFromLeaf ):
                currentIterationInfo.distanceFromLeaf = recursiveIterationInfo.distanceFromLeaf + 1
           
            if( recursiveIterationInfo.longestTraversal >= currentIterationInfo.longestTraversal ):
                currentIterationInfo.longestTraversal = recursiveIterationInfo.longestTraversal
            
            if( len( recursiveIterationInfo.closestDescendantLabel ) ):
                nodeInfo['closestDescendantLabel'] = currentIterationInfo.closestDescendantLabel = recursiveIterationInfo.closestDescendantLabel


        if( node.length ):
            currentIterationInfo.longestTraversal += node.length
        
        nodeWeight = ( currentIterationInfo.descendantTipCount / int( currentIterationInfo.distanceFromLeaf ) )

        if( recursiveIterationInfo.hasDescendantLabel ):
            currentIterationInfo.hasDescendantLabel = True
            nodeWeight *= .25

        position = bisect.bisect( renderInfo.collapseOrder.weights, nodeWeight )
        renderInfo.collapseOrder.weights.insert( position, nodeWeight )
        renderInfo.collapseOrder.ids.insert( position, nodeInfo['nodeId'] )

        if( text ):
            currentIterationInfo.closestDescendantLabel = text
            currentIterationInfo.descendantLabelCount += 1
            currentIterationInfo.hasDescendantLabel = True

            if( ( recurseInfo.generation not in renderInfo.longestLabelAtDepth ) or
                ( len( text ) > renderInfo.longestLabelAtDepth[ recurseInfo.generation ] ) ):
                renderInfo.longestLabelAtDepth[ recurseInfo.generation ] = len( text )

    
        nodeInfo['descendantTipCount'] = currentIterationInfo.descendantTipCount
        nodeInfo['descendantLabelCount'] = currentIterationInfo.descendantLabelCount

    else:

        currentIterationInfo.descendantTipCount += 1 
        currentIterationInfo.distanceFromLeaf = 1 

        if( node.length ):
            currentIterationInfo.longestTraversal = node.length


        if( text ):
            currentIterationInfo.closestDescendantLabel = text
            currentIterationInfo.descendantLabelCount += 1


    return Storage( distanceFromLeaf = currentIterationInfo.distanceFromLeaf,
                    descendantTipCount = currentIterationInfo.descendantTipCount,
                    descendantLabelCount = currentIterationInfo.descendantLabelCount,
                    closestDescendantLabel = currentIterationInfo.closestDescendantLabel,
                    longestTraversal = currentIterationInfo.longestTraversal )
  


def determineTreeToRenderForNavigateMode( tree, renderInfo, session, collapsedNodeInfo ):

    numberOfTips = renderInfo.nodeInfo[ tree.id ]['descendantTipCount']
    maxTips = session.TreeViewer.config.maxTips;

    if( numberOfTips > maxTips ):

        session.TreeViewer.status.keepVisibleNodeIds.append( tree.id )

        determineCollapsedNodes( \
            numberOfTips - maxTips,
            session.TreeViewer.status.keepVisibleNodeIds,
            renderInfo,
            collapsedNodeInfo )
        
        session.TreeViewer.status.keepVisibleNodeIds.pop()

        for colNode in collapsedNodeInfo:

            if( 'alreadyCollapsed' not in colNode ):
                node = renderInfo.nodeInfo[ colNode[ 'nodeId' ] ]
                descendantLabels = [ ]
                gatherLabels =  True if node['descendantLabelCount'] < session.TreeViewer.config.collapsedCladeSearchThreshold else False

                for childId in node['children']:
                    removeNodeAndDescendants( renderInfo, childId, gatherLabels, descendantLabels )

                renderInfo.nodeRef[ colNode['nodeId'] ].children = []
                renderInfo.nodeInfo[ colNode['nodeId'] ]['children'] = []
                renderInfo.nodeInfo[ colNode['nodeId'] ]['descendantLabels'] = descendantLabels
    
    return collapsedNodeInfo


def removeNodeAndDescendants( renderInfo, nodeId, gatherLabels, descendantLabels ):
   
    for childId in renderInfo.nodeInfo[ nodeId ]['children']:
        removeNodeAndDescendants( renderInfo, childId, gatherLabels, descendantLabels )

    if gatherLabels and len( renderInfo.nodeInfo[ nodeId ]['text'] ):
        descendantLabels.append( dict( text = renderInfo.nodeInfo[ nodeId ]['text'], id = nodeId ) )         

    del renderInfo.nodeRef[ nodeId ]
    del renderInfo.nodeInfo[ nodeId ]


def determineCollapsedNodes( tipsToCollapse, keepVisibleNodeIds, renderInfo, collapsedNodeInfo ):

    for id in reversed( renderInfo.collapseOrder.ids ):

        nodeInfo = renderInfo.nodeInfo[id]

        if( id not in keepVisibleNodeIds ):

            toCollapse = True

            for colNode in collapsedNodeInfo:

                if( colNode['nodeId'] == id ):
                    toCollapse = False
                    break

                if( util.isAncestor( Storage( next = colNode['next'], back = colNode['back'] ),
                                     Storage( next = nodeInfo['next'], back = nodeInfo['back'] ) ) ):
                    toCollapse = False
                    break


            if( toCollapse ):

                tipsAlreadyCollapsedByDescendants = 0
    
                for colNode in collapsedNodeInfo:

                    if( util.isDescendant( Storage( next = colNode['next'], back = colNode['back'] ),
                                           Storage( next = nodeInfo['next'], back = nodeInfo['back'] ) ) ):
    
                        tipsAlreadyCollapsedByDescendants += colNode['descendantTipCount']
                        collapsedNodeInfo.remove( colNode )


                tipsToCollapse = tipsToCollapse - nodeInfo['descendantTipCount'] + tipsAlreadyCollapsedByDescendants
                
                collapsedNodeInfo.append( nodeInfo )

                if( tipsAlreadyCollapsedByDescendants == 0 ):
                    tipsToCollapse += 1
                
                if( tipsToCollapse <= 0 ):
                    break;

def determineLeftLabelBuffer( renderInfo, branchLength, widthMetric ):

    leftMost = 0
   
    for ( depth, longestLabelLength ) in renderInfo.longestLabelAtDepth.iteritems():

            xCoord = ( depth * branchLength ) - ( longestLabelLength * widthMetric )

            if( xCoord < leftMost ):
                leftMost = xCoord

    return leftMost


def getLongestTipLabel( nodeInfo ):

    longest = 0

    for ( nodeId, info ) in nodeInfo.iteritems():

        if( ( len( info['children'] ) == 0 ) and
            ( len( info['text'] ) > longest ) ):

            longest = len( info[ 'text' ] )

    return longest


def getUnprocessedCladeResponse( session, tree, renderInfo, collapsedNodeRecs ):

    config = session.TreeViewer.config

    #this needs to handle dynamic branch lengths
    leftLabelBuffer = determineLeftLabelBuffer( renderInfo, config.branchLength, session.textWidthMetric  )          

    treeWidth = config.branchLength * renderInfo.depth

    totalNodes = ( tree.back - tree.next - 1 ) / 2

    numberOfTips = renderInfo.nodeInfo[ tree.id ]['descendantTipCount']
    heightAddedByCollapseUI = 0
    collapsedNodeDict = dict()
    collapsedNodeIds = [ ]

    for nodeRec in collapsedNodeRecs:
        collapseRec = collapsedNodeDict[ nodeRec['nodeId' ] ] = dict()

        collapseRec['closestDescendantLabel'] = nodeRec[ 'closestDescendantLabel' ]
        collapseRec['descendantLabelCount'] = nodeRec[ 'descendantLabelCount' ]
        collapseRec['descendantLabels'] = nodeRec[ 'descendantLabels' ] if 'descendantLabels' in nodeRec else [ ]
        collapseRec['descendantCount'] = int( math.floor( ( nodeRec['back'] - nodeRec['next'] - 1 ) / 2 ) )
        collapseRec['collapseUIHeightByTwo'] = ( math.log( collapseRec['descendantCount'] ) / math.log( totalNodes ) ) * ( config.verticalTipBuffer / 2 )

        collapsedNodeIds.append( nodeRec['nodeId'] )

        if( 'heightAdded' in nodeRec ):
            heightAddedByCollapseUI += nodeRec['heightAdded']
        
        if( 'alreadyCollapsed' not in nodeRec ):
            numberOfTips -= ( nodeRec['descendantTipCount'] - 1 )
            session.TreeViewer.status.collapsedNodeDict[ nodeRec[ 'nodeId' ] ] = nodeRec

    
    #only do this for navigate mode
    longestTipLabel = getLongestTipLabel( renderInfo.nodeInfo )

    canvasWidth = treeWidth + ( config.horizontalPadding * 2 ) + ( longestTipLabel * session.textWidthMetric ) + ( config.tipLabelBuffer - leftLabelBuffer )

    canvasHeight = ( config.verticalTipBuffer * numberOfTips ) + ( config.verticalPadding * 2 ) + heightAddedByCollapseUI

    pathString = None
      
    if( config.branchLengthStyle == 'scale' ):
        config.scaledBranchMultiplier = treeWidth / renderInfo.longestTraversal
        pathString = setScaledNodeCoordsAndPathString( tree, session.TreeViewer.config, collapsedNodeDict, totalNodes, renderInfo.nodeInfo )
    else: 
        pathString = setSmoothNodeCoordsAndPathString( tree, session.TreeViewer.config, collapsedNodeDict, renderInfo.depth, totalNodes, renderInfo.nodeInfo )

    return dict( canvas = dict( x = canvasWidth, y = canvasHeight ),
                 rootId = tree.id,
                 pathString = pathString,
                 collapsedNodeIds = collapsedNodeIds,
                 nodeInfo = renderInfo.nodeInfo )


def getPathStringForNode( nodeInfo, allNodeInfo ):

    returnString = [ ]

    strX = str( nodeInfo['x'] )
    strDX = str( nodeInfo['dx'] )
    strY = str( nodeInfo['y'] )

    if( len( nodeInfo['children'] ) > 0 ): 
        returnString.append( ''.join( [ 'M', strX, ' ', str( allNodeInfo[ nodeInfo['children'][0] ]['y'] ), 'L', strX, ' ', str( allNodeInfo[ nodeInfo['children'][ len( nodeInfo['children']) - 1 ] ]['y'] ) ] ) )
    
    returnString.append( ''.join( [ 'M', strX, ' ', strY, 'h', strDX ] ) )

    return ''.join( returnString )

def setScaledNodeCoordsAndPathString( tree, config, collapsedNodeDict, totalNodes, nodeInfo ):

    pathString = []

    nodeDict = nodeInfo[ tree.id ]

    nodeDict['x'] = config.horizontalPadding

    if( tree.next == 1 ):
        nodeDict['dx'] -( config.branchLength )
    else:
        distance = tree.length * config.scaledBranchMultiplier
        nodeDict['dx'] = -( distance )
    
    firstTip = Storage( y = session.TreeViewer.config.verticalPadding )

    for child in tree.children:
        setScaledNodeCoordsAndPathStringRecurse( child, config, firstTip, collapsedNodeDict, totalNodes, nodeInfo, pathString )
   
    nodeDict['y'] = ( ( nodeInfo[ tree.children[ -1 ].id ]['y'] + nodeInfo[ clade.children[ 0 ].id ]['y'] ) / 2 )

    pathString.append( getPathStringForNode( nodeDict, nodeInfo ) )

    return ''.join( pathString )


def setScaledNodeCoordsAndPathStringRecurse( node, config, curTip, collapsedNodeDict, totalNodes, nodeInfo, pathString ):

    nodeDict = nodeInfo[ node.id ]

    distance = node.length * config.scaledBranchMultiplier

    nodeDict['x'] = nodeInfo[ node.parent.id ]['x'] + distance
    nodeDict['dx'] = -( distance )
       
    for child in node.children:
        setScaledNodeCoordsAndPathStringRecurse( child, config, curTip, collapsedNodeDict, totalNodes, nodeInfo, pathString )

    if( node.children ):
        nodeDict['y'] = ( ( nodeInfo[ node.children[ -1 ].id ]['y'] + nodeInfo[ node.children[ 0 ].id ]['y'] ) / 2 )
    else:
        nodeDict['y'] = curTip.y

        if( node.id in collapsedNodeDict ):

            assignCollapseDetail( nodeDict, collapsedNodeDict[ node.id ], config, curTip, totalNodes )

            nodeDict['collapsed'] = collapsedNodeDict[ node.id ]

        curTip.y += config.verticalTipBuffer
    
    pathString.append( getPathStringForNode( nodeDict, nodeInfo ) )





def assignCollapseDetail( nodeDict, infoDict, config, curTip, totalNodes ):
    """
    This function gets the path string of a collapsed node UI and makes adjustments to its
    neighboring tips if the UI is larger than the normal vertical tip buffer
    """
    
    difference = ( infoDict['collapseUIHeightByTwo'] * 2 ) - config.verticalTipBuffer

    if( difference > 0 ):
        
        nodeDict['y'] += ( difference / 2 )
   
        infoDict['heightAdded'] = difference 
        curTip.y += difference

    infoDict['text'] = ''.join( [ infoDict['closestDescendantLabel'], ' (', str( infoDict['descendantCount'] ), ' nodes)' ] )
    infoDict['pathString'] = getCollapseUIPathString( nodeDict, infoDict )


def getCollapseUIPathString( nodeDict, infoDict ):
    """
    This function computes the path string of a collapsed node UI
    """
   
    return ''.join( [ "M", str( nodeDict['x'] + nodeDict['dx'] ), ' ', str( nodeDict['y'] ),
                      "l", str( - nodeDict['dx'] ), ' ', str( - infoDict['collapseUIHeightByTwo'] ),
                      'l0 ', str( 2 * infoDict['collapseUIHeightByTwo'] ), 'z' ] )



def setSmoothNodeCoordsAndPathString( tree, config, collapsedNodeDict, depth, totalNodes, nodeInfo ):

    pathString = [ ]

    firstTip = Storage( x = ( config.branchLength * depth ) + config.horizontalPadding,
                        y = config.verticalPadding )

    setSmoothNodeCoordsAndPathStringRecurse( tree, nodeInfo, config, collapsedNodeDict, firstTip, depth, totalNodes )

    for id in nodeInfo:
        pathString.append( getPathStringForNode( nodeInfo[id], nodeInfo ) )

    return ''.join( pathString )


def setSmoothNodeCoordsAndPathStringRecurse( node, nodeInfo, config, collapsedNodeDict, currentTip, currentDepth, totalNodes ):
    """
    A function that recurses through a tree adding node coordinates and labels to a dictionary where the keys are node ids.
    """

    nodeDict = nodeInfo[ node.id ]

    for child in node.children:
        setSmoothNodeCoordsAndPathStringRecurse( child, nodeInfo, config, collapsedNodeDict, currentTip, currentDepth - 1, totalNodes )

    if( len( nodeDict['children'] ) > 0 ):

        nodeDict['x'] = nodeInfo[ nodeDict['children'][0] ]['x'] + nodeInfo[ nodeDict['children'][0] ]['dx']
        nodeDict['dx'] = -( config.branchLength ) 
        nodeDict['y'] = ( nodeInfo[ nodeDict['children'][ -1 ] ]['y'] + nodeInfo[ nodeDict['children'][ 0 ] ]['y'] ) / 2

    else:

        nodeDict['x'] = currentTip.x
        nodeDict['dx'] = -( config.branchLength * currentDepth )
        nodeDict['y'] = currentTip.y

        if( node.id in collapsedNodeDict ):

            assignCollapseDetail( nodeDict, collapsedNodeDict[ node.id ], config, currentTip, totalNodes )

            nodeDict['collapsed'] = collapsedNodeDict[ node.id ]

        currentTip.y += config.verticalTipBuffer

    for child in node.children:
       
        if len( child.children ) == 0:
            continue

        closestChildX = None

        for grandkid in child.children:
            if( ( closestChildX is None ) or ( nodeInfo[ grandkid.id]['x'] < closestChildX ) ):
                closestChildX = nodeInfo[ grandkid.id ]['x']

        nodeInfo[ child.id ]['x'] = ( nodeDict['x'] + closestChildX ) / 2;
        nodeInfo[ child.id ]['dx'] = nodeDict['x'] - nodeInfo[ child.id ]['x']

        for grandkid in child.children:
            nodeInfo[ grandkid.id ]['dx'] = nodeInfo[ child.id ]['x'] - nodeInfo[ grandkid.id ]['x']

            if( 'collapsed' in nodeInfo[ grandkid.id ] ):
                info = nodeInfo[ grandkid.id ]['collapsed']
                info['pathString'] = getCollapseUIPathString( nodeInfo[ grandkid.id ], info )
    
