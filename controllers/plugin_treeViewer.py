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


def setTreeViewerHeight():
    """
    When a webpage containing a tree viewer is loaded, the client sends the height of the tree viewer container
    to the server so that it can be referenced when necessary - for example, if the viewer is displaying a large tree
    without scrolling, then this value is needed
    """
    session.TreeViewer.containerHeight = int( request.args[0] )


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

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.collapseClade( db, session, request ) )



def collapseCladeProcessedOLD():
    """
    This function handles a collapse clade request

    request.vars : nodeId ( node to be collapsed ),
                   rootId ( clade being refreshed ),
                   collapsedNodeIds ( a list of nodeIds that are already collapsed, if any )
    """

    collapsedNodeIds = [ int( request.vars.nodeId ) ]

    if( len( request.vars.collapsedNodeIds ) ):

        collapsedNodeIds.extend( [ int( id ) for id in request.vars.collapsedNodeIds.split(':') ] )

    ( clade, collapsedNodeRecs ) = util.determineTreeToRender( db, session, request.vars.rootId, collapsedNodeIds )

    return util.getRenderResponseNew( response, session, db, clade, collapsedNodeRecs )



def refreshColumn():

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.refreshColumn( db, session, request ) )


def refreshColumnPROCESSEDOLD():
    """This function handles a request to refresh a column - this is called when changes are made to a node

      request.vars : rootId ( clade being refreshed ),
                     collapsedNodeIds ( a list of nodeIds that are already collapsed )
    """
  
    collapsedNodeIds = [ int( id ) for id in request.vars.collapsedNodeIds.split(',') if id != request.vars.nodeId ]
     
    ( clade, collapsedNodeRecs ) = util.determineTreeToRender( db, session, request.vars.rootId, collapsedNodeIds )

    return util.getRenderResponseNew( response, session, db, clade, collapsedNodeRecs )



def navigateToNodePROCESSEDOLD():
    """
    This function handles a request to render a particular node
    """
    
    session.TreeViewer.status.keepVisibleNodeIds = [ int( request.vars.nodeId ) ];

    nodeTable = db.snode if session.TreeViewer.type == 'source' else db.gnode

    nodeRec = db( nodeTable.id == request.vars.nodeId ).select()[0]

    session.TreeViewer.status.keepVisibleNodeIds.extend(
        [ rec['id'] for rec in db( ( nodeTable.next < nodeRec.next ) &
                                   ( nodeTable.back > nodeRec.back ) &
                                   ( nodeTable.tree == session.TreeViewer.treeId ) ).select().as_list() ] )

    
    ( clade, collapsedNodeRecs ) = util.determineTreeToRender( db, session, request.vars.nodeId, [ ] )

    return util.getRenderResponseNew( response, session, db, clade, collapsedNodeRecs )

    
    
def horizontallyExpandNode():

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.horizontallyExpandNode( db, session, request ) )


def verticallyExpandNode():

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.verticallyExpandNode( db, session, request ) )



def verticallyExpandNodePROCESSEDOLD():
    """
    This function handles a request to expand a collapsed node in a vertical manner
                          
    request.vars : nodeId ( node to be expanded ),
                   rootId ( clade being refreshed ),
                   collapsedNodeIds ( a list of nodeIds that are already collapsed )
                   keepVisibleNodeIds ( a list of nodeIds that ancestors of the nodeToBeExpanded )
    """

    collapsedNodeIds = [ int( id ) for id in request.vars.collapsedNodeIds.split(',') if id != request.vars.nodeId ]

    session.TreeViewer.status.keepVisibleNodeIds.append( int( request.vars.nodeId ) )
    session.TreeViewer.status.keepVisibleNodeIds.extend( [ int( id ) for id in request.vars.keepVisible.split(',') ] )

    session.TreeViewer.config.maxTips += int( session.TreeViewer.config.maxTips * .5 )
    
    ( clade, collapsedNodeRecs ) = util.determineTreeToRender( db, session, request.vars.rootId, collapsedNodeIds )

    return util.getRenderResponseNew( response, session, db, clade, collapsedNodeRecs )

    
def getTree():

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.getTree( db, session, request ) )


def collapseExpandedNode():

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.collapseExpandedNode( db, session, request ) )

def removeColumns():

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.removeColumns( db, session, request ) )


def addColumn():

    renderModule = getRenderModule( request, session )

    return response.json( renderModule.addColumn( db, session, request ) )


def getCladePROCESSEDOLD():
    
    ( clade, collapsedNodeRecs ) = util.determineTreeToRender( db, session, request.vars.nodeId, [ ] )

    return util.getRenderResponseNew( response, session, db, clade, collapsedNodeRecs )



def isTreePreProcessed():

    rv = False

    if( db( ( db.treeMeta.tree == session.TreeViewer.treeId ) &
            ( db.treeMeta.treeType == session.TreeViewer.type ) ).count() == 1 ):

        rv = True

    return response.json( dict( value = rv ) )


def preProcessTree():
    
    treeId = request.vars.treeId if request.vars.treeId else session.TreeViewer.treeId
    treeType = request.vars.treeType if request.vars.treeType else session.TreeViewer.type

    import sys
    sys.stdout.write( "\nasdasd\n" )
    sys.stdout.write( str( treeId ) )
    sys.stdout.write( str( session.TreeViewer.treeId ) )
    sys.stdout.write( "\nasdasd\n" )
    sys.stdout.write( str( treeType ) )
    sys.stdout.write( str( session.TreeViewer.type ) )
    sys.stdout.write( "\nasdasd\n" )
    tree = build.tree( db, treeId, treeType )
    util.gatherTreeInfo( tree, session, db, True )


def getRenderModule( request, session ):

    val = 'processed' if session.TreeViewer.isTreePreprocessed else 'unprocessed'
    moduleName = ''.join( [ val, session.TreeViewer.viewInfo['type'].capitalize() ] )

    root = [ 'applications', '.', 
            request.application, '.',
            'modules', '.' ]

    highLevelModule = __import__(
        ''.join( [ ''.join( root ), moduleName  ] ) )

    renderModule = getattr( getattr( getattr( highLevelModule, root[2] ), root[4] ), moduleName )

    reload( renderModule )

    return renderModule

def getTreeOldProcessed():
    """
    """

    ( clade, collapsedNodeRecs ) = util.determineTreeToRender( db, session, 'root', [ ] )

    return util.getRenderResponseNew( response, session, db, clade, collapsedNodeRecs )


def browseGetTree():
    """
    This function handles a request for an entire tree.  Browse refers to a plugin view mode where the entire tree is rendered
    and scroll bars will appear if necessary.
    """

    #( clade, collapsedNodeRecs ) = util.determineTreeToRender( db, session, request.args[0], [ ] )

    clade = build.tree( db, session.TreeViewer.treeId, session.TreeViewer.type )

    return util.getRenderResponseNew( response, session, db, clade, [] )


def getDescendantLabelsForUnprocessedClade():
    return

def getDescendantLabels():

    rv = dict( nodeId = request.vars.nodeId )

    nodeTable = db[ session.TreeViewer.strNodeTable ]
    nodeRecord = db( nodeTable.id == request.vars.nodeId ).select().first()

    nodeMetaRecord = db( ( db.phylogramNodeMeta.nodeId == request.vars.nodeId ) &
                         ( db.phylogramNodeMeta.treeType == session.TreeViewer.type ) &
                         ( db.phylogramNodeMeta.tree == session.TreeViewer.treeId ) ).select().first()

    import sys
    sys.stdout.write( "\nasdadsasdasd\n" ) 
    sys.stdout.write( str( nodeMetaRecord ) ) 
    sys.stdout.write( "\nbbbbbbbbsdasd\n" ) 
    sys.stdout.write( str( session.TreeViewer.config.collapsedCladeSearchThreshold ) ) 
    sys.stdout.write( "\nbbbbbbbbsdasd\n" ) 

    if( nodeMetaRecord.descendantLabelCount > session.TreeViewer.config.collapsedCladeSearchThreshold ):
        rv['labels'] = 'search'
    else:
        rv['labels'] = \
            db( ( db.phylogramNodeMeta.next > nodeRecord.next ) &
                ( db.phylogramNodeMeta.back < nodeRecord.back ) &
                ( db.phylogramNodeMeta.treeType == session.TreeViewer.type ) &
                ( db.phylogramNodeMeta.tree == session.TreeViewer.treeId ) &
                ( db.phylogramNodeMeta.text != None ) ).select( db.phylogramNodeMeta.text ).as_list()

    return response.json( rv )

def addItemToClipboard():
    row = db.clipboard.insert( name = request.vars.name, treeType = request.vars.treeType, creationDate = datetime.datetime.now(), nodeId = request.vars.nodeId )
    return response.json( dict() )
