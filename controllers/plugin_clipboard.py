import datetime


def addToClipboard():
    return dict( instanceParams = response.json( dict( containerId = request.vars.containerId ) ) )

def viewAndGraft():
    return dict( instanceParams = response.json( dict( containerId = request.vars.containerId, clipboard = getClipboard() ) ) )

def default():
    
    instanceParams = dict( containerId = request.cid )
    instanceParams['clipboard'] = getClipboard()

    return dict( instanceParams = response.json( instanceParams ) )


def getClipboard():
       
    rv = \
        db( ( db.clipboard.id > 0 ) &
               ( db.clipboard.treeType == 'source' ) &
               ( db.clipboard.nodeId == db.snode.id ) &
               ( db.snode.tree == db.stree.id ) &
               ( db.stree.study == db.study.id ) ) \
            .select( db.clipboard.id,
                     db.clipboard.treeType,
                     db.clipboard.nodeId,
                     db.clipboard.name,
                     db.clipboard.creationDate,
                     db.snode.next,
                     db.snode.back,
                     db.study.citation ).as_list()


    rv.extend( \
        db( ( db.clipboard.id > 0 ) &
           ( db.clipboard.treeType == 'grafted' ) &
           ( db.clipboard.nodeId == db.gnode.id ) &
           ( db.gnode.tree == db.gtree.id ) )
        .select( db.clipboard.id,
                 db.clipboard.treeType,
                 db.clipboard.nodeId,
                 db.clipboard.name,
                 db.clipboard.creationDate,
                 db.gnode.next,
                 db.gnode.back,
                 db.gtree.title ).as_list() )

    return rv


def addItem():
    row = db.clipboard.insert( name = request.vars.name, treeType = request.vars.treeType, creationDate = datetime.datetime.now(), nodeId = request.vars.nodeId )
    return response.json( dict( trigger = request.vars.trigger,
                                data = dict( id = row.id, name = row.name, creationDate = row.creationDate, nodeId = row.nodeId, async = True ) ) )


def delete():
    db( db.clipboard.id == request.args[0] ).delete()
    return request.args[0]
