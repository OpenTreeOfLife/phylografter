treeUtil = local_import("treeUtil", reload=True)
viewerUtil = local_import("viewerUtil", reload=True)
from gluon.storage import Storage

#ivy = local_import("ivy", reload=True)
import ivy_local as ivy
build = local_import("build", reload=True)
util = local_import( "plugin_treeViewer", reload = True )
graftUtil = local_import( "plugin_treeGrafter", reload = True )


def treeGrafter():
    """
    This function is invoked when an ajax request is made by calling plugin_treeGrafter in a view.
    Like other viewer plugins ( treeViewer ), this function calls handleViewerInstantiation to send
    a response to the client
    """
    
    return util.handleViewerInstantiation( request, response, session, db, auth )


def getCreator():

    return db( db.gtree.id == session.TreeViewer.treeId ).select( db.gtree.contributor )[0].contributor


def getUserInfo():

    
    canEdit = len( \
        db( ( db.gtree_share.user == auth.user.id ) & ( db.gtree_share.gtree == session.TreeViewer.treeId ) ).select().as_list() )
   
    if canEdit == 0:
        canEdit =  len( \
            db( ( db.gtree.id == session.TreeViewer.treeId ) & ( db.gtree.contributor == ' '.join( [ auth.user.first_name, auth.user.last_name ] ) ) ).select().as_list() )

    return response.json( dict( firstName = auth.user.first_name, lastName = auth.user.last_name, canEdit = canEdit ) )


def pruneClade():

    return response.json( util.getRenderModule( request, session, 'Graft' ).pruneClade( db, session, request, auth ) )


def replaceClade():

    return response.json( util.getRenderModule( request, session, 'Graft' ).replaceClade( db, session, request, auth ) )


def graftClade():

    return response.json( util.getRenderModule( request, session, 'Graft' ).graftClade( db, session, request, auth ) )


def updateUrl():

    return response.json( dict( treeId = session.TreeViewer.treeId, treeType = session.TreeViewer.treeType ) )


def getGtreeSharingInfo():

    return response.json( \
        dict( sharedWith = db(
                ( db.gtree_share.gtree == session.TreeViewer.treeId ) &
                ( db.gtree_share.user == db.auth_user.id ) &
                ( db.gtree_share.user != auth.user.id ) ).select( db.auth_user.ALL ).as_list(),

              notSharedWith = db( ~db.auth_user.id.belongs(
                    db( ( db.gtree_share.gtree == session.TreeViewer.treeId ) &
                        ( db.gtree_share.user == db.auth_user.id ) |
                        ( db.auth_user.id == auth.user.id ) )._select( db.auth_user.id ) ) )
                            .select( db.auth_user.first_name, db.auth_user.last_name, db.auth_user.id ).as_list() ) )


def getGtreeGraftHistory():

    return response.json( \
        db( ( db.gtree_edit.gtree == session.TreeViewer.treeId ) &
            ( db.gtree_edit.user == db.auth_user.id ) )
            .select( orderby = db.gtree_edit.mtime ).as_list() )

def giveEditPermission():

    db.gtree_share.insert( user = request.vars.userId, gtree = session.TreeViewer.treeId )


def removeEditPermission():

    db( ( db.gtree_share.user == request.vars.userId ) & ( db.gtree_share.gtree == session.TreeViewer.treeId ) ).delete()


def showTreeBeforeEdit():

    editRow = db( db.gtree_edit.id == request.vars.editId ).select()[0]

    columns = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].columns

    tree = getattr( build, ''.join( [ session.TreeViewer.treeType, 'Clade' ] ) )( db, columns[0].rootNodeId, Storage() )

    grafts = db( ( db.gtree_edit.gtree == session.TreeViewer.treeId ) &
                 ( db.gtree_edit.mtime >= editRow.mtime ) ).select( orderby = "mtime DESC" )

    for graft in grafts:
        graftUtil.revertEdit( db, session, tree, graft )

    ivy.tree.index( tree )

    return response.json( util.getRenderModule( request, session ).getRenderResponse( \
        tree,
        session,
        Storage( rootNodeId = columns[0].rootNodeId,
                 keepVisibleNodeStorage = Storage(),
                 collapsedNodeStorage = Storage() ),
        collapseNodes = False ) )


def revertEdit():

    treeState = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ]

    editInfo = db( db.gtree_edit.id == request.vars.editId ).select()[0]
    
    editsAfter = db( ( db.gtree_edit.gtree == session.TreeViewer.treeId ) &
                     ( db.gtree_edit.mtime >= editInfo.mtime ) ).select( orderby = "mtime DESC" )
    
    for edit in editsAfter:

        if( edit.action == 'replace' or edit.action == 'graft' ):

            cladeToDelete = db.gnode[ edit.target_gnode ]

            nodesToDelete = db( ( db.gnode.pruned == False ) &
                                ( db.gnode.next >= cladeToDelete.next ) &
                                ( db.gnode.back <= cladeToDelete.back ) &
                                ( db.gnode.tree == session.TreeViewer.treeId ) ).select( db.gnode.id )

            for nodeToDelete in nodesToDelete:
               
                for column in treeState.columns:
                    
                    if nodeToDelete.id in column.collapsedNodeStorage:
                        del column.collapsedNodeStorage[ nodeToDelete.id ]

            db( ( db.gnode.pruned == False ) &
                ( db.gnode.next >= cladeToDelete.next ) &
                ( db.gnode.back <= cladeToDelete.back ) &
                ( db.gnode.tree == session.TreeViewer.treeId ) ).delete()


        if( edit.action == 'prune' or edit.action == 'replace' ):
        
            nodesToPrune = db( db.prune_detail.gtree_edit == edit.id ).select( db.prune_detail.pruned_gnode )

            for node in nodesToPrune:
                
                db( db.gnode.id == node.pruned_gnode ).update( pruned = False )
        
            db( db.prune_detail.gtree_edit == edit.id ).delete()

        
        db( db.gtree_edit.id == edit.id ).delete()




#### below this line is old
def deleteGtree():
    #if we allow deleting gtrees, then we have to know what to do with clipboard items referring to those gtrees
    return response.json( dict() )




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

# this function formerly in modules/util.py
def normalizeUsers( p ):

    db = p.db

    authUsers = db( db.auth_user.id > 0 ).select( orderby = db.auth_user.last_name )

    for user in authUsers:

        if( db( db.unique_user.last_name == user.last_name ).count() == 0 ):

            uniqueUserId = db.unique_user.insert( first_name = user.first_name, last_name = user.last_name )

            db.user_map.insert( auth_user_id = user.id, unique_user_id = uniqueUserId )

        elif( db( ( db.unique_user.last_name == user.last_name ) &
                  ( db.unique_user.first_name == user.first_name) ).count() == 1 ):

            uniqueUserId = db( ( db.unique_user.last_name == user.last_name ) &
                               ( db.unique_user.first_name == user.first_name) ).select()[0].id

            if( db( ( db.user_map.unique_user_id == uniqueUserId ) &
                    ( db.user_map.auth_user_id == user.id ) ).count() == 0 ):

                    db.user_map.insert( auth_user_id = user.id, unique_user_id = uniqueUserId )

        else:

            sameLastNames = db( db.unique_user.last_name == user.last_name ).select()

            found = False

            for person in sameLastNames:

                if( ( person.first_name in user.first_name ) or
                    ( user.first_name in person.first_name ) ):

                    found = True

                    if( db( ( db.user_map.unique_user_id == person.id ) &
                            ( db.user_map.auth_user_id == user.id ) ).count() == 0 ):

                            db.user_map.insert( auth_user_id = user.id, unique_user_id = person.id )

                    break

            if( found == False ):

                uniqueUserId = db.unique_user.insert( first_name = user.first_name, last_name = user.last_name )

                db.user_map.insert( auth_user_id = user.id, unique_user_id = uniqueUserId )
