from gluon.storage import Storage
ivy = local_import("ivy", reload=True)
build = local_import("build", reload=True)
treeUtil = local_import("treeUtil", reload=True)

def default():
    return dict( eventInfo = response.json(request.vars.eventInfo) )

def navigateExpandNode():

    rvTree = treeUtil.rollbackTree( Storage( editRecord = db.gtree_edit[ request.vars.editId ],
                                             tree = build.gnode2tree( db, int( request.vars.nodeId ), ( db.gnode.pruned == False ) ),
                                             db = db, descendantCheck = True ) )
            
    return response.json( treeUtil.getNavigateData( { 'tree': rvTree, 'info': { 'viewerHeight': session.viewportHeight,
                                                                                'labelWidthMetric': session.labelWidthMetric } } ) )



def undoRollback():
    return response.json( treeUtil.getNavigateData( { 'tree': build.gtree( db, int( request.args[0] ) ),
                                                      'info': { 'viewerHeight': session.viewportHeight,
                                                                'labelWidthMetric': session.labelWidthMetric } } ) )

def rollbackGraft():

    editRecord = db.gtree_edit[ request.args[0] ]

    rvTree = treeUtil.rollbackTree( Storage( editRecord = editRecord, tree = build.gtree( db, editRecord.gtree ), db = db ) )
    
    treeInfoObj = treeUtil.getTreeInfoObj( Storage( session = session ) )

    treeUtil.getTreeInfo( { 'node': rvTree, 'generation': 1, 'info': treeInfoObj } )

    collapsedNodeIds = request.vars.collapsedNodeIds.split(':')

    for collapsedNodeId in collapsedNodeIds:

        collapsedNode = treeUtil.getNodeById( { 'currentNode': rvTree, 'id': int(collapsedNodeId) } )
        collapsedNode.children = []

    return response.json( treeUtil.getNavigateData( { 'tree': rvTree,
                                                      'originalNodeDict': treeInfoObj['nodeDict'],
                                                      'info': { 'viewerHeight': session.viewportHeight,
                                                                'labelWidthMetric': session.labelWidthMetric } } ) )


def saveChangesAndGraft():

    params = treeUtil.handleGraftParams( request.vars )

    translation = Storage()

    rvInfo = globals()[ ''.join( [ request.vars.saveType, 'SaveChanges' ] ) ](
        Storage( db = db, editRecord = db.gtree_edit[ request.vars.editId ], auth = auth, params = params, translation = translation ) )
    
    params.treeId = rvInfo.treeId; params.db = db; params.auth = auth; params.session = session;

    if( request.vars.saveType == 'fork' ):
        params.affectedNodeId = translation.affectedNodeId
        params.affectedCladeId = translation.affectedCladeId

    return response.json( getattr( treeUtil, ''.join( [ 'grafted', 'Navigate', params.graftType.title() ] ) )( params ) )


def editSaveChanges( p ):

    tree = treeUtil.rollbackTree( Storage( editRecord = p.editRecord, tree = build.gtree( p.db, p.editRecord.gtree ), db = p.db, permanent = True ) )

    ivy.tree.index( tree )

    treeInfo = treeUtil.getTreeInfoStruct( { 'labelWidthMetric': session.labelWidthMetric,
                                             'generationSeparation': 20 } )

    treeUtil.getTreeInfo( { 'node': tree, 'generation': 1, 'info': treeInfo } )

    insertParams = None

    if( ( p.editRecord.originalTreeType == 'source' ) and ( not p.editRecord.action == 'graft' ) ):
        insertParams = Storage( sourceNodeId = p.editRecord.affected_node_id,
                                sourceTreeId = db.snode[ p.editRecord.affected_node_id ].tree,
                                gTreeId = p.editRecord.gtree )
    
    treeUtil.rollbackUpdateGNodes( Storage(
        node = tree,
        currentAction = 'update',
        db = p.db,
        treeInfo = treeInfo,
        insertParams = insertParams ) )

    return Storage( tree = tree, treeId = p.editRecord.gtree )


def forkSaveChanges( p ):

    tree = treeUtil.rollbackTree( Storage( editRecord = p.editRecord, tree = build.gtree( db, p.editRecord.gtree ), db = p.db ) )

    ivy.tree.index( tree )

    treeInfo = treeUtil.getTreeInfoStruct( { 'labelWidthMetric': session.labelWidthMetric,
                                             'generationSeparation': 20 } )

    treeUtil.getTreeInfo( { 'node': tree, 'generation': 1, 'info': treeInfo } )

    treeId = treeUtil.createGTreeRecord( Storage( db = p.db, auth = p.auth,
                                                  params = Storage( treeTitle = p.params.treeName,
                                                                    treeComment = p.params.treeComment ) ) )

    insertGNodeParams = Storage( node = tree, db = db, treeInfo = treeInfo, treeId = treeId )

    insertGNodeParams.translation = p.translation; insertGNodeParams.params = p.params

    treeUtil.insertGNodes( insertGNodeParams )

    return Storage( treeId = treeId, tree = tree )


def saveChanges():

    params = Storage( auth = auth, db = db, editRecord = db.gtree_edit[ request.vars.editId ], treeTitle = request.vars.treeTitle, treeComment = request.vars.treeComment )
    
    rvInfo = globals()[ ''.join( [ request.vars.saveType, 'SaveChanges' ] ) ]( params )

    return response.json( { 'treeId': rvInfo.treeId,
                            'render': treeUtil.getNavigateData( { 'tree': rvInfo.tree,
                                                                  'info': { 'viewerHeight': session.viewportHeight,
                                                                            'labelWidthMetric': session.labelWidthMetric } } ) } )

def rollbackTree( p ):

    for treeEdit in p.edits:

        getattr( treeUtil, ''.join( [ treeEdit.action, 'Undo' ] ) )( Storage( db = p.db, tree = p.tree, edit = treeEdit, permanent = p.permanent  ) )



def viewReplace():

    editRecord = db.gtree_edit[ request.args[0] ]

    affectedCladeRecord = None

    if( editRecord.originalTreeType == 'source' ):
       
        affectedCladeRecord = db( ( db.gnode.tree == editRecord.gtree ) &
                                  ( db.gnode.snode == editRecord.affected_clade_id ) ).select()[0]
 
    else:

        affectedCladeRecord = db.gnode[ editRecord.affected_clade_id ]

    tree = treeUtil.rollbackTree( Storage( editRecord = editRecord, tree = build.gtree( db, editRecord.gtree ), db = db ) )

    affectedClade = treeUtil.getNodeById( { 'currentNode': tree, 'id': affectedCladeRecord.id } )

    rv = Storage( id = 0, next = 0 )

    if( affectedCladeRecord.pruned == False ):

        rv.id = affectedCladeRecord.id; rv.next = affectedCladeRecord.next;


    return response.json( { 'affectedClade': rv,
                            'action': 'replace',
                            'targetNodeId': 0,
                            'affectedNodeId': 0,
                            'render': treeUtil.getNavigateData( { 'tree': affectedClade,
                                                                  'info': { 'viewerHeight': session.viewportHeight,
                                                                            'labelWidthMetric': session.labelWidthMetric } } ) } )

def viewGraft():

    editRecord = db.gtree_edit[ request.args[0] ]

    affectedCladeRecord = None

    if( editRecord.originalTreeType == 'source' ):
       
        affectedCladeRecord = db( ( db.gnode.tree == editRecord.gtree ) &
                                  ( db.gnode.snode == editRecord.affected_clade_id ) ).select()[0]
 
    else:

        affectedCladeRecord = db.gnode[ editRecord.affected_clade_id ]

    tree = treeUtil.rollbackTree( Storage( editRecord = editRecord, tree = build.gtree( db, editRecord.gtree ), db = db ) )

    affectedClade = treeUtil.getNodeById( { 'currentNode': tree, 'id': affectedCladeRecord.id } )

    rv = Storage( id = 0, next = 0 )

    if( affectedCladeRecord.pruned == False ):

        rv.id = affectedCladeRecord.id; rv.next = affectedCladeRecord.next;


    return response.json( { 'affectedClade': rv,
                            'targetNodeId': 0,
                            'affectedNodeId': 0,
                            'render': treeUtil.getNavigateData( { 'tree': affectedClade,
                                                                  'info': { 'viewerHeight': session.viewportHeight,
                                                                            'labelWidthMetric': session.labelWidthMetric } } ) } )

def viewGraftUndo():

    editRecord = db.gtree_edit[ request.args[0] ]

    affectedCladeRecord = None
        
    graftedCladeId = db( ( db.gnode.tree == editRecord.gtree ) &
                         ( db.gnode.snode == editRecord.clipboard_node ) ).select()[0].id

    if( editRecord.originalTreeType == 'source' ):
       
        affectedCladeRecord = db( ( db.gnode.tree == editRecord.gtree ) &
                                  ( db.gnode.snode == editRecord.affected_clade_id ) ).select()[0]

                    

    else:

        affectedCladeRecord = db.gnode[ editRecord.affected_clade_id ]
        

    affectedClade = build.gnode2tree( db, affectedCladeRecord.id, ( db.gnode.pruned == False ) )

    graftedClade = treeUtil.getNodeById( { 'currentNode': affectedClade, 'id': graftedCladeId } )

    affectedClade.remove_child( graftedClade )

    rv = Storage( id = 0, next = 0 )

    if( affectedCladeRecord.pruned == False ):

        rv.id = affectedCladeRecord.id; rv.next = affectedCladeRecord.next;

    return response.json( { 'affectedClade': rv,
                            'targetNodeId': 0,
                            'affectedNodeId': 0,
                            'render': treeUtil.getNavigateData( { 'tree': affectedClade,
                                                                  'info': { 'viewerHeight': session.viewportHeight,
                                                                            'labelWidthMetric': session.labelWidthMetric } } ) } )

def viewPrune():

    editRecord = db.gtree_edit[ request.args[0] ]

    affectedCladeRecord = None
    prunedCladeId = editRecord.affected_node_id

    if( editRecord.originalTreeType == 'source' ):
       
        affectedCladeRecord = db( ( db.gnode.tree == editRecord.gtree ) &
                                  ( db.gnode.snode == editRecord.affected_clade_id ) ).select()[0]
 
    else:

        affectedCladeRecord = db.gnode[ editRecord.affected_clade_id ]
        

    tree = treeUtil.rollbackTree( Storage( editRecord = editRecord, tree = build.gtree( db, editRecord.gtree ), db = db ) )

    affectedClade = treeUtil.getNodeById( { 'currentNode': tree, 'id': affectedCladeRecord.id } )

    rv = Storage( id = 0, next = 0 )

    if( affectedCladeRecord.pruned == False ):

        rv.id = affectedCladeRecord.id; rv.next = affectedCladeRecord.next;


    return response.json( { 'affectedClade': rv,
                            'targetNodeId': prunedCladeId,
                            'affectedNodeId': prunedCladeId,
                            'render': treeUtil.getNavigateData( { 'tree': affectedClade,
                                                                  'info': { 'viewerHeight': session.viewportHeight,
                                                                            'labelWidthMetric': session.labelWidthMetric } } ) } )

def viewPruneUndo():
    
    editRecord = db.gtree_edit[ request.args[0] ]

    affectedCladeRecord = None
    prunedCladeId = editRecord.affected_node_id
    prunedClade = None

    if( editRecord.originalTreeType == 'source' ):
       
        affectedCladeRecord = db( ( db.gnode.tree == editRecord.gtree ) &
                                  ( db.gnode.snode == editRecord.affected_clade_id ) ).select()[0]

        prunedClade = build.snode2tree( db, prunedCladeId )

    else:

        affectedCladeRecord = db.gnode[ editRecord.affected_clade_id ]

        prunedClade = build.gnode2tree( db, prunedCladeId, ( ( db.gnode.id == db.prune_detail.pruned_gnode ) &
                                                             ( db.prune_detail.gtree_edit == editRecord.id ) ) )
    
    affectedClade = build.gnode2tree( db, affectedCladeRecord.id, ( db.gnode.pruned == False ) )

    affectedClade.add_child( prunedClade )

    rv = Storage( id = 0, next = 0 )

    if( affectedCladeRecord.pruned == False ):

        rv.id = affectedCladeRecord.id; rv.next = affectedCladeRecord.next;

    return response.json( { 'affectedClade': rv,
                            'targetNodeId': prunedCladeId,
                            'affectedNodeId': prunedCladeId,
                            'render': treeUtil.getNavigateData( { 'tree': affectedClade,
                                                                  'info': { 'viewerHeight': session.viewportHeight,
                                                                            'labelWidthMetric': session.labelWidthMetric } } ) } )



def getGraftedTreeAudit():

    gtreeId = int( request.vars.treeId )

    root = build.gtree( db, gtreeId )
    
    rv = []

    graftHistory = db( ( db.gtree_edit.gtree == gtreeId ) &
                       ( db.gtree_edit.action == 'prune' )  &
                       ( db.gtree_edit.originalTreeType == 'source' ) &
                       ( db.snode.id == db.gtree_edit.affected_node_id ) &
                       ( db.auth_user.id == db.gtree_edit.user ) &
                       ( db.snode.tree == db.stree.id ) &
                       ( db.stree.study == db.study.id) ).select( orderby = db.gtree_edit.mtime )
    
    for rec in graftHistory:
        rv.append( dict( nodeId = rec.gtree_edit.affected_node_id,
                         clade = rec.snode.label,
                         nodeCount = rec.snode.back - rec.snode.next,
                         editId = rec.gtree_edit.id,
                         studyCitation = rec.study.citation,
                         studyId = rec.study.id,
                         user = ' '.join( [ rec.auth_user.first_name, rec.auth_user.last_name ] ),
                         action = rec.gtree_edit.action,
                         datetime = rec.gtree_edit.mtime ) )

    graftHistory = db( ( db.gtree_edit.gtree == gtreeId ) &
                       ( ( ( db.gtree_edit.action != 'prune' ) & ( db.gnode.id == db.gtree_edit.target_gnode ) ) |
                         ( ( db.gtree_edit.action == 'prune' ) & ( db.gtree_edit.originalTreeType == 'grafted' ) & ( db.gnode.id == db.gtree_edit.affected_node_id ) ) ) &
                       ( db.auth_user.id == db.gtree_edit.user ) &
                       ( db.snode.id == db.gnode.snode ) &
                       ( db.snode.tree == db.stree.id ) &
                       ( db.stree.study == db.study.id) ).select( orderby = db.gtree_edit.mtime, distinct=True )

    for rec in graftHistory:

        target = db.gnode[ rec.gtree_edit.affected_node_id ] if rec.gtree_edit.action == 'prune' else db.gnode[ rec.gtree_edit.target_gnode ]

        clade = target.label
        nodeCount = ( target.back - target.next + 1 ) / 2

        affected = None
        replaced = None
        replacedCount = None
         
        if rec.gtree_edit.action == 'graft':

            affected = db.gnode[ db.gnode[ rec.gtree_edit.target_gnode ].parent ].label

        elif rec.gtree_edit.action == 'replace':

            if rec.gtree_edit.originalTreeType == 'source':

                node = db.snode[ rec.gtree_edit.affected_node_id ]

            else:
                
                node = db.gnode[ rec.gtree_edit.affected_node_id ]

            replaced = node.label
            replacedCount = node.back - node.next


        
        rv.append( dict( nodeId = rec.gtree_edit.target_gnode,
                         clade = clade,
                         nodeCount = nodeCount,
                         replaced = replaced,
                         replacedCount = replacedCount,
                         affected = affected,
                         editId = rec.gtree_edit.id,
                         studyCitation = rec.study.citation,
                         studyId = rec.study.id,
                         user = ' '.join( [ rec.auth_user.first_name, rec.auth_user.last_name ] ),
                         action = rec.gtree_edit.action,
                         datetime = rec.gtree_edit.mtime,
                         next = rec.gnode.next ) )


    rootInfo = db( ( db.gnode.id == root.id ) &
                   ( db.snode.id == db.gnode.snode ) &
                   ( db.snode.tree == db.stree.id ) &
                   ( db.stree.study == db.study.id ) &
                   ( db.taxon.id == db.study.focal_clade ) ).select()

    sourceTreeId = db( ( db.gnode.id == root.id ) &
                       ( db.snode.id == db.gnode.snode ) ).select()[0].snode.tree

    otuCount = db( ( db.snode.tree == sourceTreeId ) &
                   ( db.snode.isleaf == True ) ).count()

    sourceCount = db( ( db.gnode.tree == gtreeId ) &
                      ( db.gnode.stree == sourceTreeId ) ).count()

    rv.insert( 0, dict( nodeId = root.id,
                        action = 'root',
                        otuCount = otuCount,
                        sourceCount = sourceCount,
                        studyId = rootInfo[0].study.id,
                        studyCitation = rootInfo[0].study.citation,
                        focalClade = rootInfo[0].taxon.name ) )

    return response.json( { 'graftHistory': rv } )

