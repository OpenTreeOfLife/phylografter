import plugin_treeViewer as util
from ivy.tree import *
import datetime, sys, math
import build as build


def revertEdit( db, session, tree, editInfo ):

    getattr( sys.modules[__name__], ''.join( [ 'revert', editInfo.action[0].capitalize(), editInfo.action[1:] ] ) )( db, session, tree, editInfo )

   
def revertPrune( db, session, clade, editInfo ):

    if( editInfo.originalTreeType == 'source' ):
        
        prunedClade = build.snode2tree( db, editInfo.affected_node_id )
        
    else:
        
        prunedClade = build.gnode2tree( db, editInfo.affected_node_id, ( ( db.gnode.id == db.prune_detail.pruned_gnode ) &
                                                                         ( db.gnode.pruned == True ) &
                                                                         ( db.prune_detail.gtree_edit == editInfo.id ) ) )

    parentNode = util.getNodeById( clade, editInfo.affected_clade_id )

    if( parentNode is None ):
        return

    parentNode.add_child( prunedClade );


def revertReplace( db, session, tree, editInfo ):

    if( editInfo.originalTreeType == 'source' ):

        replacedClade = build.snode2tree( db, editInfo.affected_node_id )
        
    else:
    
        replacedClade = build.gnode2tree( db, editInfo.affected_node_id, ( ( db.gnode.id == db.prune_detail.pruned_gnode ) &
                                                                            ( db.prune_detail.gtree_edit == editInfo.id ) ) )
    
    replacingClade = util.getNodeById( tree, editInfo.target_gnode )
    #replacingClade = build.gnode2tree( db, editInfo.target_gnode )

    if( replacingClade is None ):
        return

    parentNode = replacingClade.parent

    parentNode.remove_child( replacingClade )
    parentNode.add_child( replacedClade )


def revertGraft( db, session, tree, editInfo ):

    graftedClade = util.getNodeById( tree, editInfo.target_gnode )
    #graftedClade = build.gnode2tree( db, editInfo.target_gnode )

    if( graftedClade is None ):
        return

    parentNode = graftedClade.parent
    parentNode.remove_child( graftedClade )


def graftClade( tree, siblingCladeId, newClade ):

    sibling = util.getNodeById( tree, siblingCladeId )
    parent = sibling.parent
    parent.add_child( newClade )
    

def postGraftDBUpdate( db, session, auth):

    import sys, datetime
    sys.stdout.write( str( 'update db : ' ) )
    sys.stdout.write( str( datetime.datetime.now() ) )
    sys.stdout.write( "\n" )
    
    nodeTable = None

    if( session.TreeViewer.type == 'source' ):

       nodeTable = db.snode 
        
       session.TreeViewer.treeId = createGTreeRecord( db, auth, session.treeEdit.treeName, session.treeEdit.treeDescription )
    
    else:

        nodeTable = db.gnode


    graftedCladeSiblingRecord = db( nodeTable.id == session.treeEdit.graftedCladeSiblingId ).select().first()

    index( session.treeEdit.currentTree )

    if( session.TreeViewer.type == 'source' ):
        
        reference = \
            dict( newCladeId = session.treeEdit.graftedCladeNodeId,
                  targetGNode = None,
                  oldAffectedCladeId = graftedCladeSiblingRecord.parent,
                  newAffectedCladeId = None )
        
        insertSnodesToGtree( db, session.TreeViewer.treeId, session.treeEdit.currentTree, None, reference )
        
        createEditRecord( db, auth, session.TreeViewer.treeId, 'graft', reference['newAffectedCladeId'], graftedCladeSiblingRecord.id, session.treeEdit.graftedCladeNodeId, session.treeEdit.comment, session.TreeViewer.type, auth.user.id, reference['targetGNode'] )
        
        updateSessionForNewGtree( session )

    else:

        updateGtreeDB( db, session.treeEdit.currentTree )
        
        reference = dict( newCladeId = session.treeEdit.graftedCladeNodeId, targetGNode = None )
        
        insertGNodesToGtree( db, session.TreeViewer.treeId, util.getNodeById( session.treeEdit.currentTree, session.treeEdit.graftedCladeNodeId ), graftedCladeSiblingRecord.parent, session.treeEdit.graftedCladeType, reference )
        
        createEditRecord( db, auth, session.TreeViewer.treeId, 'graft', graftedCladeSiblingRecord.parent, graftedCladeSiblingRecord.id, session.treeEdit.graftedCladeNodeId, session.treeEdit.comment, session.TreeViewer.type, auth.user.id, reference['targetGNode'] )

    sys.stdout.write( str( 'done update db : ' ) )
    sys.stdout.write( str( datetime.datetime.now() ) )
    sys.stdout.write( "\n" )

    sys.stdout.write( str( 'preprocess new tree : ' ) )
    sys.stdout.write( str( datetime.datetime.now() ) )
    sys.stdout.write( "\n" )

    #util.gatherTreeInfo( session.treeEdit.currentTree, session, db, True )
    
    sys.stdout.write( str( 'done preprocess new tree : ' ) )
    sys.stdout.write( str( datetime.datetime.now() ) )
    sys.stdout.write( "\n" )


def replaceClade( tree, cladeToBeReplacedId, newClade ):

    cladeToReplace = util.getNodeById( tree, cladeToBeReplacedId )
    parentClade = cladeToReplace.parent

    parentClade.remove_child( cladeToReplace )
    parentClade.add_child( newClade )


def postReplaceDBUpdate( db, session, auth, tree, treeType, replacedCladeId, newCladeId, requestVars ):    
    
    if treeType == 'source':

        replacedNode = db( db.snode.id == replacedCladeId ).select()[0]
        
        gtreeId = createGTreeRecord( db, auth, requestVars.treeName, requestVars.treeDescription )
        
        index( tree )

        util.gatherTreeInfo( tree, session )
        
        reference = dict( newCladeId = newCladeId, targetGNode = None, oldAffectedCladeId = replacedNode.parent, newAffectedCladeId = None )
        
        insertSnodesToGtree( db, gtreeId, tree, None, reference )
        
        createEditRecord( db, auth, gtreeId, 'replace', reference['newAffectedCladeId'], replacedNode.id, newCladeId, requestVars.comment, treeType, auth.user.id, reference['targetGNode'] )

    else:
        
        replacedNode = db( db.gnode.id == replacedCladeId ).select()[0]
        
        index( tree )
        
        util.gatherTreeInfo( tree, session )
        
        updateGtreeDB( db, tree )
        
        reference = dict( newCladeId = newCladeId, targetGNode = None )
        
        insertGNodesToGtree( db, requestVars.treeId, util.getNodeById( tree, newCladeId ), replacedNode.parent, requestVars.clipboardNodeType, reference )

        editId = createEditRecord( db, auth, requestVars.treeId, 'replace', replacedNode.parent, replacedNode.id, requestVars.clipboardNodeId, requestVars.comment, treeType, auth.user.id, reference['targetGNode'] )
    
        pruneGNodeRecords( db, requestVars.treeId, replacedNode, editId )
        


def updateTreeStateForPrunedSourceTree( session, columnRootNodeIds, collapsedNodeIds, prunedNodeRow ):

    session.TreeViewer.treeType = 'grafted'
    session.TreeViewer.strNodeTable = 'gnode'

    oldTreeState = session.TreeViewer.treeState[ 'source' ][ session.TreeViewer.recentlyEditedSourceTreeId ]
    newTreeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ] = \
                   Storage( columns = [ ], formerlyCollapsedNodeStorage = Storage() )
        
    for column in oldTreeState.columns:

        rootNodeId = columnRootNodeIds[ column.rootNodeId ]

        newCollapsedNodeStorage = Storage()

        for ( collapsedNodeId, collapsedNodeData ) in column.collapsedNodeStorage.items():
            
            newCollapsedNodeStorage[ collapsedNodeIds[ collapsedNodeId ].nodeId ] = collapsedNodeData
            newCollapsedNodeStorage[ collapsedNodeIds[ collapsedNodeId ].nodeId ]['next'] = collapsedNodeIds[ collapsedNodeId ]['next']
            newCollapsedNodeStorage[ collapsedNodeIds[ collapsedNodeId ].nodeId ]['back'] = collapsedNodeIds[ collapsedNodeId ]['back']

        newTreeState.columns.append( Storage( rootNodeId = rootNodeId, collapsedNodeStorage = newCollapsedNodeStorage  ) )
 
    newTreeState.totalNodes = oldTreeState.totalNodes - math.floor( ( prunedNodeRow.back - prunedNodeRow.next - 1 ) / 2 )
    newTreeState.allNodesHaveLength = oldTreeState.allNodesHaveLength

    del session.TreeViewer.recentlyEditedSourceTreeId


def pruneClade( tree, nodeId ):
    
    cladeToPrune = util.getNodeById( tree, nodeId )
    parentClade = cladeToPrune.parent

    parentClade.remove_child( cladeToPrune )


def postPruneDBUpdate( db, session, request, auth, tree, prunedNodeRow ):

    treeType = session.TreeViewer.treeType

    if treeType == 'source':

        ( columnRootNodeIds, collapsedNodeIds ) = gatherTreeStateIds( session )
        session.TreeViewer.recentlyEditedSourceTreeId = session.TreeViewer.treeId

        gtreeId = createGTreeRecord( db, auth, request.vars.treeName, request.vars.treeDescription )

        session.TreeViewer.treeId = gtreeId

        index( tree )

        reference = dict( \
            oldAffectedCladeId = prunedNodeRow.parent,
            newAffectedCladeId = None,
            columnRootNodeIds = columnRootNodeIds,
            collapsedNodeIds = collapsedNodeIds )

        insertSnodesToGtree( db, session.TreeViewer.treeId, tree, None, reference )
        
        createEditRecord( db, auth, gtreeId, 'prune', reference['newAffectedCladeId'], prunedNodeRow.id, None, request.vars.comment, treeType, auth.user.id )

        updateTreeStateForPrunedSourceTree( session, columnRootNodeIds, collapsedNodeIds, prunedNodeRow )

    else:
        
        index( tree )

        updateGtreeDB( db, tree )
        
        editId = createEditRecord( db, auth, session.TreeViewer.treeId, 'prune', prunedNodeRow.parent, prunedNodeRow.id, None, request.vars.comment, treeType, auth.user.id )
        
        pruneGNodeRecords( db, session.TreeViewer.treeId, prunedNodeRow.id, editId )
        

def gatherTreeStateIds( session ):

    columnRootNodeIds = Storage()
    collapsedNodeIds = Storage()

    for column in session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].columns:

        columnRootNodeIds[ column.rootNodeId ] = None

        for ( collapsedNodeId, collapsedNodeData ) in column.collapsedNodeStorage.items():
            
            collapsedNodeIds[ collapsedNodeId ] = None

    return ( columnRootNodeIds, collapsedNodeIds )


def updateGtreeDB( db, currentNode ):

    db( db.gnode.id == currentNode.id ).update( \
        next = currentNode.next,
        back = currentNode.back,
        ntips = currentNode.descendantTipCount )


    for child in currentNode.children:
        updateGtreeDB( db, child )


def insertGNodesToGtree( db, gtreeId, node, parentId, nodeType, reference ):

    snode = db( db.gnode.id == node.id ).select()[0].snode if nodeType == 'grafted' else node.id

    gnode = db.gnode.insert( \
        label = node.label,
        isleaf = node.isleaf,
        ntips = node.descendantTipCount,
        parent = parentId,
        next = node.next,
        back = node.back,
        length = node.length,
        tree = gtreeId,
        snode = snode,
        pruned = False )

    if( node.id == reference['newCladeId'] ):
        reference['targetGNode'] = gnode.id

    for child in node.children:
        insertGNodesToGtree( db, gtreeId, child, gnode.id, nodeType, reference )



def insertSnodesToGtree( db, gtreeId, node, parentId, reference=None ):
    
    gnode = db.gnode.insert( \
        label = node.label,
        isleaf = node.isleaf,
        ntips = node.descendantTipCount,
        parent = parentId,
        next = node.next,
        back = node.back,
        length = node.length,
        tree = gtreeId,
        snode = node.id,
        pruned = False )

    if( reference is not None ):
        
        if( ( 'newCladeId' in reference ) and ( node.id == reference['newCladeId'] ) ):
            
            reference['targetGNode'] = gnode.id
        
        if( ( 'oldAffectedCladeId' in reference ) and ( node.id == reference['oldAffectedCladeId'] ) ):

            reference['newAffectedCladeId'] = gnode.id
        
        if( ( 'columnRootNodeIds' in reference ) and ( node.id in reference[ 'columnRootNodeIds' ] ) ):
            reference[ 'columnRootNodeIds' ][ node.id ] = gnode.id
        
        if( ( 'collapsedNodeIds' in reference ) and ( node.id in reference[ 'collapsedNodeIds' ] ) ):
            reference[ 'collapsedNodeIds' ][ node.id ] = Storage( nodeId = gnode.id, next = node.next, back = node.back )
    
    node.id = gnode.id

    for child in node.children:
        insertSnodesToGtree( db, gtreeId, child, gnode.id, reference )


def createGTreeRecord( db, auth, name, desc ):

    return db.gtree.insert(
        contributor = ' '.join( [ auth.user.first_name, auth.user.last_name ] ),
        title = name,
        comment = desc,
        date = datetime.datetime.now() ).id


def createEditRecord( db, auth, treeId, action, affectedCladeId, affectedNodeId, clipboardId, comment, originalTreeType, userId, targetGnode = None ):

    insertDict = dict(
        gtree = treeId,
        action = action,
        affected_clade_id = affectedCladeId,
        affected_node_id = affectedNodeId,
        comment = comment,
        originalTreeType = originalTreeType,
        user = userId )

    if action != 'prune':
        insertDict['clipboard_node'] = clipboardId
        insertDict['target_gnode'] = targetGnode

    return db.gtree_edit.insert( **insertDict ).id


def pruneGNodeRecords( db, treeId, node, editId ):

    db( ( db.gnode.tree == treeId ) & 
        ( db.gnode.next >= node.next ) &
        ( db.gnode.back <= node.back ) ).update( pruned = True )

    nodesToPrune = db(
        ( db.gnode.tree == treeId ) & 
        ( db.gnode.next >= node.next ) &
        ( db.gnode.back <= node.back ) ).select( db.gnode.id )

    for node in nodesToPrune:
        db.prune_detail.insert( pruned_gnode = node.id, gtree_edit = editId )
