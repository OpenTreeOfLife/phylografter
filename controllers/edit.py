def label():

    db( db.node.id == request.vars.nodeId ).update( label = request.vars.label )
