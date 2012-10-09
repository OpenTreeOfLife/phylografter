def default():
    return dict( eventInfo = response.json(request.vars.eventInfo) )


def getTreeLabels():
    
    table = 'gnode' if request.vars.treeType == 'grafted' else 'snode'

    return response.json( db( ( db[ table ].tree == request.vars.treeId ) &
                              ( db[ table ].label != '') ).select( db[table].id, db[table].next, db[table].label, orderby=db[table].next ).as_dict() )
