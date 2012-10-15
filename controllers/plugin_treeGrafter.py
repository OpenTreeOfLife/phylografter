treeUtil = local_import("treeUtil", reload=True)
viewerUtil = local_import("viewerUtil", reload=True)
from gluon.storage import Storage

ivy = local_import("ivy", reload=True)
build = local_import("build", reload=True)
util = local_import( "plugin_treeViewer", reload = True )
graftUtil = local_import( "plugin_treeGrafter", reload = True )


def treeGrafter():
    """
    This function is invoked when an ajax request is made by calling plugin_treeGrafter in a view.
    Like other viewer plugins ( treeViewer ), this function calls handleViewerInstantiation to send
    a response to the client
    """
    
    return util.handleViewerInstantiation( request, response, session, db )


def pruneClade():

    return response.json( util.getRenderModule( request, session, 'Graft' ).pruneClade( db, session, request, auth ) )



def updateURL():

    return response.json( dict( treeId = session.TreeViewer.treeId, treeType = session.TreeViewer.type ) )


def getRecentlyCreatedGTree():

    tree = build.tree( db, session.recentlyCreatedGTreeId, session.TreeViewer.type )

    util.autoCollapse( tree, session, db, 'cladogram', [ ] )

    return util.getRenderResponse( response, session, tree )


def getPreEditClade():

    editRow = db( db.gtree_edit.id == request.vars.editId ).select()[0]

    clade = build.node2tree( db, editRow.affected_clade_id, 'grafted' )

    grafts = db( ( db.gtree_edit.gtree == session.TreeViewer.treeId ) &
                 ( db.gtree_edit.mtime >= editRow.mtime ) ).select( orderby = "mtime DESC" )

    for graft in grafts:
        graftUtil.revertEdit( db, session, clade, graft )

    util.autoCollapse( clade, session, db, 'cladogram', [ ] )

    return util.getRenderResponse( response, session, clade )


def getPostEditClade():

    editRow = db( db.gtree_edit.id == request.vars.editId ).select()[0]

    clade = build.node2tree( db, editRow.affected_clade_id, 'grafted' )

    grafts = db( ( db.gtree_edit.gtree == session.TreeViewer.treeId ) &
                 ( db.gtree_edit.mtime > editRow.mtime ) ).select( orderby = "mtime DESC" )


    for graft in grafts:
        graftUtil.revertEdit( db, session, clade, graft )

    util.autoCollapse( clade, session, db, 'cladogram', [ ] )

    return util.getRenderResponse( response, session, clade )

       
        
def graftClade():

    tree = build.tree( db, session.TreeViewer.treeId, session.TreeViewer.type )

    newCladeRecord = db( db.clipboard.id == request.vars.clipboardNodeId ).select().first()

    newCladeSiblingId = int( request.vars.affectedNodeId )

    graftUtil.graftClade( tree, newCladeSiblingId, build.node2tree( db, newCladeRecord.nodeId, newCladeRecord.treeType ) )



def postGraftDBUpdate():
    
    graftUtil.postGraftDBUpdate( db, session, auth )


def replaceClade():

    tree = build.tree( db, request.vars.treeId, session.TreeViewer.type )

    newClade = db( db.clipboard.id == request.vars.clipboardNodeId ).select()[0]

    replacedCladeId = int( request.vars.affectedNodeId )

    graftUtil.replaceClade( tree, replacedCladeId, build.node2tree( db, newClade.nodeId, newClade.treeType ) )

    request.vars.clipboardNodeType = newClade.treeType

    graftUtil.postReplaceDBUpdate( db, session, auth, tree, session.TreeViewer.type, replacedCladeId, newClade.nodeId, request.vars )


def postPruneDBUpdate():
    graftUtil.postPruneDBUpdate( db, session, auth )


def getGtreeGraftHistory():

    return response.json( \
        db( ( db.gtree_edit.gtree == session.TreeViewer.treeId ) &
            ( db.auth_user.id == db.gtree_edit.user ) ).select( orderby = db.gtree_edit.mtime ).as_list() )


def deleteGtree():
    #if we allow deleting gtrees, then we have to know what to do with clipboard items referring to those gtrees
    return response.json( dict() )



#below is old..
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


###Old - hopefully deprecated###
def navigateExpandNode():

    root = build.gnode2tree( db, request.vars.nodeId, ( db.gnode.pruned == False ) )

    return response.json( treeUtil.getNavigateData( { 'tree': root, 'info': { 'viewerHeight': session.viewportHeight,
                     
                                                                              'labelWidthMetric': session.labelWidthMetric } } ) )
def navigateGetTree():

    session.labelWidthMetric = float( request.vars.labelWidthMetric )
    session.viewportHeight = int( request.vars.viewportHeight )

    root = build.gtree( db, request.args[0] )
    
    return response.json( treeUtil.getNavigateData( { 'tree': root,
                                                      'info': { 'viewerHeight': session.viewportHeight,
                                                                'labelWidthMetric': session.labelWidthMetric } } ) )


def navigateViewGraft():
    
    return response.json( dict() )

    gTreeId = int( request.vars.treeId )
    editId = int( request.vars.editId )

    sourceTree = build.stree( db, db( ( db.gnode.tree == gTreeId ) &
                                      ( db.gnode.next == 1 ) &
                                      ( db.snode.id == db.gnode.snode ) &
                                      ( db.stree.id == db.snode.tree ) ).select( db.stree.id )[0] )


    grafts = db( ( db.gtree_edit.gtree == gTreeId ) &
                 ( db.gtree_edit.mtime <= db( db.gtree_edit.id == editId ).select( db.gtree_edit.mtime )[0] ) ).select( orderby = db.gtree_edit.mtime )


    for graft in grafts:
        treeUtil.graft( { 'graft': graft, 'tree': sourceTree } )

    return response.json( dict() )
    




def navigateGetGraftView():

    baseTree = None

    if request.vars.treeType == 'source':

       baseTree = build.snode2tree( db, request.vars.affectedCladeId )

    elif request.vars.editId:
       
       baseTree = treeUtil.rollbackTree( Storage( editRecord = db.gtree_edit[ request.vars.editId ],
                                                  tree = build.gtree( db, request.vars.treeId ), db = db ) )
       
       baseTree = treeUtil.getNodeById( { 'currentNode': baseTree, 'id': int( request.vars.affectedCladeId ) } )
       
    elif request.vars.treeType == 'grafted':

       baseTree = build.gnode2tree( db, request.vars.affectedCladeId, ( db.gnode.pruned == False ) )

    
    newSiblingClade = build.snode2tree( db, request.vars.clipboardNodeId )
    
    if( request.vars.graftType == 'graft' ):
        baseTree.add_child( newSiblingClade )
    elif( request.vars.graftType == 'replace' ):
        childToRemove = treeUtil.getNodeById( { 'currentNode': baseTree,
                                                'id': int( request.vars.affectedNodeId ) } )
        baseTree.remove_child( childToRemove )
        baseTree.add_child( newSiblingClade )
    
    return response.json( treeUtil.getNavigateData( { 'tree': baseTree, 'info': { 'viewerHeight': session.viewportHeight,
                                                                                  'labelWidthMetric': session.labelWidthMetric } } ) )



def commitGraftAction():
    
    params = treeUtil.handleGraftParams( request.vars )
    params.db = db; params.auth = auth; params.session = session

    return response.json( getattr( treeUtil, ''.join( [ params.treeType, params.viewMode.title(), params.graftType.title() ] ) )( params ) )


def isTreeOwner():

   treeId = int( request.args[0] ) 

   if( db.gtree[ treeId ].contributor == ' '.join( [ auth.user.first_name, auth.user.last_name ] ) ):

        return response.json( True )

   else:

        return response.json( False )



def getCurrentCollaborators():

    #util.normalizeUsers( Storage( db = db ) )

    treeId = int( request.args[0] )

    users = db( db.unique_user.id > 0 ).select( orderby = db.unique_user.last_name )
    
    treeCollaborators = db( ( db.unique_user.id == db.gtree_share.user ) &
                            ( db.gtree_share.gtree == treeId ) ).select()

    rv = Storage( viewOnly = [], viewEdit = [] )

    for user in users:

        info = Storage( id = user.id, name = ' '.join( [ user.first_name, user.last_name ] ) )

        found = False

        for collab in treeCollaborators:

            if( collab.unique_user.id == user.id ):

                found = True; break

        uniqueUserId = db( db.user_map.auth_user_id == auth.user.id ).select()[0].unique_user_id

        if( user.id != uniqueUserId ):

            if( found ):
                rv.viewEdit.append( info )
            else:
                rv.viewOnly.append( info )

    return response.json( rv )
