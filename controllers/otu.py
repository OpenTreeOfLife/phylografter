# coding: utf-8
from uuid import uuid4
from gluon.storage import Storage

response.subtitle = "OTUs"

## def index():
##     t = db.study

##     class Virtual(object):
##         @virtualsettings(label='OTUs')
##         def otu_url(self):
##             study = t[self.study.id]
##             n = db(db.otu.study==study.id).count()
##             if n > 0:
##                 u = URL(c="otu",f="study",args=[study.id])
##                 return A("%s OTUs" % n, _href=u)
##             else:
##                 return "%s OTUs" % n

##         @virtualsettings(label='Study')
##         def study_url(self):
##             study = t[self.study.id]
##             u = URL(c="study",f="view",args=[study.id])
##             s = study.citation
##             if len(s)>65: s = s[:60]+" ..."
##             return A(s, _href=u, _title=study.citation)

##     powerTable = plugins.powerTable
##     powerTable.datasource = t
##     powerTable.dtfeatures["sScrollY"] = "100%"
##     powerTable.dtfeatures["sScrollX"] = "100%"
##     powerTable.virtualfields = Virtual()
##     powerTable.headers = "labels"
##     powerTable.showkeycolumn = False
##     powerTable.dtfeatures["bJQueryUI"] = request.vars.get("jqueryui",True)
##     ## powerTable.uitheme = request.vars.get("theme","cupertino")
##     powerTable.uitheme = request.vars.get("theme","smoothness")
##     powerTable.dtfeatures["iDisplayLength"] = 25
##     powerTable.dtfeatures["aaSorting"] = [[6,'desc']]
##     powerTable.dtfeatures["sPaginationType"] = request.vars.get(
##         "pager","full_numbers"
##         ) # two_button scrolling
##     powerTable.columns = ["study.id",
##                           "study.focal_clade",
##                           "virtual.study_url",
##                           "study.year_published",
##                           "virtual.otu_url",
##                           "study.uploaded"]
##     #powerTable.hiddencolumns = ["study.treebase_id"]
##     ## details = dict(detailscallback=URL(c="study",f="details"))
##     ## powerTable.extra = dict(autoresize=True,
##     ##                         tooltip={},
##     ##                         details=details)
##     powerTable.extra = {}
   
##     return dict(table=powerTable.create())    

## def study():
##     t = db.otu
##     study = db.study(request.args(0)) or redirect(URL("index"))

##     class Virtual(object):
##         @virtualsettings(label='Taxon')
##         def taxon(self):
##             ## taxon = db.taxon(t[self.otu.id].taxon) or Storage()
##             if auth.has_membership(role="contributor"):
##                 return taxon_link(self.otu.id)
##             else:
##                 rec = db.taxon(self.otu.taxon) or Storage()
##                 return SPAN(rec.name)
            
##     powerTable = plugins.powerTable
##     powerTable.datasource = db(t.study==study).select()
##     powerTable.virtualfields = Virtual()
##     powerTable.dtfeatures["sScrollY"] = "100%"
##     powerTable.dtfeatures["sScrollX"] = "100%"
##     powerTable.virtualfields = Virtual()
##     powerTable.headers = "labels"
##     powerTable.showkeycolumn = False
##     powerTable.dtfeatures["bJQueryUI"] = request.vars.get("jqueryui",True)
##     ## powerTable.uitheme = request.vars.get("theme","cupertino")
##     powerTable.uitheme = request.vars.get("theme","smoothness")
##     powerTable.dtfeatures["iDisplayLength"] = 25
##     powerTable.dtfeatures["aaSorting"] = [[1,'asc']]
##     powerTable.dtfeatures["sPaginationType"] = request.vars.get(
##         "pager","full_numbers"
##         ) # two_button scrolling
##     powerTable.columns = ["otu.id",
##                           "otu.label",
##                           "virtual.taxon"]
##     ## powerTable.hiddencolumns = ["stree.type"]

##     ## details = dict(detailscallback=URL(c="stree",f="details"))
##     ## powerTable.extra = dict(autoresize=True,
##     ##                         tooltip={},
##     ##                         details=details)
##     study_url = A(_study_rep(study),
##                   _href=URL(c="study",f="view",args=[study.id]))
##     N = db(db.otu.study==study.id).count()
##     return dict(study_url=study_url, N=N, table=powerTable.create())

def studyNew():
    study = db.study(request.args(0)) or redirect(URL("index"))

    return dict( study = study )


def getStudyOTUs():

    study = db.study( request.vars.studyId )

    otuTable = db.otu

    left = db.ottol_name.on( db.ottol_name.id == otuTable.ottol_name )

    fields = [ otuTable.label, db.ottol_name.name ]

    orderby = []

    """ 
    if request.vars.iSortCol_0:
        for i in range(int(request.vars.iSortingCols or 1)):
            col = int(request.vars.get("iSortCol_%s" % i))
            scol = fields[col]
            sdir = request.vars.get("sSortDir_%s" % i) or "asc"
            if sdir == "desc": scol = ~scol
            orderby.append(scol)
    """


    start = ( ( int( request.vars.page ) - 1  ) * int( request.vars.rowsOnPage ) ) + 1
    end = start + int( request.vars.rowsOnPage )

    limitby = ( start, end )

    q = q0 = ( otuTable.study == study.id )

    if len( request.vars.labelSearch ):
        q &= otuTable.label.like( '%' + request.vars.labelSearch + '%' )
    
    if len( request.vars.taxonSearch ):
        q &= db.ottol_name.name.like( '%' + request.vars.taxonSearch + '%' )

    def tx(otu):
        if auth.has_membership(role="contributor"):
            return taxon_link(otu)
        else:
            return SPAN(otu.ottol_name.name if otu.ottol_name else '')

    rows = db( q ).select( otuTable.id, otuTable.label, otuTable.ottol_name,
                           left = left,
                           orderby = orderby,
                           limitby = limitby )

    data = [ (r.label, tx(r).xml()) for r in rows ]
    
    totalrecs = db(q0).count()

    disprecs = db(q).count()

    return response.json( \
        dict( data = data,
              totalRecords = totalrecs,
              recordsInData = disprecs ) )


def study():
    t = db.otu
    study = db.study(request.args(0)) or redirect(URL("index"))
    theme = "smoothness"
    for x in (
        'DataTables-1.8.1/media/js/jquery.js',
        'DataTables-1.8.1/media/js/jquery.dataTables.min.js',
        'DataTables-1.8.1/media/css/demo_table.css',
        'DataTables-1.8.1/media/ui/css/%s/jquery-ui-1.8.5.custom.css' % theme):
        response.files.append(URL('static',x))

    colnames = ["Label", "Taxon"]
    widths = ["50%", "50%"]
    tid = "study-otus"
    table = TABLE(_id=tid, _class="display")
    table.append(THEAD(TR(*[ TH(f, _width=w)
                             for f, w in zip(colnames, widths) ])))
    table.append(TBODY(TR(TD("Loading data from server",
                             _colspan=len(colnames),
                             _class="dataTables_empty"))))
    table.append(TFOOT(TR(
        TH(INPUT(_name="search_label",
                 _style="width:100%",_class="search_init",
                 _title="search label" )),
        TH(INPUT(_name="search_taxon",
                 _style="width:100%",_class="search_init",
                 _title="search taxon" ))
        )))

    return dict(tid=tid, table=table, study=study)
    
def dtrecords():
    ## for k, v in sorted(request.vars.items()):
    ##     print k, ":", v
    study = db.study(request.args(0)) or redirect(URL("index"))
    t = db.otu
    left = db.ottol_name.on(db.ottol_name.id==t.ottol_name)
    fields = [ t.label, db.ottol_name.name ]
    orderby = []
    print request.vars
    if request.vars.iSortCol_0:
        for i in range(int(request.vars.iSortingCols or 1)):
            col = int(request.vars.get("iSortCol_%s" % i))
            scol = fields[col]
            sdir = request.vars.get("sSortDir_%s" % i) or "asc"
            if sdir == "desc": scol = ~scol
            orderby.append(scol)
    start = int(request.vars.iDisplayStart or 0)
    end = start + int(request.vars.iDisplayLength or 10)
    limitby = (start,end)
    q = q0 = (t.study==study.id)
    for i, f in enumerate(fields):
        sterm = request.vars.get("sSearch_%s" % i)
        if f and sterm:
            q &= f.like('%'+sterm+'%')
                
    def tx(otu):
        if auth.has_membership(role="contributor"):
            return taxon_link(otu)
        else:
            return SPAN(otu.ottol_name.name if otu.ottol_name else '')

    rows = db(q).select(t.id, t.label, t.ottol_name,
                        left=left, orderby=orderby, limitby=limitby)

    data = [ (r.label, tx(r).xml()) for r in rows ]
    totalrecs = db(q0).count()
    disprecs = db(q).count()
    return dict(aaData=data,
                iTotalRecords=totalrecs,
                iTotalDisplayRecords=disprecs,
                sEcho=int(request.vars.sEcho))
    
def taxon_link(otu):
    ## print otu.keys()
    taxon = db.ottol_name(otu.ottol_name) or Storage()
    ## d = request.vars
    ## if d.otu != otu: d.otu = otu
    ## if d.taxon != taxon.id: d.taxon = taxon.id
    ## d = dict(otu=otu, taxon=taxon.id)
    u = URL(c="otu",f="taxon_edit.load",args=[otu.id])
    uid = uuid4().hex
    return SPAN(A(str(taxon.name), _href=u, cid=uid), _id=uid)

def taxon_edit():
    otu = db.otu(int(request.args(0)))
    field = Field("taxon", "integer", default=otu.ottol_name)
    field.widget = SQLFORM.widgets.autocomplete(
        request, db.ottol_name.unique_name, id_field=db.ottol_name.id,
        orderby=db.ottol_name.unique_name)
    form = SQLFORM.factory(field, formstyle="divs")
    if form.accepts(request.vars, session):
        taxon = form.vars.taxon
        if taxon != otu.ottol_name:
            ## response.flash="record updated"
            otu.update_record(ottol_name=taxon)
            otu.snode.update(ottol_name=taxon)
        return dict(form=None, cancel=None, a=taxon_link(otu))

    cancel = A("Cancel",
               _href=URL(c="otu",f="taxon_edit_cancel.load",args=[otu.id]),
               cid=request.cid)
    return dict(form=form, cancel=cancel, a=None)

def taxon_edit_cancel():
    r = db.otu(request.args(0))
    ## t = db.otu
    ## left = db.ottol_name.on(db.ottol_name.id==t.ottol_name)
    ## r = db(t.id==request.args(0)).select(
    ##     t.id, t.label, db.ottol_name.name, left=left).first()
    return taxon_link(r)
