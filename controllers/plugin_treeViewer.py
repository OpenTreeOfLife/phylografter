build = local_import("build", reload=True)

util = local_import( "plugin_treeViewer", reload = True )

from gluon.storage import Storage


def treeViewer():
    """
    This function handles a request made when plugin_treeViewer is invoked in a view.
    Because the treeViewer plugin is a superclass to the treeGrafter plugin, on the client and server,
    this function routes the request to the tree viewer module where plugins that inherit from the
    tree viewer can use. 

    Currently, there are two ways to instantiate a treeViewer. You can either pass in a treeId and a treeType
    ( 'source', 'grafted' ), or, you can pass in a python tree object.  All of the parameters have not
    been fully fleshed out.

    Load from treeId :

    {{=plugin_treeViewer(
        dict( treeId = request.args(0),
              treeType = 'source',
              eventInfo = dict( labelClick = dict( type = 'getUrlForm', url = str( URL( c='modal', f='editSnodeTaxon' ) ) ),
                                nodeRightClick = dict( type = 'contextMenu', options = [ 'collapseClade', 'addToClipboard' ] ) ),
              viewInfo = dict( mode = 'navigate' ) ) ) }}
    """

    return util.handleViewerInstantiation( request, response, session, db )


def getMatchingDescendantLabels():

    value = ''.join( [ '\'%', request.vars.value, '%\'' ] )

    nTbl = session.TreeViewer.strNodeTable

    pageLength = session.TreeViewer.config.collapsedCladeSearchPageLength
    limit = ''.join( [ 'LIMIT ', str( ( int( request.vars.page ) - 1 ) * pageLength ), ', ', str( pageLength ) ] )

    query = [ \
        'SELECT SQL_CALC_FOUND_ROWS ', nTbl, '.id, ' , nTbl, '.label, taxon.name, ', nTbl, '.next, ', nTbl, '.back '
        'FROM ', nTbl, ' LEFT JOIN taxon ON ', nTbl, '.taxon = taxon.id ',
        'WHERE ', nTbl, '.tree = ', session.TreeViewer.treeId, ' AND ' ]

    if( int( request.vars.next ) != 1 ):

        query.append( ''.join( [ \
            nTbl, '.next > ', request.vars.next, ' AND ',
            nTbl, '.back < ', request.vars.back, ' AND ' ] ) )

    query.append( ''.join( ['( ', nTbl, '.label LIKE ', value, ' OR taxon.name LIKE ', value, ' ', ' ) ', limit, ';' ] ) )

    limitedRows = db.executesql( ''.join( query ) );
    total = db.executesql( 'SELECT FOUND_ROWS();' )

    return response.json( dict( rows = limitedRows, total = total ) )


def updateConfig():
    """This function updates the tree viewer configuration on the server."""

    treeConfig = session.TreeViewer.treeConfig[ session.TreeViewer.treeId ]

    names = request.vars.names.split(',')
    values = request.vars.vals.split(',')

    for i in range ( len( names ) ):

        if( hasattr( treeConfig[ names[i] ], 'type' ) ):\

            if( treeConfig[ names[i] ].type == 'int' ):
                treeConfig[ names[i] ].value = int( values[i] )
        else:
            treeConfig[ names[i] ] = values[i]

    session.TreeViewer.config.update( treeConfig )

    return response.json( session.TreeViewer.config )


def getConfig():
    """
    This function returns tree viewer configuration to the client.  You can find the configuration variables
    in the tree viewer module in the setConfig function.
    """

    return response.json( session.TreeViewer.config )


def getMaxTips():
    return session.TreeViewer.config.maxTips.value


def collapseClade():

    return response.json( util.getRenderModule( request, session ).collapseClade( db, session, request ) )


def refreshColumn():

    return response.json( util.getRenderModule( request, session ).refreshColumn( db, session, request ) )


def horizontallyExpandNode():

    return response.json( util.getRenderModule( reuqest, session ).horizontallyExpandNode( db, session, request ) )


def verticallyExpandNode():

    return response.json( util.getRenderModule( request, session ).verticallyExpandNode( db, session, request ) )

    
def getTree():

    return response.json( util.getRenderModule( request, session ).getTree( db, session, request ) )


def collapseExpandedNode():

    return response.json( util.getRenderModule( request, session ).collapseExpandedNode( db, session, request ) )


def removeColumns():

    return response.json( util.getRenderModule( request, session ).removeColumns( db, session, request ) )


def addColumn():

    return response.json( util.getRenderModule( request, session ).addColumn( db, session, request ) )


def addItemToClipboard():
    row = db.clipboard.insert( name = request.vars.name, treeType = request.vars.treeType, creationDate = datetime.datetime.now(), nodeId = request.vars.nodeId )
    return response.json( dict() )
