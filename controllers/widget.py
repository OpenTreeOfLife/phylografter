from gluon.storage import Storage
build = local_import("build", reload=True)

def treeVisual():
    t = db.snode
    tree = buildTree({'nodes': db(t.tree==request.vars.treeId).select(
        t.id, t.label, t.next, t.back, orderby = t.next
        )})
    
    return widgetWrapper( { 'data':
                            { 'treeInfo': { 'id': request.vars.treeId,
                                            'tree': convertTreeToDict( tree ),
                                            'events' : { 'handleLabelClick': 'standardEditLabel' } } } } )

def stree_vis_edit_taxon():
    t = db.snode
    i = int(request.vars.treeId or 0)
    assert i
    root = build.stree(db, i)
    d = taxon_edit_treedict(root)
    return widgetWrapper({'data':
                          {'treeInfo': {'id': i,
                                        'tree': d,
                                        'events': {'handleLabelClick': 'editSnodeTaxon'}}}})
    
def modalBox():
    return widgetWrapper( { 'data': { },
                            'view': True } )    


def widgetWrapper( p ):
    import gluon.contrib.simplejson as json

    if 'view' not in p:
         response.view = 'widget/wrapper.load'
  
    p['data']['containerId'] = request.cid; 

    response.write( SCRIPT( ''.join( [ 'widgetResponseHandler("', request.function, '", ', 'eval( "(" + \'', json.dumps( p['data'] ), '\' + ")" ) );' ] ), _language='javascript' ), escape=False )

    return dict( )


def taxon_edit_treedict(node):
    label = node.label or "[%s]" % node.rec.id
    if node.rec.taxon:
        label = "%s [%s]" % (node.rec.taxon.name, node.rec.taxon.id)
    d = {'id': node.id, 'label': label,
         'children': [ taxon_edit_treedict(c) for c in node.children ]}
    return d


def convertTreeToDict( tree ):
    treeDict = { 'id': tree.id, 'label': tree.label, 'children': [ ] }
    
    def traverseTree( p ):
        currentDict = { }
        currentDict['id'] = p['node'].id
        currentDict['label'] = p['node'].label
        currentDict['children'] = [ ]
        for child in p['node'].children:
            currentDict['children'].append( traverseTree( { 'node': child } ) )
        return currentDict

    for child in tree.children:
        treeDict['children'].append( traverseTree( { 'node': child } ) )

    return treeDict


def tree():

    treeId = request.args[0]

    tree = buildTree( { 'nodes': db( db.node.treeId == treeId ).select( db.node.id, db.node.label, db.node.left, db.node.right, orderby = db.node.left ) } )
    
    treeInfo = getTreeInfo( { 'tree': tree } )

    buffer = 100
    generationSeparation = 40
    siblingSeparation = 20

    firstTip = { 'x': ( generationSeparation * treeInfo.depth ) - buffer,
                 'y': ( siblingSeparation * treeInfo.tips ) - buffer }
    
    pathString = generatePathString( { 'clade': tree,
                                       'currentTip': firstTip,
                                       'depth': treeInfo.depth,
                                       'config': { 'generationSeparation': generationSeparation,
                                                   'siblingSeparation': siblingSeparation } } )

    return { 'pathString': pathString,
             'canvasWidth': ( generationSeparation * treeInfo.depth ) + ( buffer * 2 ),
             'canvasHeight': ( siblingSeparation * treeInfo.tips ) + ( buffer * 2 ) }



def getTreeInfo( p ):
    
    treeInfo = Storage( { 'tips': 0,
                          'depth': 0 } )

    def traverseTree( q ):
       
        if q['node'].children:
            treeInfo.depth += 1
            for child in q['node'].children:
                traverseTree( { 'node': child } )
        else:
            treeInfo.tips += 1

    traverseTree( { 'node': p['tree'] } )

    return treeInfo



def generatePathString( p ):

    p = Storage(p)

    rv = Storage( pathString = '' )

    def traverseTree( q ):

        node = q['node']
        children = node.children

        for child in children:
            traverseTree( { 'node': child } )

        if children:

            node.x = children[0].x + children[0].dx
            node.dx = - p.config['generationSeparation']
            node.y = ( children[ -1 ].y + children[0].y ) / 2

            rv.pathString = ''.join( [ rv.pathString, "M", str(node.x), " ", str(children[0].y), "L", str(node.x), " ", str(children[ -1 ].y) ] )
        else:

            node.x = p.currentTip['x']
            node.dx = -( p.config['generationSeparation'] * p.depth )
            node.y = p.currentTip['y']

            p.currentTip['y'] += p.config['siblingSeparation']

        rv.pathString = ''.join( [ rv.pathString, "M", str(node.x), " ", str(node.y), "l", str(node.dx), " 0" ] )

    traverseTree( { 'node': p.clade } )
    
    return rv.pathString


def buildTree( p ):
    import ivy_local as ivy
    
    root = None
    currentNode = None

    for node in p['nodes']:
        if currentNode:
            while( currentNode.back < node.back ):
                currentNode = currentNode.parent

        treeNode = ivy.tree.Node()
        treeNode.id = node.id
        treeNode.back = node.back
        treeNode.label = node.label
        treeNode.rec = node

        if currentNode:
            currentNode.add_child( treeNode )
            currentNode = treeNode
        else:
            root = treeNode
            root.isroot = True
            currentNode = treeNode

    return root

