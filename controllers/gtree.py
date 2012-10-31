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
  
    #### 
    ownDataSource = db( db.gtree.contributor == ' '.join( [ auth.user.first_name, auth.user.last_name ] ) ).select()

    class ownVirtualFields(object):
        @virtualsettings(label='Tree')
        def tree_url(self):
            gtree = self.gtree.id
            u = URL(c="gtree",f="backbone",args=self.gtree.id, vars=dict(treeType='grafted'))
            return A('grafted', _href=u)

    ownTable = plugins.powerTable
    ownTable._id = 'ownTableId'
    ownTable._class = 'ownTableClass'
    #ownTable.dtfeatures['aoColumns'] = [ '', '', '', '', '' ]
    ownTable.datasource = ownDataSource
    ownTable.dtfeatures["sScrollY"] = "200px"
    ownTable.dtfeatures["sScrollX"] = "100%"
    ownTable.virtualfields = ownVirtualFields()
    ownTable.headers = "labels"
    ownTable.showkeycolumn = False
    ownTable.dtfeatures["bJQueryUI"] = request.vars.get("jqueryui",True)
    ## ownTable.uitheme = request.vars.get("theme","cupertino")
    ownTable.uitheme = request.vars.get("theme","smoothness")
    ownTable.dtfeatures["iDisplayLength"] = 25
    ownTable.dtfeatures["aaSorting"] = [[6,'desc']]
    ownTable.dtfeatures["sPaginationType"] = request.vars.get(
        "pager","full_numbers"
        ) # two_button scrolling
    ownTable.columns = ["gtree.id",
                        "virtual.tree_url",
                        "gtree.mtime",
                        "gtree.title",
                        "gtree.comment" ]

    ownTable.extra = dict(autoresize=True)
    
    return dict( ownedByUser = ownTable.create() )
    
    #### 

    uniqueUserId = db( db.user_map.auth_user_id == auth.user.id ).select()[0].unique_user_id

    shareDataSource = db( ( db.gtree.id == db.gtree_share.gtree ) &
                          ( db.gtree_share.user == uniqueUserId ) ).select()

    class shareVirtualFields(object):
        @virtualsettings(label='Tree')
        def tree_url(self):
            gtree = self.gtree.id
            u = URL(c="gtree",f="view",args=self.gtree.id, vars=dict(treeType='grafted'))
            return A('grafted', _href=u)

    shareTable = plugins.powerTable
    shareTable._id = 'shareTableId'
    shareTable._class = 'shareTableClass'
    #shareTable.dtfeatures['aoColumns'] = [ '', '', '', '', '' ]
    shareTable.datasource = shareDataSource
    shareTable.dtfeatures["sScrollY"] = "200px"
    shareTable.dtfeatures["sScrollX"] = "100%"
    shareTable.virtualfields = shareVirtualFields()
    shareTable.headers = "labels"
    shareTable.showkeycolumn = False
    shareTable.dtfeatures["bJQueryUI"] = request.vars.get("jqueryui",True)
    ## shareTable.uitheme = request.vars.get("theme","cupertino")
    shareTable.uitheme = request.vars.get("theme","smoothness")
    shareTable.dtfeatures["iDisplayLength"] = 25
    shareTable.dtfeatures["aaSorting"] = [[6,'desc']]
    shareTable.dtfeatures["sPaginationType"] = request.vars.get(
        "pager","full_numbers"
        ) # two_button scrolling
    shareTable.columns = ["gtree.id",
                          "virtual.tree_url",
                          "gtree.mtime",
                          "gtree.title",
                          "gtree.comment" ]

    shareTable.extra = dict(autoresize=True)

    return dict( ownedByUser = ownTable.create(), sharedWithUser = shareTable.create() )


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
