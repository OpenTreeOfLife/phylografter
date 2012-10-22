import bisect, math, sys, build
from gluon.storage import Storage
import plugin_treeViewer as util

def getTree( db, session, request ):

    response = [ ]

    for index in range( len( session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].columns ) ):
       
        columnInfo = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].columns[ index ]

        response.append( \
            getRenderResponse( \
                getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, session, columnInfo.rootNodeId, columnInfo.collapsedNodeStorage ),
                session,
                columnInfo ) )

    return response


def collapseClade( db, session, request ):

    collapsingNodeId = int( request.vars.nodeId )
    columnIndex = int( request.vars.columnIndex )

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]

    if( collapsingNodeId in treeState.formerlyCollapsedNodeStorage ):

        treeState.columns[ columnIndex ].collapsedNodeStorage[ collapsingNodeId ] = treeState.formerlyCollapsedNodeStorage[ collapsingNodeId ]

    else:

        collapsingClade = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, session, collapsingNodeId, Storage() )

        renderInfo = getattr( sys.modules[__name__], ''.join( [ 'getRenderInfoFor', session.TreeViewer.viewInfo['mode'].capitalize(), 'Mode' ] ) )( collapsingClade )

        collapsedCladeInfo = renderInfo.nodeInfo[ collapsingNodeId ]

        if( collapsedCladeInfo['descendantLabelCount'] < session.TreeViewer.config.collapsedCladeSearchThreshold ):
            
            collapsedCladeInfo['descendantLabels'] = util.getDescendantLabels( collapsingClade )
        
        treeState.columns[ columnIndex ].collapsedNodeStorage[ collapsingNodeId ] = collapsedCladeInfo

    return getRenderResponse( \
        getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, session,
                                                                                   treeState.columns[ columnIndex ].rootNodeId,
                                                                                   treeState.columns[ columnIndex ].collapsedNodeStorage ),
        session,
        treeState.columns[ columnIndex ] )


def addColumn( db, session, request ):

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]

    columnRootNodeId = request.vars.rootNodeId if len( treeState.columns ) != 0 else session.TreeViewer.rootNodeId

    treeState.columns.append( \
        Storage( rootNodeId = columnRootNodeId,
                 keepVisibleNodeStorage = Storage(),
                 collapsedNodeStorage = Storage() ) )



def removeColumns( db, session, request ):

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]

    start = int( request.vars.start )
    end = int( request.vars.end )

    for i in range( int( end ), int( start - 1 ), -1 ):
        removeColumn( treeState, i )

        

def removeColumn( treeState, i ):
    for nodeId, collapsedNodeData in treeState.columns[ i ].collapsedNodeStorage.items():
        if nodeId not in treeState.formerlyCollapsedNodeStorage:
            treeState.formerlyCollapsedNodeStorage[ nodeId ] = collapsedNodeData

    treeState.columns.pop( i )


def horizontallyExpandNode( db, session, request ):

    expandingNodeId = int( request.vars.nodeId )
    columnIndex = int( request.vars.columnIndex )
    
    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]

    newColumnInfo = treeState.columns[ -1 ]
    
    if request.vars.navigateToNodeId:

        nTbl = session.TreeViewer.strNodeTable

        navToNodeRow = \
            db.executesql( \
                ''.join( [ \
                    'SELECT ', nTbl, '.next, ', nTbl, '.back ',
                    'FROM ', nTbl, ' ',
                    'WHERE ', nTbl, '.id = ', str( request.vars.navigateToNodeId ) ] ) )[0]

        sqlString = [ \
            'SELECT ', nTbl, '.id ',
            'FROM ', nTbl, ' ',
            'WHERE ( ', nTbl, '.tree = ', str( session.TreeViewer.treeId ), ' ) AND ( ',
            nTbl, '.next < ', str( navToNodeRow[0] ), ' ) AND ( ',
            nTbl, '.back > ', str( navToNodeRow[1] ), ' );' ]

        for rec in db.executesql( ''.join( sqlString ) ):

            newColumnInfo.keepVisibleNodeStorage[ int( rec[0] ) ] = True

    return getRenderResponse( \
        getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, session, newColumnInfo.rootNodeId, newColumnInfo.collapsedNodeStorage ),
        session,
        newColumnInfo )


def verticallyExpandNode( db, session, request ):

    expandingNodeId = int( request.vars.nodeId )

    columnIndex = int( request.vars.columnIndex )

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]

    session.TreeViewer.treeConfig[ session.TreeViewer.treeId ].maxTips.value = session.TreeViewer.config.maxTips.value = \
        session.TreeViewer.config.maxTips.value * 1.5

    treeState.columns[ columnIndex ].keepVisibleNodeStorage[ expandingNodeId ] = True
    
    if( treeState.columns[ columnIndex ].rootNodeId != expandingNodeId ):
        for id in request.vars.ancestorIds.split(':'):
            treeState.columns[ columnIndex ].keepVisibleNodeStorage[ int( id ) ] = True

    if( expandingNodeId not in treeState.formerlyCollapsedNodeStorage ):
        treeState.formerlyCollapsedNodeStorage[ expandingNodeId ] = treeState.columns[ columnIndex ].collapsedNodeStorage[ expandingNodeId ]

    del treeState.columns[ columnIndex ].collapsedNodeStorage[ expandingNodeId ]

    if( ( ( len( treeState.columns ) - 1 ) > columnIndex ) and ( treeState.columns[ columnIndex + 1 ].rootNodeId == expandingNodeId ) ):
        while( ( len( treeState.columns ) - 1 ) > columnIndex ):
            treeState.columns.pop()

    return getRenderResponse( \
        getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, session, treeState.columns[ columnIndex ].rootNodeId, treeState.columns[ columnIndex ].collapsedNodeStorage ),
        session,
        treeState.columns[ columnIndex ] )


def navigateToNode( db, session, request ):

    nodeId = int( request.vars.nodeId )
    
    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]

    nodeTable = db.snode if session.TreeViewer.treeType == 'source' else db.gnode
    nodeRec = db( nodeTable.id == nodeId ).select()[0]

    for rec in db( ( nodeTable.next < nodeRec.next ) &
                   ( nodeTable.back > nodeRec.back ) &
                   ( nodeTable.tree == session.TreeViewer.treeId ) ).select().as_list():

        treeState.columns[ 0 ].keepVisibleNodeStorage[ rec['id'] ] = True

        if( rec['id'] in treeState.columns[ 0 ].collapsedNodeStorage ):
            if( rec['id'] not in treeState.formerlyCollapsedNodeStorage ):
                treeState.formerlyCollapsedNodeStorage[ rec['id'] ] = treeState.columns[ 0 ].collapsedNodeStorage[ rec['id'] ]
            del treeState.columns[ 0 ].collapsedNodeStorage[ rec['id'] ]

    return getRenderResponse( \
        getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) ) \
            ( db, session, treeState.columns[ 0 ].rootNodeId, treeState.columns[ 0 ].collapsedNodeStorage ),
        session,
        treeState.columns[ 0 ] )



def getRenderResponse( tree, session, columnInfo ):
   
    mode = session.TreeViewer.viewInfo['mode'].capitalize()
    
    renderInfo = getattr( sys.modules[__name__], ''.join( [ 'getRenderInfoFor', mode, 'Mode' ] ) )( tree )

    getattr( sys.modules[__name__], ''.join( [ 'determineTreeToRenderFor', mode, 'Mode' ] ) )( tree, renderInfo, session, columnInfo )

    return getCladeResponse( session, tree, renderInfo, columnInfo )


def getRenderInfoForNavigateMode( tree ):

    renderInfo = \
        Storage( depth = 0,
                 longestTraversal = 0,
                 nodeInfo = dict(),
                 nodeRef = Storage(),
                 longestLabelAtDepth = Storage(),
                 leafIds = [ ],
                 collapseOrder = Storage( weights = [], ids = [] ) )

    renderInfo.longestTraversal = recurseForInfoNavigateMode( renderInfo, tree, Storage( generation = 1 ) ).longestTraversal

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
   
    node.text = text = node.taxon if node.taxon else node.label if node.label else ''

    nodeInfo = renderInfo.nodeInfo[ node.id ] = \
        dict( text = text,
              next = node.next,
              back = node.back,
              nodeId = node.id,
              children = [ child.id for child in node.children ],
              parent = node.parent.id if node.parent else '' )

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

    
        nodeInfo['descendantLabelCount'] = currentIterationInfo.descendantLabelCount

    else:
        
        renderInfo.leafIds.append( node.id )

        currentIterationInfo.descendantTipCount += 1 
        currentIterationInfo.distanceFromLeaf = 1 

        if( node.length ):
            currentIterationInfo.longestTraversal = node.length


        if( text ):
            currentIterationInfo.closestDescendantLabel = text
            currentIterationInfo.descendantLabelCount += 1
        
        
    nodeInfo['descendantTipCount'] = currentIterationInfo.descendantTipCount
    node.longestTraversal = currentIterationInfo.longestTraversal


    return Storage( distanceFromLeaf = currentIterationInfo.distanceFromLeaf,
                    descendantTipCount = currentIterationInfo.descendantTipCount,
                    descendantLabelCount = currentIterationInfo.descendantLabelCount,
                    closestDescendantLabel = currentIterationInfo.closestDescendantLabel,
                    longestTraversal = currentIterationInfo.longestTraversal )
  

def allRootChildrenCollapsed( tree, collapsedNodeStorage, nodesToCollapseStorage ):

    combined = dict( collapsedNodeStorage.items() + nodesToCollapseStorage.items() )

    for child in tree.children:

        childCollapsed = False

        for ( nodeId, collapsedNodeData ) in combined.items():

            if( ( nodeId == child.id ) or ( len( child.children ) == 0 ) ):
        
                childCollapsed = True
                break
                
        if( not childCollapsed ):

            return False

    return True


def determineTreeToRenderForNavigateMode( tree, renderInfo, session, columnInfo ):

    numberOfTips = renderInfo.nodeInfo[ tree.id ]['descendantTipCount']
    maxTips = session.TreeViewer.config.maxTips.value;
        
    renderInfo.tipsRemoved = 0

    if( numberOfTips > maxTips ):

        columnInfo.keepVisibleNodeStorage[ tree.id ] = True

        nodesToCollapseStorage = determineCollapsedNodes( \
            session,
            renderInfo,
            numberOfTips - maxTips,
            columnInfo )

        if( allRootChildrenCollapsed( tree, columnInfo.collapsedNodeStorage, nodesToCollapseStorage ) ):
       
            for child in tree.children:
                if( child.id in nodesToCollapseStorage ):
                    columnInfo.keepVisibleNodeStorage[ child.id ] = True
       
            nodesToCollapseStorage = determineCollapsedNodes( \
               session,
               renderInfo,
               numberOfTips - maxTips,
               columnInfo )

        for ( nodeId, collapsedNodeData ) in nodesToCollapseStorage.items():

            node = renderInfo.nodeInfo[ nodeId ]

            renderInfo.tipsRemoved += ( collapsedNodeData['descendantTipCount'] - 1 )

            descendantLabels = [ ]
            gatherLabels =  True if node['descendantLabelCount'] < session.TreeViewer.config.collapsedCladeSearchThreshold else False

            for childId in node['children']:
                removeNodeAndDescendants( \
                    renderInfo,
                    childId,
                    gatherLabels,
                    descendantLabels )

            renderInfo.nodeInfo[ nodeId ]['children'] = []
            renderInfo.nodeInfo[ nodeId ]['descendantLabels'] = descendantLabels

            columnInfo.collapsedNodeStorage[ nodeId ] = collapsedNodeData

         
def removeNodeAndDescendants( renderInfo, nodeId, gatherLabels, descendantLabels ):
   
    for childId in renderInfo.nodeInfo[ nodeId ]['children']:
        removeNodeAndDescendants( renderInfo, childId, gatherLabels, descendantLabels )

    if gatherLabels and len( renderInfo.nodeInfo[ nodeId ]['text'] ):
        descendantLabels.append( dict( text = renderInfo.nodeInfo[ nodeId ]['text'], id = nodeId ) )

    del renderInfo.nodeRef[ nodeId ]
    del renderInfo.nodeInfo[ nodeId ]


def determineCollapsedNodes( session, renderInfo, tipsToCollapse, columnInfo ):
    
    formerlyCollapsedNodeStorage = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].formerlyCollapsedNodeStorage

    nodesToCollapseStorage = Storage()

    for id in reversed( renderInfo.collapseOrder.ids ):

        nodeInfo = renderInfo.nodeInfo[id]

        if( id not in columnInfo.keepVisibleNodeStorage ):

            toCollapse = True

            combined = dict( columnInfo.collapsedNodeStorage.items() + nodesToCollapseStorage.items() )

            for ( nodeId, collapsedNodeData ) in combined.items():

                if( nodeId == id ):
                    toCollapse = False
                    break

                if( util.isAncestor( collapsedNodeData, nodeInfo ) ):
                    toCollapse = False
                    break


            if( toCollapse ):

                tipsAlreadyCollapsedByDescendants = 0
    
                for ( nodeId, collapsedNodeData ) in columnInfo.collapsedNodeStorage.items():

                    if( util.isDescendant( Storage( next = collapsedNodeData['next'], back = collapsedNodeData['back'] ),
                                           Storage( next = nodeInfo['next'], back = nodeInfo['back'] ) ) ):
    
                        tipsAlreadyCollapsedByDescendants += collapsedNodeData['descendantTipCount']

                        if nodeId not in formerlyCollapsedNodeStorage:
                            formerlyCollapsedNodeStorage[ nodeId ] = columnInfo.collapsedNodeStorage[ nodeId ]
                        del columnInfo.collapsedNodeStorage[ nodeId ]

                tipsToCollapse = tipsToCollapse - nodeInfo['descendantTipCount'] + tipsAlreadyCollapsedByDescendants


                for ( nodeId, collapsedNodeData ) in nodesToCollapseStorage.items():

                    if( util.isDescendant( Storage( next = collapsedNodeData['next'], back = collapsedNodeData['back'] ),
                                           Storage( next = nodeInfo['next'], back = nodeInfo['back'] ) ) ):
                        del nodesToCollapseStorage[ nodeId ]


                nodesToCollapseStorage[ id ] = nodeInfo

                if( tipsAlreadyCollapsedByDescendants == 0 ):
                    tipsToCollapse += 1
                
                if( tipsToCollapse <= 0 ):
                    break;

    return nodesToCollapseStorage


def determineLeftLabelBuffer( renderInfo, branchLengthStyle, branchLength, widthMetric, scaledBranchMultiplier ):

    leftMost = 0

    if( branchLengthStyle == 'smooth' ):
           
        for ( depth, longestLabelLength ) in renderInfo.longestLabelAtDepth.iteritems():

                xCoord = ( depth * branchLength ) - ( longestLabelLength * widthMetric )

                if( xCoord < leftMost ):
                    leftMost = xCoord

    elif( branchLengthStyle == 'scale' ):
        
        for ( nodeId, node ) in renderInfo.nodeRef.iteritems():

            if( len( node.children ) ):

                xCoord = ( node.longestTraversal * scaledBranchMultiplier ) - ( len( node.text ) * widthMetric )

                if( xCoord < leftMost ):
                    leftMost = xCoord

    return math.fabs( leftMost )


def getDepthAndLongestTipLabel( renderInfo, collapsedNodeDict ):

    depth = 0
    longestTip = 0

    for nodeId in renderInfo.leafIds:
        
        if( nodeId in renderInfo.nodeRef ):
           
            nodeRef = renderInfo.nodeRef[ nodeId ]

            if( nodeRef.depth > depth ):
                depth = nodeRef.depth

            if( len( nodeRef.text ) > longestTip ):
                longestTip = len( nodeRef.text )

   
    for ( nodeId, colData ) in collapsedNodeDict.items():

        if( nodeId in renderInfo.nodeRef ):

            nodeRef = renderInfo.nodeRef[ nodeId ]

            if( nodeRef.depth > depth ):
                depth = nodeRef.depth
               
            if( len( colData['text'] ) > longestTip ):
                longestTip = len( colData['text'] )
            
    return ( depth, longestTip )


def updateLongestTraversal( renderInfo, rootId ):

    renderInfo.longestTraversal = updateLongestTraversalRecurse( renderInfo, rootId )


def updateLongestTraversalRecurse( renderInfo, nodeId ):

    longestTraversal = 0

    for childId in renderInfo.nodeInfo[ nodeId ]['children']:
        childTraversal = updateLongestTraversalRecurse( renderInfo, childId )

        if( childTraversal > longestTraversal ):
            longestTraversal = childTraversal

    if( renderInfo.nodeRef[ nodeId ].length ):
        longestTraversal += renderInfo.nodeRef[ nodeId ].length

    return longestTraversal
    

def processCollapsedNodeInfo( nodeDictionary, totalNodeCount, config, session, columnInfo ):

    heightAdded = 0
    collapsedNodeDictionary = dict()
    collapsedNodeIds = [ ]

    for ( nodeId, nodeData ) in columnInfo.collapsedNodeStorage.items():

        if( nodeId in nodeDictionary ):

            ref = collapsedNodeDictionary[ nodeId ] = dict()

            ref['closestDescendantLabel'] = nodeData[ 'closestDescendantLabel' ]
            ref['descendantLabelCount'] = nodeData[ 'descendantLabelCount' ]
            ref['descendantLabels'] = nodeData[ 'descendantLabels' ] if 'descendantLabels' in nodeData else [ ]
            ref['descendantCount'] = int( math.floor( ( nodeData['back'] - nodeData['next'] - 1 ) / 2 ) )
            ref['collapseUIHeightByTwo'] = ( math.log( ref['descendantCount'] ) / math.log( totalNodeCount ) ) * ( config.verticalTipBuffer.value / 2 )

            if( not nodeData[ 'text' ] ):
                ref['text'] = ''.join( [ ref['closestDescendantLabel'], ' (', str( ref['descendantCount'] ), ' nodes)' ] )
            else:
                ref['text'] = ''.join( [ '(', str( ref['descendantCount'] ), ' nodes)' ] )

            difference = ( ref['collapseUIHeightByTwo'] * 2 ) - config.verticalTipBuffer.value

            if( difference > 0 ):
                ref['heightAdded'] = difference 
                heightAdded += difference
            
            collapsedNodeIds.append( nodeId )

    return ( heightAdded, collapsedNodeDictionary, collapsedNodeIds )


def getScaleBranchStyleResponse( session, tree, renderInfo, collapsedNodeDictionary, collapsedNodeIds ):

    config = session.TreeViewer.config

    #if in navigate mode(if we collapsed stuff)
    updateLongestTraversal( renderInfo, tree.id )

    renderInfo.treeWidth = None

    if( not renderInfo.nodeRef[ tree.id ].length ):
        scaledTreeSize = config.branchLength.value * ( renderInfo.depth - 1 )
        renderInfo.treeWidth = scaledTreeSize + config.branchLength.value
    else:
        renderInfo.treeWidth = scaledTreeSize = ( config.branchLength.value * renderInfo.depth )
    
    if( renderInfo.longestTraversal == 0 ):
        renderInfo.longestTraversal = config.branchLength.value
            
    renderInfo.scaledBranchMultiplier = scaledTreeSize / renderInfo.longestTraversal
        
    renderInfo.leftLabelBuffer = \
        determineLeftLabelBuffer( \
            renderInfo,
            config.branchLengthStyle,
            config.branchLength.value,
            session.textWidthMetric,
            renderInfo.scaledBranchMultiplier  )          

    canvasSize = getCanvasSize( renderInfo, config, session )

    pathString = setScaledNodeCoordsAndPathString( \
        tree.id,
        config,
        collapsedNodeDictionary,
        renderInfo.totalNodes,
        renderInfo.nodeInfo,
        renderInfo.nodeRef,
        canvasSize,
        renderInfo.scaledBranchMultiplier )

    return dict( canvas = canvasSize,
                 rootId = tree.id,
                 pathString = pathString,
                 collapsedNodeIds = collapsedNodeIds,
                 nodeInfo = renderInfo.nodeInfo )


def getCanvasSize( renderInfo, config, session ):

    return dict( width = renderInfo.treeWidth + \
                     ( config.horizontalPadding * 2 ) + \
                     ( renderInfo.longestTipLabel * session.textWidthMetric ) + \
                     config.tipLabelBuffer + renderInfo.leftLabelBuffer,

                 height = ( config.verticalTipBuffer.value * renderInfo.numberOfTips ) + \
                     ( config.verticalPadding * 2 ) + \
                     renderInfo.heightAddedByCollapseUI )

def getSmoothBranchStyleResponse( session, tree, renderInfo, collapsedNodeDictionary, collapsedNodeIds ):

    config = session.TreeViewer.config

    renderInfo.treeWidth = config.branchLength.value * renderInfo.depth

    renderInfo.leftLabelBuffer = \
        determineLeftLabelBuffer( \
            renderInfo,
            config.branchLengthStyle,
            config.branchLength.value,
            session.textWidthMetric,
            renderInfo.scaledBranchMultiplier  )          

    pathString = \
        setSmoothNodeCoordsAndPathString( \
            tree.id,
            session.TreeViewer.config,
            collapsedNodeDictionary,
            renderInfo )

    return dict( canvas = getCanvasSize( renderInfo, config, session ),
                 rootId = tree.id,
                 pathString = pathString,
                 collapsedNodeIds = collapsedNodeIds,
                 nodeInfo = renderInfo.nodeInfo )


def getCladeResponse( session, tree, renderInfo, columnInfo ):

    config = session.TreeViewer.config

    totalNodes = ( tree.back - tree.next - 1 ) / 2

    ( renderInfo.heightAddedByCollapseUI, 
      collapsedNodeDictionary,
      collapsedNodeIds ) = processCollapsedNodeInfo( renderInfo.nodeInfo, totalNodes, config, session, columnInfo )

    renderInfo.numberOfTips = renderInfo.nodeInfo[ tree.id ]['descendantTipCount'] - renderInfo.tipsRemoved

    #only do this for navigate mode
    ( renderInfo.depth, renderInfo.longestTipLabel ) = getDepthAndLongestTipLabel( renderInfo, collapsedNodeDictionary )
  
    return getattr( sys.modules[ __name__ ],
           ''.join( [ 'get', config.branchLengthStyle.capitalize(),
                      'BranchStyleResponse' ] ) )( session, tree, renderInfo, collapsedNodeDictionary, collapsedNodeIds )
   

def getPathStringForNode( nodeInfo, allNodeInfo ):

    returnString = [ ]

    strX = str( nodeInfo['x'] )
    strDX = str( nodeInfo['dx'] )
    strY = str( nodeInfo['y'] )

    if( len( nodeInfo['children'] ) > 0 ): 
        returnString.append( ''.join( [ 'M', strX, ' ', str( allNodeInfo[ nodeInfo['children'][0] ]['y'] ), 'L', strX, ' ', str( allNodeInfo[ nodeInfo['children'][ len( nodeInfo['children']) - 1 ] ]['y'] ) ] ) )
    
    returnString.append( ''.join( [ 'M', strX, ' ', strY, 'h', strDX ] ) )

    return ''.join( returnString )


def setScaledNodeCoordsAndPathString( treeId, config, collapsedNodeDict, totalNodes, nodeInfo, nodeRef, canvasSize, scaledBranchMultiplier ):

    pathString = []

    nodeDict = nodeInfo[ treeId ]

    if( ( nodeDict['next'] == 1 ) and ( not nodeRef[ treeId ].length ) ):
        nodeDict['dx'] = -( config.branchLength.value )
    else:
        distance = nodeRef[ treeId ].length * scaledBranchMultiplier
        nodeDict['dx'] = -( distance )
    
    nodeDict['x'] = config.horizontalPadding + ( - nodeDict['dx'] )
    
    firstTip = Storage( y = config.verticalPadding )

    for childId in nodeDict['children']:
        setScaledNodeCoordsAndPathStringRecurse( childId, config, firstTip, collapsedNodeDict, totalNodes, nodeInfo, nodeRef, pathString, scaledBranchMultiplier )
  
    if( len( nodeDict[ 'children' ] ) ):
        nodeDict['y'] = ( ( nodeInfo[ nodeDict['children'][ -1 ] ]['y'] + nodeInfo[ nodeDict['children'][ 0 ] ]['y'] ) / 2 )
    else:
        nodeDict['y'] = ( canvasSize['height'] / 2 )
        assignCollapseDetail( nodeDict, collapsedNodeDict[ treeId ], config, firstTip, totalNodes, 'scaled' )
        nodeDict['collapsed'] = collapsedNodeDict[ treeId ]

    pathString.append( getPathStringForNode( nodeDict, nodeInfo ) )

    return ''.join( pathString )


def setScaledNodeCoordsAndPathStringRecurse( nodeId, config, curTip, collapsedNodeDict, totalNodes, nodeInfo, nodeRef, pathString, scaledBranchMultiplier ):

    nodeDict = nodeInfo[ nodeId ]

    distance = nodeRef[ nodeId ].length * scaledBranchMultiplier

    nodeDict['x'] = nodeInfo[ nodeDict['parent'] ]['x'] + distance
    nodeDict['dx'] = -( distance )
       
    for childId in nodeDict['children']:
        setScaledNodeCoordsAndPathStringRecurse( childId, config, curTip, collapsedNodeDict, totalNodes, nodeInfo, nodeRef, pathString, scaledBranchMultiplier )

    if( nodeDict['children'] ):
        nodeDict['y'] = ( ( nodeInfo[ nodeDict['children'][ -1 ] ]['y'] + nodeInfo[ nodeDict['children'][ 0 ] ]['y'] ) / 2 )
    else:
        nodeDict['y'] = curTip.y

        if( nodeId in collapsedNodeDict ):

            assignCollapseDetail( nodeDict, collapsedNodeDict[ nodeId ], config, curTip, totalNodes, 'scaled' )

            nodeDict['collapsed'] = collapsedNodeDict[ nodeId ]

        curTip.y += config.verticalTipBuffer.value
    
    pathString.append( getPathStringForNode( nodeDict, nodeInfo ) )



def refreshColumn( db, session, request ):

    columnInfo = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].columns[ int( request.vars.columnIndex ) ]

    return getRenderResponse( \
                getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, session, columnInfo.rootNodeId, columnInfo.collapsedNodeStorage ),
                session,
                columnInfo )


def assignCollapseDetail( nodeDict, infoDict, config, curTip, totalNodes, branching ):
    """
    This function gets the path string of a collapsed node UI and makes adjustments to its
    neighboring tips if the UI is larger than the normal vertical tip buffer
    """

    if( 'heightAdded' in infoDict ): 

        nodeDict['y'] += ( infoDict['heightAdded'] / 2 )

        curTip.y += infoDict['heightAdded']

    infoDict['branching'] = branching    
    infoDict['pathString'] = getCollapseUIPathString( nodeDict, infoDict, config, branching )


def getCollapseUIPathString( nodeDict, infoDict, config, branching ):
    """
    This function computes the path string of a collapsed node UI
    """

    if( branching == 'smooth' ):
        
        triangleWidth = -( nodeDict['dx'] )
        minimumWidth = config.minimumCollapsedUIWidth

        if( triangleWidth < minimumWidth ):
            triangleWidth = minimumWidth

        return ''.join( [ "M", str( nodeDict['x'] - triangleWidth ), ' ', str( nodeDict['y'] ),
                          "l", str( triangleWidth ), ' ', str( - infoDict['collapseUIHeightByTwo'] ),
                          'l0 ', str( 2 * infoDict['collapseUIHeightByTwo'] ), 'z' ] )

    elif( branching == 'scaled' ):

        return ''.join( [ "M", str( nodeDict['x'] + config.scaledBranchingCollapseUIBuffer ), ' ', str( nodeDict['y'] ),
                          "l", str( config.minimumCollapsedUIWidth ), ' ', str( - infoDict['collapseUIHeightByTwo'] ),
                          'l0 ', str( 2 * infoDict['collapseUIHeightByTwo'] ), 'z' ] )



def setSmoothNodeCoordsAndPathString( rootId, config, collapsedNodeDict, renderInfo ):

    pathString = [ ]

    firstTip = Storage( x = ( config.branchLength.value * renderInfo.depth ) + config.horizontalPadding + renderInfo.leftLabelBuffer,
                        y = config.verticalPadding )

    setSmoothNodeCoordsAndPathStringRecurse(
        rootId,
        renderInfo.nodeInfo,
        config,
        collapsedNodeDict,
        firstTip,
        renderInfo.depth,
        renderInfo.totalNodes )

    for id in renderInfo.nodeInfo:
        pathString.append( getPathStringForNode( renderInfo.nodeInfo[id], renderInfo.nodeInfo ) )

    return ''.join( pathString )


def setSmoothNodeCoordsAndPathStringRecurse( id, nodeInfo, config, collapsedNodeDict, currentTip, currentDepth, totalNodes ):
    """
    A function that recurses through a tree adding node coordinates and labels to a dictionary where the keys are node ids.
    """

    nodeDict = nodeInfo[ id ]

    for childId in nodeDict['children']:
        setSmoothNodeCoordsAndPathStringRecurse( childId, nodeInfo, config, collapsedNodeDict, currentTip, currentDepth - 1, totalNodes )

    if( len( nodeDict['children'] ) > 0 ):

        nodeDict['x'] = nodeInfo[ nodeDict['children'][0] ]['x'] + nodeInfo[ nodeDict['children'][0] ]['dx']
        nodeDict['dx'] = -( config.branchLength.value ) 
        nodeDict['y'] = ( nodeInfo[ nodeDict['children'][ -1 ] ]['y'] + nodeInfo[ nodeDict['children'][ 0 ] ]['y'] ) / 2

    else:

        nodeDict['x'] = currentTip.x
        nodeDict['dx'] = -( config.branchLength.value * currentDepth )
        nodeDict['y'] = currentTip.y

        if( id in collapsedNodeDict ):

            assignCollapseDetail( nodeDict, collapsedNodeDict[ id ], config, currentTip, totalNodes, 'smooth' )

            nodeDict['collapsed'] = collapsedNodeDict[ id ]

        currentTip.y += config.verticalTipBuffer.value

    for childId in nodeDict['children']:
       
        if len( nodeInfo[ childId ]['children'] ) == 0:
            continue

        closestChildX = None

        for grandkidId in nodeInfo[ childId ]['children']:
            if( ( closestChildX is None ) or ( nodeInfo[ grandkidId ]['x'] < closestChildX ) ):
                closestChildX = nodeInfo[ grandkidId ]['x']

        nodeInfo[ childId ]['x'] = ( nodeDict['x'] + closestChildX ) / 2;
        nodeInfo[ childId ]['dx'] = nodeDict['x'] - nodeInfo[ childId ]['x']


        for grandkidId in nodeInfo[ childId ]['children']:
            
            nodeInfo[ grandkidId ]['dx'] = nodeInfo[ childId ]['x'] - nodeInfo[ grandkidId ]['x']

            if( 'collapsed' in nodeInfo[ grandkidId ] ):
                info = nodeInfo[ grandkidId ]['collapsed']
                info['pathString'] = getCollapseUIPathString( nodeInfo[ grandkidId ], info, config, 'smooth' )
    
