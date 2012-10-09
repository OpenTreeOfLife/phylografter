def default():
    
    instanceParams = dict( containerId = request.cid )
    instanceParams['userTrees'] = db( db.gtree.contributor == ' '.join( [ auth.user.first_name, auth.user.last_name ] ) ).select().as_list()

    return dict( instanceParams = response.json( instanceParams ) )

def updateCollaboration():

    userId = int( request.vars.userId )
    treeId = ( request.vars.treeId )

    query = ( db.gtree_share.user == userId ) & ( db.gtree_share.gtree == treeId )

    if( db( query ).count() ):

        db( query ).delete()

    else:

        db.gtree_share.insert( user = userId, gtree = treeId )
