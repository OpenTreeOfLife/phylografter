def editLabel():
    rv = { 'title': 'Edit Label', 'jsSuccess': request.vars.jsResponse, 'request': str( URL( 'edit', 'label' ) ) }

    currentLabel = db( db.node.id == request.vars.nodeId ).select()[0].label

    rv['form'] = DIV(
                      SPAN( 'Label : ' ),
                      INPUT( _type='text', _value=currentLabel, _id='labelValue'), 
                      INPUT( _type='hidden', _value=request.vars.nodeId, _id='nodeId')
                     ).xml()

    return response.json( rv )
