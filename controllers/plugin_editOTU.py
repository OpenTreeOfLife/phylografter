def default():
    
    instanceParams = dict( containerId = request.cid )

    for attr in request.vars:
        instanceParams[ attr ] = request.vars[ attr ]

    return dict( instanceParams = response.json( instanceParams ) )


def getPage():

    page = int( request.vars.page )
    rowsPerPage = int( request.vars.rowsPerPage )

    startIndex = 0 if page == 1 else ( ( page - 1 ) * rowsPerPage )

    rows = db( ( db.snode.isleaf == True ) & ( db.snode.label != '' ) & ( db.snode.tree == int( request.vars.treeId ) ) &
               ( db.snode.otu == db.otu.id ) ).select( orderby=db.snode.next, limitby=( startIndex, rowsPerPage ) )

    return response.json( rows )
