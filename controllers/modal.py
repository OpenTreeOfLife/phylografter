def standardEditLabel():

    currentLabelValue = db( db.snode.id == request.args[0] ).select()[0].label

    form = str( FORM( 'Label :', INPUT( _name='label', _value=currentLabelValue ),
                                 INPUT( _name='nodeId', _type='hidden', _value=request.args[0] ),
                                 INPUT( _type='submit' ), _action=str( URL( 'edit', 'label' ) ) ).xml() )

    return response.json( { 'title': 'Edit Label', 'form':  form } )

