def index():
    return dict()
  
def addTreeComponent():
    return dict()


def getNodeInfo():
    node = db( db.node.id == request.vars.nodeId ).select( )[0]

    return response.json( { 'nodeId': node.id, 'treeId': node.treeId, 'label': node.label } )
    


def editLabel():
    db( db.node.id == request.vars.nodeId ).update( label = request.vars.newLabel )

    return dict()

def editLabelDialogue():

    form = DIV( '', _class='zBoxOverlay' ), \
            DIV( 
                DIV( 'Edit Label', _id='zBoxTitle' ),
                FORM(  
                    DIV( 
                        SPAN( 'Label : ' ),
                        INPUT( _type='text', _value=request.vars.currentLabel, _id='editLabelNewLabel' ), 
                        INPUT( _type='hidden', _value=request.vars.nodeId, _id='editLabelNodeId' ),
                        _class='zBoxForm' ),
                    DIV( 
                        DIV( 
                            A( 'Submit', _href='javascript:void(0)', _id='zBoxSubmit' ),
                            _class='fLeft width50' ),
                        DIV( 
                            A( 'Cancel', _href='javascript:void(0)', _id='zBoxCancel', _onclick='closeZBox();' ),
                            _class='fRight width50' ),
                        DIV( '', _class='clear' ),
                        _class='zBoxFormActions' ),
                    _action=URL('editLabel'), _name='editLabel' ),
                _id='zBoxContent' )

    response.js = 'showZBox()'

    return dict( form = form )

def treeVisual():
    import gluon.contrib.simplejson as json

    args = XML("""{
                    nodeId: $(this).attr('nodeId'),
                    currentLabel: $(this).text(),
                  }
               """)
        
    return dict( { 'handleLabelClick': { 'request': 'editLabelDialogue.load',
                                         'args': args } } )


def zBox():
    return dict()

def treeInfoPanel():
    return { 'treeInfoList': [ { 'id': row.id, 'name': row.name, 'creationDate': row.creationDate }
                                for row in db(  db.tree.id > 0 ).select( db.tree.id, db.tree.name, db.tree.creationDate ) ] }

def addTree():
    import datetime
    newick = local_import('newick')

    treeObj = None

    try:
        treeObj = newick.parse( request.vars.newick )
    except:
        return 'parseError'

    treeRow = db.tree.insert( name = request.vars.name, creationDate = datetime.datetime.now() )
    
    insertTreeNodes( { 'node': treeObj, 'treeId': treeRow.id } )

    return response.json( { 'id': treeRow.id, 'creationDate': treeRow.creationDate, 'name': treeRow.name } )


def insertTreeNodes( p ):
    nodeId = db.node.insert( treeId = p['treeId'], label = p['node'].label, left = p['node'].id, right = p['node'].rightId ).id

    for attr in [ 'length' ]:
        if hasattr( p['node'], attr ):
            db.nodeMeta.insert( nodeId = nodeId, key = attr, value = getattr( p['node'], attr ) )

    for child in p['node'].children:
        insertTreeNodes( { 'node': child, 'treeId': p['treeId'] } )


def getTree():

    tree = buildTree( { 'nodes': db( db.node.treeId == request.vars.treeId ).select( db.node.id, db.node.label, db.node.left, db.node.right, orderby = db.node.left ) } )

    return ''.join( [ '{ "id": "', request.vars.treeId,
                      '", "tree": ', tree.emit_json(), ' }' ] )


def buildTree( p ):
    phylo = local_import('phylo')
    
    root = None
    currentNode = None

    for node in p['nodes']:
        if currentNode:
            while( currentNode.rightId < node.right ):
                currentNode = currentNode.parent

        treeNode = phylo.Node()
        treeNode.id = node.id
        treeNode.rightId = node.right;
        treeNode.label = node.label;

        if currentNode:
            currentNode.add_child( treeNode )
            currentNode = treeNode
        else:
            root = treeNode
            currentNode = treeNode

    return root

   
   
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
