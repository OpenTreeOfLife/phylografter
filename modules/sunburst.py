def getRenderResponse( clade, session ):
   
    rootNode = dict( name = clade.label, children = [ ] )

    rv = dict( renderData = rootNode )

    getRenderResponseRecurse( clade, session, rootNode );

    return rv


def getRenderResponseRecurse( clade, session, curNode ):

    for child in clade.children:
        childNode = dict( name = clade.label or '', children = [ ] )
        curNode['children'].append( childNode )
        getRenderResponseRecurse( child, session, childNode )

    if( len( clade.children ) == 0 ):
        curNode['size'] = 3000
        del curNode['children']
