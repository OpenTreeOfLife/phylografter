import plugin_common as common
import build as build
import forceDirected
reload( forceDirected )
import sunburst
reload( sunburst )
import math

from gluon.storage import Storage
from types import *

def handleViewerInstantiation( request, response, session, db ):
    """
    This function handles a viewer instantiation request.  This is not fully fleshed out - more details to come.
    In controllers/plugin_treeViewer.py, def treeViewer, can provide more information as well.
    """

    instanceParams = dict( containerId = request.cid, treeType = session.TreeViewer.treeType )
    instanceParams['treeId'] = session.TreeViewer.treeId = request.vars.treeId

    session.TreeViewer.viewInfo = common.evaluate( request.vars.viewInfo )

    addThingsToSession( session, db )
    
    instanceParams['totalNodes'] = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].totalNodes
    instanceParams[ 'allNodesHaveLength' ] = session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ].allNodesHaveLength

    for param in [ 'eventInfo', 'viewInfo', 'menuInfo' ]:
        if( param in request.vars ):
            instanceParams[ param ] = common.evaluate( request.vars[ param ] )

    for param in [ 'auxPlugins' ]:
        if( param in request.vars ):
            if( type( request.vars[ param ] ) is ListType ):
                instanceParams[ param ] = [ common.evaluate( strDict ) for strDict in request.vars[ param ] ]
            else:
                instanceParams[ param ] = [ common.evaluate( request.vars[ param ] ) ]

    
    for param in [ 'modal' ]:
        if( param in request.vars ):
            instanceParams[ param ] = request.vars[ param ]

    instanceParams[ 'isTreePreprocessed' ] = session.TreeViewer.isTreePreprocessed = False

    return dict( instanceParams = response.json( instanceParams ) )


def addThingsToSession( session, db ):

    initializeViewerConfig( session ) 

    initializeTreeConfig( session )

    session.TreeViewer.config.update( session.TreeViewer.treeConfig[ session.TreeViewer.treeId ] )

    initializeTreeState( session, db )




def initializeViewerConfig( session ):

    if( 'config' not in session.TreeViewer ):
        session.TreeViewer.config = Storage( \
            largeCladeThreshold = 20000,
            nodesProcessedPerSecond = 5000,
            internalLabelBackdropColor = 'yellow',
            internalLabelBackdropOpacity = .5,
            nonTipLabelBuffer = -5,
            nodeSelectorRadius = 5,
            nodeSelectorOpacity = .7,
            nodeSelectorColor = 'blue',
            collapsedCladeColor = 'grey',
            collapsedCladeSearchThreshold = 25,
            collapsedCladeSearchPageLength = 25,
            minimumCollapsedUIWidth = 10,
            scaledBranchingCollapseUIBuffer = 5 )


def initializeTreeConfig( session ):

    if 'treeConfig' not in session.TreeViewer:
        session.TreeViewer.treeConfig = Storage()

    if session.TreeViewer.treeId not in session.TreeViewer.treeConfig:
        session.TreeViewer.treeConfig[ session.TreeViewer.treeId ] = \
            globals()[ ''.join( [ 'initialize', session.TreeViewer.viewInfo[ 'type' ].capitalize(), 'TreeConfig' ] ) ]()

def initializePhylogramTreeConfig():

    return Storage( \
        verticalTipBuffer = Storage( value = 20, type = 'int' ),
         branchLength = Storage( value = 20, type = 'int' ),
         branchLengthStyle = 'smooth',
         maxTips = Storage( value = 50, type = 'int' ),
         verticalPadding = 50,
         horizontalPadding = 50,
         tipLabelBuffer = 10,
         pathWidth = 3,
         treeColor = 'black',
         fontFamily = 'Verdana',
         fontSize = Storage( value = 12, type = 'int' ) )

    '''
    if( session.TreeViewer.treeType == 'grafted' ):

        config.primaryShowEditColor = 'red'
        config.secondaryShowEditColor = 'blue'
        config.tertiaryShowEditColor = 'yellow'
    '''

def initializeTreeState( session, db ):
  
    if not 'treeState' in session.TreeViewer:
        session.TreeViewer.treeState = Storage( source = Storage(), grafted = Storage() )

    if( not session.TreeViewer.treeId in session.TreeViewer.treeState[ session.TreeViewer.treeType ] ):
        session.TreeViewer.treeState[ session.TreeViewer.treeType ][ session.TreeViewer.treeId ] = \
            globals()[ ''.join( [ 'initialize', session.TreeViewer.viewInfo[ 'type' ].capitalize(), 'TreeState' ] ) ]( session, db )


def initializePhylogramTreeState( session, db ):

    rootNodeRowInfo = db.executesql( \
        ''.join( [ 'SELECT id, back FROM ',
                   session.TreeViewer.strNodeTable,
                   ' WHERE tree = ', session.TreeViewer.treeId, ' AND next = 1' ] ) )[0]

    session.TreeViewer.rootNodeId = rootNodeRowInfo[ 0 ]

    #this is fast - how?
    dbNodeTable = db.snode if session.TreeViewer.treeType == 'source' else db.gnode
    allNodesHaveLength = True if db( ( dbNodeTable.tree == session.TreeViewer.treeId ) &
                                     ( dbNodeTable.next != 1 ) &
                                     ( dbNodeTable.length == None ) ).count() == 0 else False


    return Storage( \
        allNodesHaveLength = allNodesHaveLength,
        totalNodes = ( ( rootNodeRowInfo[1] - 2 ) / 2 ),
        columns = [ Storage( rootNodeId = rootNodeRowInfo[0], 
                           keepVisibleNodeStorage = Storage(),
                           collapsedNodeStorage = Storage() ) ],
        formerlyCollapsedNodeStorage = Storage() )



def isAncestor( possibleAncestor, possibleDescendant ):

    possibleDescendant = normalizeNextBack( possibleDescendant )
    possibleAncestor = normalizeNextBack( possibleAncestor )

    if( ( possibleDescendant['next'] > possibleAncestor['next'] ) and
        ( possibleDescendant['back'] < possibleAncestor['back'] ) ):

        return True

    else:

        return False


def isDescendant( possibleDescendant, possibleAncestor ):

    possibleDescendant = normalizeNextBack( possibleDescendant )
    possibleAncestor = normalizeNextBack( possibleAncestor )
    
    if( ( possibleDescendant['next'] > possibleAncestor['next'] ) and
        ( possibleDescendant['back'] < possibleAncestor['back'] ) ):

        return True

    else:

        return False


def normalizeNextBack( arg ):

    if( hasattr( arg, 'next' ) ):
        return dict( next = arg.next, back = arg.back )
    else:
        return arg


def getNodeById( currentNode, nodeId ):

    if( nodeId == currentNode.id ):
        return currentNode
    else:
        for child in currentNode.children:
            ret = getNodeById( child, nodeId )
            if ret:
                return ret
    return None


def getDescendantLabels( clade ):

    descendantLabels = [ ]

    for child in clade.children:
        getDescendantLabelsRecurse( child, descendantLabels )

    return descendantLabels


def getDescendantLabelsRecurse( clade, descendantLabels ):

   if clade.text:
       descendantLabels.append( dict( text = clade.text, nodeId = clade.id, next = clade.next, back = clade.back ) )

   for child in clade.children:
    getDescendantLabelsRecurse( child, descendantLabels )


def getRenderModule( request, session, suffix = '' ):

    moduleName = ''.join( [ 'unprocessed', session.TreeViewer.viewInfo['type'].capitalize(), suffix ] )

    root = [ 'applications', '.', 
            request.application, '.',
            'modules', '.' ]

    highLevelModule = __import__(
        ''.join( [ ''.join( root ), moduleName  ] ) )

    renderModule = getattr( getattr( getattr( highLevelModule, root[2] ), root[4] ), moduleName )

    reload( renderModule )

    return renderModule
