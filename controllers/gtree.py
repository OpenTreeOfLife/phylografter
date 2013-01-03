# coding: utf-8
tree = local_import("tree", reload=True)
build = local_import("build", reload=True)
link = local_import("link")
reload(link)
ivy = local_import("ivy")
reload(ivy.tree)

from gluon.storage import Storage

response.subtitle = "Grafted trees"

@auth.requires_login()
def index():
    return dict()

@auth.requires_login()
def backbone():

    #used for testing
    #del session.TreeViewer

    if( 'TreeViewer' not in session ):
        session.TreeViewer = Storage()

    if( request.vars.treeType ):
        session.TreeViewer.treeType = request.vars.treeType
        session.TreeViewer.strNodeTable = 'snode' if request.vars.treeType == 'source' else 'gnode'
    else:
        session.TreeViewer.treeType = 'source'
        session.TreeViewer.strNodeTable = 'snode'
    
    return dict()


def getGtrees():

    orderby = []

    if request.vars.nameSort:
        orderby.append( db.gtree.title if request.vars.nameSort == 'ascending' else ~db.gtree.title )
    
    if request.vars.creatorSort:
        orderby.append( db.gtree.contributor if request.vars.creatorSort == 'ascending' else ~db.gtree.contributor )
    
    if request.vars.dateSort:
        orderby.append( db.gtree.date if request.vars.dateSort == 'ascending' else ~db.gtree.date )

    start = ( ( int( request.vars.page ) - 1  ) * int( request.vars.rowsOnPage ) )
    end = start + int( request.vars.rowsOnPage )

    limitby = ( start, end )

    q = ( )

    if len( request.vars.nameSearch ):
        q &= db.gtree.title.like( '%' + request.vars.nameSearch + '%' )
    
    if len( request.vars.descriptionSearch ):
        q &= db.gtree.comment.like( '%' + request.vars.descriptionSearch + '%' )
    
    if len( request.vars.creatorSearch ):
        q &= db.gtree.contributor.like( '%' + request.vars.creatorSearch + '%' )

    rows = db( q ).select( db.gtree.id, db.gtree.title, db.gtree.comment, db.gtree.contributor, db.gtree.date,
                           orderby = orderby,
                           limitby = limitby ).as_list()

    totalrecs = db().select( db.gtree.id.count() )[0]._extra['COUNT(gtree.id)']

    disprecs = db( q ).select( db.gtree.id.count() )[0]._extra['COUNT(gtree.id)']

    return response.json( \
        dict( data = rows,
              totalRecords = totalrecs,
              recordsInData = disprecs ) )

