import math, datetime, build, ivy
from gluon.storage import Storage
from ivy_local.tree import *
from pprint import pprint

def getTreeInfo( p ):

    p['info']['nodeDict'][ p['node'].id ] = p['node']
    
    curGeneration = p['generation']

    if( p['info']['depth'] < curGeneration ):
        p['info']['depth'] = curGeneration

    if curGeneration not in p['info']['depthTipCount']:
        p['info']['depthTipCount'][ curGeneration ] = 0
        
    if curGeneration not in p['info']['depthNodeCount']:
        p['info']['depthNodeCount'][ curGeneration ] = 1
    else:
        p['info']['depthNodeCount'][ curGeneration ] += 1
        
    myDescendants = 0
    myLevel = 0
    myDescendantTips = 0
    myDescendantLabels = [ ]
    hasDescendantLabel = False
        
    if p['node'].children:

        for child in p['node'].children:

            returnedInfo = getTreeInfo( { 'node': child, 'generation': curGeneration + 1, 'descendants': 0, 'info': p['info'] } )

            myDescendantLabels.extend( returnedInfo['descendantLabels'] )
            myDescendants += returnedInfo['descendants']
            myDescendantTips += returnedInfo['descendantTips']

            if( ( returnedInfo['level'] + 1 ) > myLevel ):
                myLevel = returnedInfo['level'] + 1
    
        p['node'].descendantLabels = myDescendantLabels
        p['node'].descendantCount = myDescendants
        p['node'].descendantTipCount = myDescendantTips

        if( returnedInfo['hasDescendantLabel'] ):
            hasDescendentLabel = True

        nodeWeight = ( myDescendantTips / float(myLevel) )
        if( returnedInfo['hasDescendantLabel'] ):
            nodeWeight *= .25
        p['info']['nodeWeights'].append( ( nodeWeight, p['node'] ) )
                
        if( p['node'].label ):
            canvasXLabel = ( curGeneration * p['info']['genSep'] ) - ( len( p['node'].label ) * p['info']['labelWidthMetric'] )

            if( canvasXLabel < p['info']['leftmostLabel'] ):
                p['info']['leftmostLabel'] = canvasXLabel

            hasDescendentLabel = True

    else:

        p['info']['tips'] += 1
        p['info']['depthTipCount'][ p['generation'] ] += 1
        
        myDescendantTips += 1
        myLevel = 1
    
        if( p['node'].label and len( p['node'].label ) > p['info']['longestTipLabel'] ):
            p['info']['longestTipLabel'] = len( p['node'].label )
            
    myDescendants += 1

    if( p['node'].label ):
        myDescendantLabels.append( { 'id': p['node'].id, 'label': p['node'].label } )

    return { 'descendants': myDescendants, 'descendantTips': myDescendantTips, 'descendantLabels': myDescendantLabels,
             'hasDescendantLabel': hasDescendantLabel, 'level': myLevel }


def getMaxGeneration( p ):

    maxTips = int( math.floor( ( p['viewerHeight'] - p['bufferY'] ) / p['tipSeparation'] ) )

    i = 1; runningTipCount = 0; currentTipCount = p['treeInfo']['depthNodeCount'][1];

    while( currentTipCount <= maxTips ):

       runningTipCount += p['treeInfo']['depthTipCount'][i]

       temp = runningTipCount + p['treeInfo']['depthNodeCount'][i + 1]

       if( temp <= maxTips ):
           i += 1
           currentTipCount = runningTipCount + p['treeInfo']['depthNodeCount'][i]
       else:
           break;
                
    return { 'maxGeneration': i, 'currentTipCount': currentTipCount, 'maxTips': maxTips }


def removeCollapsed( p ):

    if( str( p['node'].id ) in p['collapsed'] ):
        p['node'].children = []
    else:
        for child in p['node'].children:
            removeCollapsed( { 'node' : child, 'collapsed' : p['collapsed'] } )


def truncateTree( p ):

    currentNode = p['currentNode']
    currentGeneration = p['currentGeneration']
    stopGeneration = p['stopGeneration']
    currentTipCount = p['currentTipCount']

    newNode = currentNode.copy()
    newNode.parent = currentNode.parent
    newNode.children = []
  
    if( currentGeneration == stopGeneration ):
    
        if( currentNode.label ):
            return { 'tree': newNode, 'tipCount': currentTipCount }

        if( currentNode.parent and currentNode.parent.label ):
            return { 'msg': 'parent', 'tipCount': currentTipCount - currentNode.parent.children.length + 1 }
        
        if( currentNode.parent.parent and currentNode.parent.parent.label ):
            return { 'msg': 'grandparent', 'tipCount': currentTipCount - currentNode.parent.parent.descendantTipCount + 1 }

        return { 'tree': newNode, 'tipCount': currentTipCount }


    for child in currentNode.children:

        result = truncateTree( { 'currentGeneration': currentGeneration + 1,
                                 'currentNode': child,
                                 'currentTipCount': currentTipCount,
                                 'stopGeneration': stopGeneration } );
        
        if( 'tree' in result ):
            newNode.children.append( result['tree'] )
            currentTipCount = result['tipCount']

        elif( result['msg'] == 'parent' ):
            newNode.children = [];
            currentTipCount = result['tipCount']

        elif( result['msg'] == 'grandparent' ):
            return { 'msg': 'parent', 'tipCount': result['tipCount'] }

    return { 'tree': newNode, 'tipCount': currentTipCount }


def fillOutTree( p ):

    currentNode = p['currentNode']
    tipsToFill = p['tipsToFill']

    childCount = len( currentNode.children )
    
    if( childCount ):

        for child in currentNode.children:

            tipsToFill = fillOutTree( { 'tipsToFill': tipsToFill,
                                        'originalNodeDict': p['originalNodeDict'],
                                        'currentNode': child } );

    else:

        originalNode = p['originalNodeDict'][ currentNode.id ]
        childLength = len( originalNode.children )

        if( childLength != 0 and originalNode.descendantCount <= tipsToFill ):

            currentNode.children = originalNode.children
            tipsToFill = tipsToFill - originalNode.descendantTipCount + 1

        elif( childLength != 0 and childLength <= tipsToFill ):
                
            allChildLabels = True

            for child in originalNode.children:
                if( not child.label ):
                    allChildLabels = False
                    break


            if( allChildLabels ):
            
                currentNode.children = originalNode.children
                tipsToFill = tipsToFill - childLength - 1

                for child in currentNode.children:
                
                    child.children = []

                    tipsToFill = fillOutTree( { 'tipsToFill': tipsToFill,
                                                'originalNodeDict': p['originalNodeDict'],
                                                'currentNode': child } )
    return tipsToFill

def getTruncatedTreeInfo( p ):
    
    node = p['node']
    generation = p['generation']

    if( p['info']['depth'] < generation ):
        p['info']['depth'] = generation

    if( len( node.children ) ):
        
        for child in node.children:

            getTruncatedTreeInfo( { 'node': child,
                                    'info': p['info'],
                                    'generation': generation + 1 } )

        if( node.label ):
            canvasXLabel = ( generation * p['info']['genSep'] ) - ( len( node.label ) * p['info']['labelWidthMetric'] )

            if( canvasXLabel < p['info']['leftmostLabel'] ):
                p['info']['leftmostLabel'] = canvasXLabel

    else:
        
        p['info']['tips'] += 1;

        if( node.label and len( node.label ) > p['info']['longestTipLabel'] ):
            p['info']['longestTipLabel'] = len( node.label )


def getTreeClientInfo( p ):

    leftLabelBuffer = p['treeInfo']['leftmostLabel'] if p['treeInfo']['leftmostLabel'] < 0 else 0

    canvasWidth = ( p['config']['generationSeparation'] * p['treeInfo']['depth'] ) + \
                  p['config']['buffer']['2x'] + ( p['treeInfo']['longestTipLabel'] * p['labelWidthMetric'] ) + \
                  p['config']['tipLabelBuffer'] - leftLabelBuffer
    
    canvasHeight = ( p['config']['tipSeparation'] * p['treeInfo']['tips'] ) + p['config']['buffer']['2y']

    clientRenderInfo = {
         'currentTip': { 'x': canvasWidth - p['config']['buffer']['x'] - ( p['treeInfo']['longestTipLabel'] * p['labelWidthMetric'] ),
                         'y': p['config']['buffer']['y'] },
         'pathString': '',
         'expandableUI': [ ],
         'generationSeparation': p['config']['generationSeparation'],
         'totalNodes': p['tree'].descendantCount,
         'clientInfo': { },
         'tipSeparation': p['config']['tipSeparation'] }

    generatePathString( {
        'node': p['tree'],
        'depth': p['treeInfo']['depth'],
        'originalNodeDict': p['nodeDict'],
        'info': clientRenderInfo } )

    return { 'canvas': { 'x': canvasWidth, 'y': canvasHeight },
             'rootId': p['tree'].id,
             'pathString': clientRenderInfo['pathString'],
             'expandableUI': clientRenderInfo['expandableUI'],
             'config': { 'tipSeparation': p['config']['tipSeparation'],
                         'generationSeparation': p['config']['generationSeparation'] },
             'nodeInfo': clientRenderInfo['clientInfo'] }


def layout( p ):
    "calculate coordinates"
    node = p['node']
    children = node.children
    clientInfo = p['info']['clientInfo']
    
    for child in children:
        layout( {'node': child,
                 'depth': p['depth'] - 1,
                 'originalNodeDict': p['originalNodeDict'],
                 'info': p['info'] } )

    if children:

        clientInfo[ node.id ] = {
            'parent': node.parent.id if node.parent else None,
            'isInternal': True,
            'children': [ child.id for child in children ],
            'next': node.next,
            'back': node.back,
            'x': clientInfo[ children[0].id ]['x'] + clientInfo[ children[0].id ]['dx'],
            'dx': -( p['info']['generationSeparation'] ),
            'y': ( clientInfo[ children[ -1 ].id ]['y'] + clientInfo[ children[0].id ]['y'] ) / 2 }

    else:

        clientInfo[ node.id ] = {
            'parent': node.parent.id if node.parent else None,
            'isInternal': False,
            'children': [ ],
            'next': node.next,
            'back': node.back,
            'x': p['info']['currentTip']['x'],
            'dx': -( p['info']['generationSeparation'] * p['depth'] ),
            'y': p['info']['currentTip']['y'] }

        p['info']['currentTip']['y'] += p['info']['tipSeparation']
    
    if( node.label ):
        clientInfo[ node.id ]['label'] = node.label

def generatePathString( p ):

    node = p['node']
    node.ladderize()
    children = node.children
    clientInfo = p['info']['clientInfo']
    
    for child in children:
        p['pathStrings'] = \
            generatePathString( {
                'node': child,
                'depth': p['depth'] - 1,
                'originalNodeDict': p['originalNodeDict'],
                'info': p['info'] } )

    if children:

        clientInfo[ node.id ] = {
            'parent': node.parent.id if node.parent else None,
            'isInternal': True,
            'children': [ child.id for child in children ],
            'next': node.next,
            'back': node.back,
            'x': clientInfo[ children[0].id ]['x'] + clientInfo[ children[0].id ]['dx'],
            'dx': -( p['info']['generationSeparation'] ),
            'y': ( clientInfo[ children[ -1 ].id ]['y'] + clientInfo[ children[0].id ]['y'] ) / 2 }

        x = clientInfo[node.id]['x']
        y = clientInfo[node.id]['y']

        for child in children:
            cx = clientInfo[child.id]['x']
            cy = clientInfo[child.id]['y']

            s = " M%s,%s L%s,%s L%s,%s " % (cx,cy,x,cy,x,y)

            p['info']['pathString'] += s

        ## if len( children ) == 1:

        ##     p['info']['pathString'] += \
        ##         ''.join( [ "M", str( clientInfo[ node.id ]['x'] ), ',',
        ##                    str( clientInfo[ children[0].id ]['y'] - ( p['info']['tipSeparation'] / 4 ) ), "l0 ",
        ##                    str( p['info']['tipSeparation'] / 2 ) ] )

        ## else :
            
        ##     p['info']['pathString'] += \
        ##         ''.join( [ "M", str( clientInfo[ node.id ]['x'] ), ',', str( clientInfo[ children[0].id ]['y'] ),
        ##                    "L", str( clientInfo[ node.id ]['x'] ), ',', str( clientInfo[ children[-1].id ]['y'] ) ] )
        
        ## p['info']['pathString'] += \
        ##     ''.join( [ "M", str( clientInfo[ node.id ]['x'] ), ',', str( clientInfo[ node.id ]['y'] ), 'l', str( clientInfo[ node.id ]['dx'] ), ",0" ] )

    else:

        clientInfo[ node.id ] = {
            'parent': node.parent.id if node.parent else None,
            'isInternal': False,
            'children': [ ],
            'next': node.next,
            'back': node.back,
            'x': p['info']['currentTip']['x'],
            'dx': -( p['info']['generationSeparation'] * p['depth'] ),
            'y': p['info']['currentTip']['y'] }

        p['info']['currentTip']['y'] += p['info']['tipSeparation']
    
        if( p['originalNodeDict'][ node.id ].descendantCount ) :

            size = ( ( math.log( p['originalNodeDict'][ node.id ].descendantCount ) / math.log( p['info']['totalNodes'] ) ) * ( p['info']['tipSeparation'] / 2 ) )

            pathString = ''.join( [ "M", str( clientInfo[ node.id ]['x'] + clientInfo[ node.id ]['dx'] ), ' ', str( clientInfo[ node.id ]['y'] ), \
                           "l", str( - clientInfo[ node.id ]['dx'] ), ' ', str( -size ), 'l0 ', str( 2 * size ), 'z' ] )

            p['info']['expandableUI'].append( { 'nodeId': node.id,
                                                'pathString': pathString,
                                                'descendantCount': p['originalNodeDict'][ node.id ].descendantCount,
                                                'descendantLabels': p['originalNodeDict'][ node.id ].descendantLabels } )

            clientInfo[ node.id ]['isCollapsed'] = True
                
        else:
            p['info']['pathString'] += ''.join( [ "M", str( clientInfo[ node.id ]['x'] ), ',', str( clientInfo[ node.id ]['y'] ), 'l', str( clientInfo[ node.id ]['dx'] ), ",0" ] )

    if( node.label ):
        clientInfo[ node.id ]['label'] = node.label

 
def getBrowseData( p ):

    root = p.tree

    viewerHeight = p.info.viewerHeight
    labelWidthMetric = p.info.labelWidthMetric

    buffer = { 'x': 20, 'y': 20, '2x': 40, '2y': 40 }

    tipLabelBuffer = 5
    generationSeparation = 20
    tipSeparation = 20

    treeInfoObj = getTreeInfoObj( Storage( labelWidthMetric = labelWidthMetric ) )

    getTreeInfo( { 'node': root, 'generation': 1, 'info': treeInfoObj } )

    return getTreeClientInfo( { 'treeInfo': treeInfoObj,
                                'tree': root,
                                'nodeDict': p.originalNodeDict if 'originalNodeDict' in p else treeInfoObj['nodeDict'],
                                'config': { 'generationSeparation': generationSeparation,
                                            'buffer': buffer,
                                            'tipLabelBuffer': tipLabelBuffer,
                                            'tipSeparation': tipSeparation },
                                'labelWidthMetric': labelWidthMetric } )



def getNavigateData( p ):

    root = p['tree']
    viewerHeight = p['info']['viewerHeight']
    labelWidthMetric = p['info']['labelWidthMetric']

    buffer = { 'x': 20, 'y': 20, '2x': 40, '2y': 40 }
    tipLabelBuffer = 5
    generationSeparation = 20
    tipSeparation = 20

    treeInfo = { 'tips': 0,
                 'depth': 0,
                 'nodeDict': { },
                 'nodeWeights': [ ],
                 'depthTipCount': { },
                 'depthNodeCount': { },
                 'longestTipLabel': 0,
                 'leftmostLabel': 10000,
                 'labelWidthMetric': labelWidthMetric,
                 'genSep': generationSeparation }

    getTreeInfo( { 'node': root, 'generation': 1, 'info': treeInfo } )

    ## pprint(treeInfo)

    treeInfoForClient = treeInfo
    
    if viewerHeight < ( ( buffer['2y'] ) + ( tipSeparation * treeInfo['tips'] ) ):

        truncateInfo = getMaxGeneration( {
            'treeInfo': treeInfo,
            'viewerHeight': viewerHeight,
            'bufferY': buffer['2y'],
            'tipSeparation': tipSeparation } )
    
        truncateData = truncateTree( {
                'currentGeneration': 1,
                'currentNode': root,
                'currentTipCount': truncateInfo['currentTipCount'],
                'stopGeneration': truncateInfo['maxGeneration'] } );

        fillOutTree( { 'tipsToFill': truncateInfo['maxTips'] - truncateData['tipCount'],
                       'originalNodeDict': treeInfo['nodeDict'],
                       'currentNode': truncateData['tree'] } );

        consolidateCollapsedNodes( { 'currentNode': truncateData['tree'],
                                     'originalNodeDict': treeInfo['nodeDict'] } )

        truncatedTreeInfo = \
            { 'labelWidthMetric': labelWidthMetric,
              'genSep': generationSeparation,
              'longestTipLabel': 0,
              'leftmostLabel': 1000000,
              'tips': 0,
              'depth': 0 }

        getTruncatedTreeInfo( {
            'node': truncateData['tree'],
            'info': truncatedTreeInfo,
            'generation': 1 } )

        treeInfoForClient = truncatedTreeInfo
        root = truncateData['tree']

    return getTreeClientInfo( { 'treeInfo': treeInfoForClient,
                                'tree': root,
                                'nodeDict': p['originalNodeDict'] if 'originalNodeDict' in p else treeInfo['nodeDict'],
                                'config': { 'generationSeparation': generationSeparation,
                                            'buffer': buffer,
                                            'tipLabelBuffer': tipLabelBuffer,
                                            'tipSeparation': tipSeparation },
                                'labelWidthMetric': labelWidthMetric } )


def consolidateCollapsedNodes( p ):

    node = p['currentNode']
 
    allChildrenCollapsed = False
    
    if( len( node.children ) ): 
        
        allChildrenCollapsed = True

        for child in node.children: 
            isCollapsed = consolidateCollapsedNodes( { 'currentNode': child, 'originalNodeDict': p['originalNodeDict'] } )
            if( not isCollapsed ):
                allChildrenCollapsed = False
           
        if( allChildrenCollapsed ):
            node.children = []

    if( ( len( node.children ) == 0 ) and ( p['originalNodeDict'][ node.id ].descendantCount ) ):
        return True
    else:
        return False



def getNodeById( p ):

    if( p['id'] == p['currentNode'].id ):
        return p['currentNode']
    else:
        for child in p['currentNode'].children:
            ret = getNodeById( { 'id': p['id'], 'currentNode': child  } )
            if ret:
                return ret
    return None


def createGTreeRecord( p ):

    return p.db.gtree.insert(
        contributor = ' '.join( [ p.auth.user.first_name, p.auth.user.last_name ] ),
        title = p.params.treeTitle,
        comment = p.params.treeComment,
        date = datetime.datetime.now() ).id



def getTreeInfoStruct( p ):

    return { 'tips': 0,
             'depth': 0,
             'nodeDict': { },
             'nodeWeights': [ ],
             'depthTipCount': { },
             'depthNodeCount': { },
             'longestTipLabel': 0,
             'leftmostLabel': 10000,
             'labelWidthMetric': p['labelWidthMetric'],
              'genSep': p['generationSeparation'] }


def insertGNodes( p ):

    db = p.db

    node = p.node

    gnode = db.gnode.insert( label = node.label,
                             istip = node.isleaf,
                             ntips = p.treeInfo['nodeDict'][node.id].descendantTipCount,
                             parent = p.parentId if 'parentId' in p else None,
                             next = node.next,
                             back = node.back,
                             length = node.length,
                             tree = p.treeId,
                             snode = node.snode,
                             pruned = False,
                             stree = node.stree )

    if( node.id == p.params.affectedNodeId ):
        p.translation.affectedNodeId = gnode.id
    
    if( node.id == p.params.affectedCladeId ):
        p.translation.affectedCladeId = gnode.id

    node.id = gnode.id

    for child in node.children:
        insertGNodes( Storage( node = child, db = db, treeInfo = p.treeInfo,
                               treeId = p.treeId, parentId = node.id, translation = p.translation, params = p.params ) )


def rollbackUpdateGNodes( p ):
    
    db = p.db

    node = p.node

    if( p.currentAction == 'update' ):

        db( db.gnode.id == node.id ).update( ntips = p.treeInfo['nodeDict'][node.id].descendantTipCount,
                                             istip = node.isleaf,
                                             parent = node.parent.id if node.parent else None,
                                             next = node.next,
                                             back = node.back )

    elif( p.currentAction == 'insert' ):

        gnode = db.gnode.insert( label = node.label,
                                 istip = node.isleaf,
                                 ntips = p.treeInfo['nodeDict'][node.id].descendantTipCount,
                                 parent = p.parentId,
                                 next = node.next,
                                 back = node.back,
                                 length = node.length,
                                 tree = p.insertParams.gTreeId,
                                 snode = node.id,
                                 pruned = False,
                                 stree = p.insertParams.streeId )
        
        node.id = gnode.id
            
    for child in node.children:

        currentAction = p.currentAction;
        
        if( ( currentAction == 'update' ) and ( p.insertParams ) and
            ( p.insertParams.sourceNodeId == child.id ) and ( child.stree == None ) ):
            currentAction = 'insert'
        
        rollbackUpdateGNodes( Storage( node = child, parentId = node.id, currentAction = currentAction,
                                       db = db, treeInfo = p.treeInfo, insertParams = p.insertParams ) )



def insertAndUpdateGNodes( p ):

    db = p['db']
    node = p['node']

    parentId = None

    if( p['currentAction'] == 'update' ):

        db( db.gnode.id == node.id ).update( \
            ntips = p['treeInfo']['nodeDict'][node.id].descendantTipCount,
            next = node.next,
            back = node.back )

    elif( p['currentAction'] == 'insert' ):

        streeId = p['insertTreeId']
        snode = node.id

        if( p['aux']['treeType'] == 'forked' ):
            streeId = node.stree
            snode = node.snode
        
        gnode = db.gnode.insert( \
                    label = node.label,
                    istip = node.isleaf,
                    ntips = p['treeInfo']['nodeDict'][node.id].descendantTipCount,
                    parent = p['parentId'],
                    next = node.next,
                    back = node.back,
                    length = node.length,
                    tree = p['aux']['treeId'],
                    snode = snode,
                    pruned = False,
                    stree = streeId )

        if( ( p['aux']['treeType'] == 'source' ) and
            ( p['affectedCladeId'] == node.id ) ):
            p['affectedCladeId'] = gnode.id

        if( ( node.id == p['aux']['clipboardNodeId'] ) and
            ( p['parentId'] == p['affectedCladeId'] ) ):
            p['aux']['targetGNodeId'] = gnode.id

        p['treeInfo']['nodeDict'][gnode.id] = p['treeInfo']['nodeDict'][node.id]
        del p['treeInfo']['nodeDict'][node.id]
        node.id = gnode.id

    parentId = node.id

    for child in node.children:
        currentAction = p['currentAction']
        insertTreeId = p['insertTreeId'] if 'insertTreeId' in p else 0
        clipboardNodeId = p['aux']['clipboardNodeId'] if 'clipboardNodeId' in p['aux'] else 0
        affectedCladeId = p['affectedCladeId'] if 'affectedCladeId' in p else 0

        if( ( int( child.id ) == int( clipboardNodeId ) ) and
            ( int( node.id ) == int( p['affectedCladeId'] ) ) ):
            currentAction = 'insert'
            insertTreeId = p['aux']['clipboardSTreeId'];

        insertAndUpdateGNodes( { 'db': p['db'], 
                                 'node': child,
                                 'treeInfo': p['treeInfo'],
                                 'currentAction': currentAction,
                                 'insertTreeId': insertTreeId,
                                 'parentId': parentId,
                                 'affectedCladeId': affectedCladeId,
                                 'aux': p['aux'] } )

def rollbackTree( p ):

    db = p.db

    allTreeEdits = db( ( db.gtree_edit.gtree == p.editRecord.gtree ) &
                       ( db.gtree_edit.mtime >= p.editRecord.mtime ) ).select( orderby = ~db.gtree_edit.mtime )
     
    for treeEdit in allTreeEdits:

        if( treeEdit.originalTreeType == 'source' ):

            if( p.descendantCheck ):

                rootSourceRef = db.snode[ p.tree.snode ]
                editSourceNode = db.snode[ treeEdit.affected_clade_id ]

                if( not ( ( rootSourceRef.next <= editSourceNode.next ) &
                          ( rootSourceRef.back >= editSourceNode.back ) ) ):
                        continue

            rvTree = globals()[ ''.join( [ 'revertInitial', treeEdit.action.title() ] ) ](
                Storage( gTree = p.tree,
                         db = db,
                         permanent = p.permanent,
                         sourceNode = build.snode2tree( db, treeEdit.affected_node_id ),
                         editRow = treeEdit ) )

        else:

            if( p.descendantCheck ):

                editGNode = db.gnode[ treeEdit.affected_clade_id ]

                if( not ( ( p.tree.next <= editGNode.next ) &
                        ( p.tree.back >= editGNode.back ) ) ):
                        continue

            globals()[ ''.join( [ treeEdit.action, 'Undo' ] ) ]( Storage( db = db, tree = p.tree, edit = treeEdit, permanent = p.permanent  ) )
   
    return p.tree


def pruneUndo( p ):

    db = p.db
    
    prunedClade = build.gnode2tree( db, p.edit.affected_node_id, ( ( db.gnode.id == db.prune_detail.pruned_gnode ) &
                                                                   ( db.prune_detail.gtree_edit == p.edit.id ) ) )

    parentNode = getNodeById( { 'currentNode': p.tree, 'id': p.edit.affected_clade_id } )

    parentNode.add_child( prunedClade );

    if( p.permanent ):

        nodesToUnPrune = db( ( db.prune_detail.gtree_edit == p.edit.id ) &
                             ( db.gnode.id == db.prune_detail.pruned_gnode ) ).select()

        for node in nodesToUnPrune:
            db.gnode[ node.gnode.id ]= dict( pruned = False )

        db( db.prune_detail.gtree_edit == p.edit.id ).delete()
        
        db( db.gtree_edit.id == p.edit.id ).delete()



def graftUndo( p ):

    db = p.db

    graftedNode = getNodeById( { 'currentNode': p.tree, 'id': p.edit.target_gnode } )

    parentNode = graftedNode.parent

    parentNode.remove_child( graftedNode )

    if( p.permanent ):

        db( db.gtree_edit.id == p.edit.id ).delete()

        db( ( db.gnode.next >= graftedNode.next ) &
            ( db.gnode.back <= graftedNode.back ) &
            ( db.gnode.tree == p.edit.gtree ) ).update( pruned = True )


 
def replaceUndo( p ):
    
    db = p.db
    
    nodeInTree = getNodeById( { 'currentNode': p.tree, 'id': p.edit.target_gnode } )
   
    parentNode = nodeInTree.parent
     
    replacedNode = build.gnode2tree( db, p.edit.affected_node_id, ( ( db.gnode.id == db.prune_detail.pruned_gnode ) &
                                                                    ( db.prune_detail.gtree_edit == p.edit.id ) ) )

    parentNode.remove_child( nodeInTree )
    parentNode.add_child( replacedNode )
    

    if( p.permanent ):

        db( ( db.gnode.next >= nodeInTree.next ) &
            ( db.gnode.back <= nodeInTree.back ) &
            ( db.gnode.pruned == False ) &
            ( db.gnode.tree == p.edit.gtree ) ).update( pruned = True )

        gNodesToUnPrune = db( ( db.gnode.id == db.prune_detail.pruned_gnode ) &
                              ( db.prune_detail.gtree_edit == p.edit.id ) ).select()

        for record in gNodesToUnPrune:
            db.gnode[ record.gnode.id ].pruned = False

        db( db.prune_detail.gtree_edit == p.edit.id ).delete()
        
        db( db.gtree_edit.id == p.edit.id ).delete()

        

def revertInitialPrune( p ):

    db = p.db
    
    parentToAddTo = getNodeById( { 'currentNode': p.gTree,
                                            'id': db( ( db.gnode.tree == p.editRow.gtree ) &
                                                      ( db.gnode.snode == p.editRow.affected_clade_id ) ).select()[0].id } )

    parentToAddTo.add_child( p.sourceNode )

    if( p.permanent ):
        db( db.gtree_edit.id == p.editRow.id ).delete()

    return p.gTree


def revertInitialGraft( p ):

    db = p.db

    nodeToRemove = getNodeById( { 'currentNode': p.gTree, 'id': int( p.editRow.target_gnode ) } )
    
    parent = nodeToRemove.parent;

    parent.remove_child( nodeToRemove )
    
    if( p.permanent ):
        db( db.gtree_edit.id == p.editRow.id ).delete()

        db( ( db.gnode.next >= nodeToRemove.next ) &
            ( db.gnode.back <= nodeToRemove.back ) &
            ( db.gnode.tree == p.editRow.gtree ) ).update( pruned = True )


    return p.gTree


def revertInitialReplace( p ):

    db = p.db
    
    nodeToRemove = getNodeById( { 'currentNode': p.gTree, 'id': int( p.editRow.target_gnode ) } )

    parent = nodeToRemove.parent;

    parent.remove_child( nodeToRemove )

    parent.add_child( p.sourceNode )
    
    if( p.permanent ):

        db( ( db.gnode.next >= nodeToRemove.next ) &
            ( db.gnode.back <= nodeToRemove.back ) &
            ( db.gnode.tree == p.editRow.gtree ) ).update( pruned = True )
        
        gNodesToUnPrune = db( ( db.gnode.id == db.prune_detail.pruned_gnode ) &
                              ( db.prune_detail.gtree_edit == p.editRow.id ) ).select()

        for record in gNodesToUnPrune:
            db.gnode[ record.gnode.id ].pruned = False

        db( db.prune_detail.gtree_edit == p.editRow.id ).delete()

        db( db.gtree_edit.id == p.editRow.id ).delete()

    return p.gTree



def handleGraftParams( p ):

    return Storage( treeId = p.treeId,
                    clipboardNodeId = int( p.clipboardNodeId ) if p.clipboardNodeId != '' else 0,
                    affectedCladeId = int( p.affectedCladeId ),
                    affectedNodeId = int( p.affectedNodeId ),
                    treeTitle = p.treeName,
                    treeType = p.treeType,
                    viewMode = p.viewMode,
                    graftType = p.graftType,
                    treeComment = p.treeComment,
                    graftComment = p.graftComment )


def graftedNavigateReplace( params ):

    db = params.db; auth = params.auth;

    tree = build.gtree( db, params.treeId )

    prunedGNode = treeReplace( Storage( db = db, params = params, tree = tree ) )
    
    editId = createEditRecord( Storage( auth = auth, db = db, params = params, action = 'replace' ) )

    pruneGNodeRecords( Storage( db = db, params = params, node = prunedGNode, editId = editId ) )
    
    return postGraftForClient( Storage(
        params = params,
        editId = editId,
        tree = tree,
        treeType = 'grafted',
        action = 'replace' ) )


def sourceNavigateReplace( params ):
    
    db = params.db; auth = params.auth

    tree = build.stree( db, params.treeId )
    
    treeReplace( Storage( db = db, params = params, tree = tree ) )

    insertSTreeId = params.treeId

    params.treeId = createGTreeRecord( Storage( auth = auth, db = db, params = params ) )
    
    editId = createEditRecord( Storage( auth = auth, db = db, params = params, action = 'replace', treeType = 'source' ) )

    return postGraftForClient( Storage(
        params = params,
        editId = editId,
        tree = tree,
        treeType = 'source',
        action = 'graft',
        insertSTreeId = insertSTreeId ) )


def sourceNavigateGraft( params ):
    
    db = params.db; auth = params.auth

    tree = build.stree( db, params.treeId )
    
    treeGraft( Storage( db = db, params = params, tree = tree ) )

    insertSTreeId = params.treeId

    params.treeId = createGTreeRecord( Storage( auth = auth, db = db, params = params ) )
    
    editId = createEditRecord( Storage( db = db, auth = auth, params = params, action = 'graft', treeType = 'source' ) )
    
    return postGraftForClient( Storage(
        params = params,
        editId = editId,
        tree = tree,
        treeType = 'source',
        action = 'graft',
        insertSTreeId = insertSTreeId ) )



def graftedNavigateGraft( params ):

    db = params.db; auth = params.auth

    tree = build.gtree( db, params.treeId )
   
    treeGraft( Storage( db = db, params = params, tree = tree ) )

    editId = createEditRecord( Storage( auth = auth, db = db, params = params, action = 'graft', treeType = 'grafted' ) )
    
    return postGraftForClient( Storage(
        params = params,
        tree = tree,
        treeType = 'grafted',
        editId = editId,
        action = 'graft' ) )


def sourceNavigatePrune( params ):
    
    db = params.db; auth = params.auth

    tree = build.stree( db, params.treeId )

    treePrune( Storage( db = db, params = params, tree = tree ) )
    
    insertSTreeId = params.treeId

    params.treeId = createGTreeRecord( Storage( auth = auth, db = db, params = params ) )

    editId = createEditRecord( Storage( auth = auth, db = db, params = params, action = 'prune', treeType = 'source' ) )

    return postGraftForClient( Storage(
        params = params,
        editId = editId,
        tree = tree,
        treeType = 'source',
        action = 'prune',
        insertSTreeId = insertSTreeId ) )


def graftedNavigatePrune( params ):
    
    db = params.db; auth = params.auth

    tree = build.gtree( db, params.treeId )

    prunedGNode = treePrune( Storage( db = db, params = params, tree = tree ) )

    editId = createEditRecord( Storage( auth = auth, db = db, params = params, action = 'prune', treeType = 'grafted' ) )

    pruneGNodeRecords( Storage( db = db, params = params, node = prunedGNode, editId = editId ) )

    return postGraftForClient( Storage(
        params = params,
        editId = editId,
        tree = tree,
        treeType = 'grafted',
        action = 'prune' ) )


def postGraftForClient( p ) :

    db = p.params.db

    treeInfo = getTreeInfoStruct( { 'labelWidthMetric': p.params.session.labelWidthMetric,
                                    'generationSeparation': 20 } )

    clipboardNodeSTreeId = db( db.snode.id == p.params.clipboardNodeId ).select()[0].tree if p.action != 'prune' else 0

    index( p.tree )

    getTreeInfo( { 'node': p.tree, 'generation': 1, 'info': treeInfo } )

    aux = {
        'treeId': p.params.treeId,
        'treeType': p.treeType,
        'targetGNodeId': None,
        'clipboardNodeId': p.params.clipboardNodeId,
        'clipboardSTreeId': clipboardNodeSTreeId }

    insertAndUpdateGNodes( { 'node': p.tree,
                                      'db': db,
                                      'treeInfo': treeInfo,
                                      'currentAction': 'update' if p.treeType == 'grafted' else 'insert',
                                      'insertTreeId': p.insertSTreeId,
                                      'parentId': None,
                                      'affectedCladeId': p.params.affectedCladeId,
                                      'aux': aux } )

    
    db( db.gtree_edit.id == p.editId ).update( target_gnode = aux['targetGNodeId'] )

    
    return {
        'treeId': p.params.treeId,
        'renderInfo': getNavigateData( {
                         'tree': p.tree,
                         'info': { 'viewerHeight': p.params.session.viewportHeight,
                                   'labelWidthMetric': p.params.session.labelWidthMetric } } ) }


def treeReplace( p ):

    replacingNode = build.snode2tree( p.db, p.params.clipboardNodeId )
    parentNode = getNodeById( { 'currentNode': p.tree, 'id': p.params.affectedCladeId } )
    childToRemove = getNodeById( { 'currentNode': p.tree, 'id': p.params.affectedNodeId } )

    parentNode.remove_child( childToRemove )
    parentNode.add_child( replacingNode )

    return childToRemove


def treeGraft( p ):
    newSibling = build.snode2tree( p.db, p.params.clipboardNodeId )
    parentNode = getNodeById( { 'currentNode': p.tree, 'id': p.params.affectedCladeId } )
        
    parentNode.add_child( newSibling )


def treePrune( p ):
    
    parentClade = getNodeById( { 'currentNode': p.tree, 'id': p.params.affectedCladeId } )
    cladeToPrune = getNodeById( { 'currentNode': p.tree, 'id': p.params.affectedNodeId } )

    parentClade.remove_child( cladeToPrune ) 

    return cladeToPrune


def pruneGNodeRecords( p ):

    db = p.db

    db( ( db.gnode.tree == p.params.treeId ) & 
        ( db.gnode.next >= p.node.next ) &
        ( db.gnode.back <= p.node.back ) ).update( pruned = True )

    nodesToPrune = db( ( db.gnode.tree == p.params.treeId ) & 
        ( db.gnode.next >= p.node.next ) &
        ( db.gnode.back <= p.node.back ) ).select( db.gnode.id )

    for node in nodesToPrune:
        db.prune_detail.insert( pruned_gnode = node.id, gtree_edit = p.editId )


def createEditRecord( p ):

    insertDict = dict(
        gtree = p.params.treeId,
        action = p.action,
        affected_clade_id = p.params.affectedCladeId,
        affected_node_id = p.params.affectedNodeId,
        comment = p.params.graftComment,
        originalTreeType = p.treeType,
        user = p.auth.user.id )

    if p.action != 'prune':
        insertDict['clipboard_node'] = p.params.clipboardNodeId

    return p.db.gtree_edit.insert( **insertDict )


def getTreeInfoObj( p ):

    return { 'tips': 0,
             'depth': 0,
             'nodeDict': { },
             'nodeWeights': [ ],
             'depthTipCount': { },
             'depthNodeCount': { },
             'longestTipLabel': 0,
             'leftmostLabel': 10000,
             'labelWidthMetric': p.session.labelWidthMetric if 'session' in p else p.labelWidthMetric,
             'genSep': 20 }



def getSVGCladePathString( clade ):
    """
    The function takes a clade and returns its path string
    """

    strList = []

    getSVGCladePathStringRecurse( clade, strList )

    return ''.join( strList )


def getSVGCladePathStringRecurse( node, strList ):
    """
    The function iterates through a clade recursively appending a path string for each node to a list.
    Used by getSVGCladePathString
    """

    strList.append( getSVGNodePathString( node ) )

    for child in node.children:
        getSVGCladePathStringRecurse( child, strList )


def getSVGNodePathString( node ):
    """
    The function accepts a modules.ivy.Node object and returns an svg path string using x, dx and y associated with the given node.
    Should this use a 'dx' attribute as well, or a branch length session variable or parameter?
    """

    returnString = [ ]

    strX = str( node.x )
    strDX = str( node.dx )
    strY = str( node.y )

    if node.children: 
        returnString.append( ''.join( [ 'M', strX, ' ', str( node.children[0].y ), 'L', strX, ' ', str( node.children[ len( node.children) - 1 ].y ) ] ) )
    
    returnString.append( ''.join( [ 'M', strX, ' ', strY, 'h', strDX ] ) )

    return ''.join( returnString )





def getNodeCoordinates( mode, tree, session ):
    """
    A function that takes a tree and a render mode, and returns a dictionary mapping node ids to relative x,y coordinates.
    
    It uses session values to get branch length and vertical tip separation.  
    """

    gatherTreeInfo( tree, session )
  
    if( ( mode == 'navigate' ) and viewerUtil.needsCollapsing( tree.meta.tips, session ) ):

        maxTips = math.floor( ( session.pageHeight - ( session.verticalPadding * 2 ) ) / session.verticalTipBuffer )
    
        collapsedNodes = determineCollapsedNodes( tree.meta, [ ], Storage(), maxTips )
   
        collapseTreeNodes( tree, collapsedNodes )

    nodeCoordinates = dict()

    assignNodeCoordinates( tree,
                           Storage( x = ( session.branchLength * tree.meta.depth ), y = session.verticalPadding ),
                           tree.meta.depth,
                           session.branchLength,
                           session.verticalTipBuffer,
                           nodeCoordinates )

    return nodeCoordinates

   
def assignNodeCoordinates( node, currentTip, currentDepth, branchLength, verticalTipBuffer, nodeCoords ):
    """
    This function takes a tree, a storage object containing x and y attributes associated with the coordinates of the next
    place for a tip node, the branch length, and an object to store the node coordinates.  It iterates through the tree
    beginning with the tip nodes and assigns coordinates based on the input parameters.
    """

    for child in node.children:
        assignNodeCoordinates( child, currentTip, currentDepth - 1, branchLength, verticalTipBuffer, nodeCoords )

    if node.children:

        node.x = node.children[0].x + node.children[0].dx
        node.dx = -branchLength
        node.y = ( node.children[ -1 ].y + node.children[0].y ) / 2

    else:

        node.x = currentTip.x
        node.dx = -( branchLength * currentDepth )
        node.y = currentTip.y

        currentTip.y += verticalTipBuffer
        
    nodeCoords[ node.id ] = Storage( x = node.x, dx = node.dx, y = node.y )


def collapseTreeNodes( clade, collapsedNodeIds, db, session ):
    """
    """
    
    info = dict()

    totalNodes = ( db.snode[ clade.id ].back - db.snode[ clade.id ].next - 1 ) / 2

    for row in db( db.snode.id.belongs( collapsedNodeIds ) ).select():

        info[ int( row.id ) ] = dict(
            descendantCount = ( row.back - row.next - 1 ) / 2,
            descendantLabels = [ labelRow.label for labelRow in db( ( db.stree.id == row.tree ) &
                                                                    ( db.snode.next > row.next ) &
                                                                    ( db.snode.back < row.back ) ).select( db.snode.label ) if labelRow.label ] )

        info[ int( row.id ) ]['size'] = ( math.log( info[ row.id ]['descendantCount'] ) / math.log( totalNodes ) ) * ( session.TreeViewer.config.verticalTipBuffer / 2 )
            
    clade.collapsedNodeInfo = info

    collapseTreeNodesRecurse( clade, collapsedNodeIds )


 
def collapseTreeNodesRecurse( node, collapsedNodes ):
    """
    This function takes a node and a storage object, or list, of collapsed node ids - referring to nodes that should be collapsed.
    It recurses through the tree and "collapses" nodes by removing their children.
    """

    if( node.id in collapsedNodes ):
        node.children = []

    for child in node.children:
        collapseTreeNodesRecurse( child, collapsedNodes )

   
def determineCollapsedNodes( treeInfoObj, collapse, keepVisible, maxTips ):
    """
    A function that returns a storage object of nodes to collapse using a list of nodeWeights associated with an id
    """
    
    treeInfoObj.nodeWeights.sort(); treeInfoObj.nodeWeights.reverse()

    for weight, node in treeInfoObj.nodeWeights:
        
        if( ( node.id not in keepVisible ) and ( node.id not in collapse ) and
            ( not isAncestorCollapsed( node.id, treeInfoObj, collapse ) ) ):

            collapse.append( node.id )
            treeInfoObj.tips -= node.descendantTipCount + collapsedDescendantsTipCount( node.id, treeInfoObj, collapse )

            if( treeInfoObj.tips <= maxTips ):
                break;

    f = open( '/tmp/debug', 'a')
    f.write( str( collapse ) )                

    return collapse
            

    
def collapsedDescendantsTipCount( nodeId, treeInfoObj, collapse ):
    """
    This is a helper function used by the determineCollapsedNodes function.
    It returns the number of tips already collapsed by nodes that are descendants of the
    passed in parameter nodeId.
    """

    collapsedDescendantsTipCount = 0

    nodeInQuestion = treeInfoObj.nodeDict[ nodeId ]

    for collapsedNodeId in collapse:
        
        collapsedNode = treeInfoObj.nodeDict[ collapsedNodeId ]

        if( ( nodeInQuestion.next < collapsedNode.next ) and ( nodeInQuestion.back > collapsedNode.back ) ):
            collapsedDescendantsTipCount += collapsedNode.descendantTipCount
            collapse.remove( collapsedNodeId )

    return collapsedDescendantsTipCount


def isAncestorCollapsed( nodeId, treeInfoObj, collapse ):
    """
    This is a helper function used by the determineCollapsedNodes function.
    It returns a boolean value based on whether the passed in nodeId already has an ancestor
    that is collapsed.  This is used to ensure we are only collapsing nodes ( and removing tips )
    that are not already collapsed implicitly because their ancestor is collapsed.
    """

    nodeInQuestion = treeInfoObj.nodeDict[ nodeId ]

    for collapsedNodeId in collapse:
        
        collapsedNode = treeInfoObj.nodeDict[ collapsedNodeId ]

        if( ( nodeInQuestion.next > collapsedNode.next ) and ( nodeInQuestion.back < collapsedNode.back ) ):
            return True

    return False


def assignCollapseDetail( node, infoDict, session, currentTip ):
    
    difference = ( infoDict['size'] * 2 )  - session.TreeViewer.config.verticalTipBuffer

    if( difference > 0 ):
        
        node.y += ( difference / 2 )
    
        currentTip.y += difference

    infoDict['pathString'] = ''.join( [ "M", str( node.x + node.dx ), ' ', str( node.y ),
                                        "l", str( - node.dx ), ' ', str( -infoDict['size'] ),
                                        'l0 ', str( 2 * infoDict['size'] ), 'z' ] )
        

def assignNodeMappings( clade, session, collapsedNodeInfo ):
    """
    A function that manages a tree recusrion that sets node coordiates and labels
    """

    nodeMap = dict() 

    firstTip = Storage( x = ( session.TreeViewer.config.branchLength * clade.meta.depth ) + session.TreeViewer.config.horizontalPadding,
                        y = session.TreeViewer.config.verticalPadding )

    assignNodeMappingsRecurse( clade, nodeMap, session, collapsedNodeInfo, firstTip, clade.meta.depth )

    return nodeMap


def assignNodeMappingsRecurse( node, nodeMap, session, collapsedNodeInfo, currentTip, currentDepth ):
    """
    A function that recurses through a tree adding node coordinates and labels to a dictionary where the keys are node ids.
    """

    nodeMap[ node.id ] = dict( children = [ ] )
   
    for child in node.children:
        nodeMap[ node.id ]['children'].append( child.id )
        assignNodeMappingsRecurse( child, nodeMap, session, collapsedNodeInfo, currentTip, currentDepth - 1 )

    if node.children:

        node.x = nodeMap[ node.children[0].id ]['x'] + nodeMap[ node.children[0].id ]['dx']
        node.dx = -( session.TreeViewer.config.branchLength )
        node.y = ( ( nodeMap[ node.children[ -1 ].id ]['y'] + nodeMap[ node.children[ 0 ].id ]['y'] ) / 2 )

    else:

        node.x = currentTip.x
        node.dx = -( session.TreeViewer.config.branchLength * currentDepth )
        node.y = currentTip.y

        if( node.id in collapsedNodeInfo ):

            assignCollapseDetail( node, collapsedNodeInfo[ node.id ], session, currentTip )

            nodeMap[ node.id ]['collapsed'] = collapsedNodeInfo[ node.id ]

        currentTip.y += session.TreeViewer.config.verticalTipBuffer
   
    nodeMap[ node.id ]['x'] = node.x
    nodeMap[ node.id ]['y'] = node.y
    nodeMap[ node.id ]['dx'] = node.dx
    nodeMap[ node.id ]['label'] = node.label




def gatherTreeInfo( node, session ):
    """
    A function that recursively parses a node obj and adds the following information to its 'meta' attribute: 

        a node dict
        number of tips
        node weights
        dict of tip counts at each "generation"
        dict of total node counts at each "generation"
        the longest tip label
        the 'leftmost' label
    """

    treeInfoObj = getTreeInfoObj2()

    getTreeInfo2( treeInfoObj, node, Storage( generation = 1 ), session )

    node.meta = treeInfoObj


    
def getTreeInfoObj2():
    """
    A function returning a Storage object ( web2py ) used by the getTreeInfo2 function
    """

    return Storage( tips = 0, depth = 0, nodeDict = Storage(), nodeWeights = [], depthTipCount = Storage(),
                    depthNodeCount = Storage(), longestTipLabel = 0, leftmostLabel = 10000 )


def getClade( rootId, treeType, db ):
    """
    This function takes a rootId and a treeType, and returns the resulting tree
    """

    return getattr( build, 'gnode2tree' if treeType == 'grafted' else 'snode2tree' )( db, rootId )


def getTreeInfo2( infoObj, node, recurseStruct, session ):
    """
    A recursive function that iterates the given node and its children to determine values in the passed in variable infoObj
    """

    infoObj.nodeDict[ node.id ] = node

    curGeneration = recurseStruct.generation

    if( infoObj.depth < curGeneration ):
        infoObj.depth = curGeneration

    if curGeneration not in infoObj:
        infoObj.depthTipCount[ curGeneration ] = 0

    if curGeneration in infoObj.depthNodeCount:
        infoObj.depthNodeCount[ curGeneration ] += 1
    else:
        infoObj.depthNodeCount[ curGeneration ] = 1
       
    currentIterationInfo = Storage( descendantCount = 0, level = 0, descendantTipCount = 0, descendantLabels = [], hasDescendantLabel = False )

    if node.children:

        for child in node.children:

            recursiveIterationInfo = \
                getTreeInfo2( infoObj, child, Storage( generation = curGeneration + 1, descendants = 0 ), session )

            currentIterationInfo.descendantLabels.extend( recursiveIterationInfo.descendantLabels )
            currentIterationInfo.descendantCount += recursiveIterationInfo.descendantCount
            currentIterationInfo.descendantTipCount += recursiveIterationInfo.descendantTipCount

            if( recursiveIterationInfo.level >= currentIterationInfo.level ):
                currentIterationInfo.level = recursiveIterationInfo.level + 1

        for attr in [ 'descendantLabels', 'descendantCount', 'descendantTipCount', 'hasDescendantLabel' ]:
            setattr( node, attr, currentIterationInfo[ attr ] )

        nodeWeight = ( currentIterationInfo.descendantTipCount / float( currentIterationInfo.level ) )

        if( recursiveIterationInfo.hasDescendantLabel ):
            currentIteration.hasDescendentLabel = True
            nodeWeight *= .25

        infoObj.nodeWeights.append( ( nodeWeight, node ) )

        if( node.label ):
            canvasXLabel = ( curGeneration * session.TreeViewer.config.branchLength ) - ( len( node.label ) * session.textWidthMetric )

            infoObj.leftmostLabel = canvasXLabel if canvasXLabel < infoObj.leftmostLabel else infoObj.leftmostLabel

            currentIteration.hasDescendentLabel = True

    else:

        infoObj.tips += 1
        infoObj.depthTipCount[ curGeneration ] += 1
        
        currentIterationInfo.descendantTipCount += 1 
        currentIterationInfo.level = 1 
    
        infoObj.longestTipLabel = len( node.label ) if( node.label and ( len( node.label ) > infoObj.longestTipLabel ) ) else infoObj.longestTipLabel
            
    currentIterationInfo.descendantCount += 1

    if( node.label ):
        currentIterationInfo.descendantLabels.append( Storage( id = node.id, label = node.label ) )

    return Storage( descendantCount = currentIterationInfo.descendantCount,
                    descendantTipCount = currentIterationInfo.descendantTipCount,
                    descendantLabels = currentIterationInfo.descendantLabels,
                    hasDescendantLabel = currentIterationInfo.hasDescendantLabel,
                    level = currentIterationInfo.level )


def getCollapsedNodeInfo( clade, collapsedNodeIds, db, session ):

    info = dict()

    totalNodes = ( db.snode[ clade.id ].back - db.snode[ clade.id ].next - 1 ) / 2

    for row in db( db.snode.id.belongs( collapsedNodeIds ) ).select():

        info[ int( row.id ) ] = dict( descendantCount = ( row.back - row.next - 1 ) / 2,
                               descendantLabels = [ labelRow.label for labelRow in db( ( db.stree.id == row.tree ) & ( db.snode.next > row.next ) & ( db.snode.back < row.back ) ).select( db.snode.label ) if labelRow.label ] )

        info[ int( row.id ) ]['size'] = ( math.log( info[ row.id ]['descendantCount'] ) / math.log( totalNodes ) ) * ( session.TreeViewer.config.verticalTipBuffer / 2 )
            
    clade.collapsedNodeInfo = info


