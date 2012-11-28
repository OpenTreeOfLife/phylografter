import datetime

def viewAndGraft():
    return dict( instanceParams = response.json( dict( containerId = request.vars.containerId, clipboard = getClipboard() ) ) )

def default():
    
    instanceParams = dict( containerId = request.cid )
    instanceParams['clipboard'] = getClipboard()

    return dict( instanceParams = response.json( instanceParams ) )


def getClipboard():

    queryStringList = [ \
        'SELECT ',
            'clipboard.id, ',
            'clipboard.nodeId, ',
            'clipboard.name, ',
            'clipboard.creationDate, ',
            'snode.next, ',
            'snode.back, ',
            'study.id, ',
            'study.citation, ',
            'snode.tree, ',
            'snode.id ',
        'FROM clipboard JOIN snode ON ( snode.id = clipboard.nodeId AND clipboard.treeType = "source" ) ',
                       'JOIN stree ON stree.id = snode.tree ',
                       'JOIN study ON study.id = stree.study ' ]
       
    sourceList = db.executesql( ''.join( queryStringList ) )

    queryStringList = [ \
        'SELECT ',
            'clipboard.id, ',
            'clipboard.nodeId, ',
            'clipboard.name, ',
            'clipboard.creationDate, ',
            'gnode.next, ',
            'gnode.back, ',
            'gtree.id, ',
            'gtree.title ',
        'FROM clipboard JOIN gnode ON ( gnode.id = clipboard.nodeId AND clipboard.treeType = "grafted" ) ',
                       'JOIN gtree ON gtree.id = gnode.tree ' ]

    graftedList = db.executesql( ''.join( queryStringList ) )
        
    return response.json( dict( sourceList = sourceList, graftedList = graftedList ) )


def addItemToClipboard():
    row = db.clipboard.insert( \
        name = request.vars.name,
        treeType = session.TreeViewer.treeType,
        creationDate = datetime.datetime.now(),
        user = auth.user.id,
        nodeId = request.vars.nodeId )

    return response.json( dict() )


def delete():
    db( db.clipboard.id == request.args[0] ).delete()
    return request.args[0]
