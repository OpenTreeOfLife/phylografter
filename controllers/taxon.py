#build = local_import("build")
import build
from gluon.sql import Field

response.subtitle = "Taxa"

def index():
    theme = "smoothness"
    for x in (
        'DataTables-1.8.1/media/js/jquery.js',
        'DataTables-1.8.1/media/js/jquery.dataTables.min.js',
        'DataTables-1.8.1/media/css/bootstrap_table.css',
        'DataTables-1.8.1/media/ui/css/%s/jquery-ui-1.8.5.custom.css' % theme):
        response.files.append(URL('static',x))

    t = db.taxon
    fields = t.fields
    colnames = ["Id", "Name", "Rank", "NCBI taxid", "APG name"]
    widths = ["5%", "30%", "15%", "15%", "15%"]
    tid = "taxa"
    table = TABLE(_id=tid, _class="display")
    table.append(THEAD(TR(*[ TH(f, _width=w)
                             for f, w in zip(colnames, widths) ])))
    table.append(TBODY(TR(TD("Loading data from server",
                             _colspan=len(fields),
                             _class="dataTables_empty"))))
    table.append(TFOOT(TR(*[ TH(INPUT(_name="search_%s" % f,
                                      _style="width:100%",
                                      _class="search_init",
                                      _title="search %s" % c))
                             for f, c in zip(fields, colnames) ])))
    return dict(tid=tid, table=table)

def dtrecords():
    ## for k, v in sorted(request.vars.items()):
    ##     print k, ":", v
    t = db.taxon
    fieldnames = t.fields
    fields = [ t[x] for x in fieldnames ]
    orderby = []
    if request.vars.iSortCol_0:
        for i in range(int(request.vars.iSortingCols or 1)):
            col = int(request.vars.get("iSortCol_%s" % i))
            ## print fields[i]
            scol = fields[col]
            sdir = request.vars.get("sSortDir_%s" % i) or "asc"
            if sdir == "desc": scol = ~scol
            ## print sdir
            orderby.append(scol)
    start = int(request.vars.iDisplayStart or 0)
    end = start + int(request.vars.iDisplayLength or 10)
    limitby = (start,end)
    q = q0 = (t.id>0)#&(t["ncbi_taxid"].like('%3071%'))
    if request.vars.sSearch:
        q &= t.name.like('%'+request.vars.sSearch+'%')
    for i, f in enumerate(fields):
        sterm = request.vars.get("sSearch_%s" % i)
        if sterm:
            if f.name == "apg_taxon":
                q &= ((t.apg_taxon==db.apg_taxon.id)&
                      (db.apg_taxon.name.like('%'+sterm+'%')))
            else:
                q &= f.like('%'+sterm+'%')
    rows = db(q).select(*fields, orderby=orderby, limitby=limitby)
    def rep(row, fname):
        if t[fname].represent: return t[fname].represent(row[fname])
        return row[fname]
    data = [ [ rep(row, fn) for fn in fieldnames ] for row in rows ]
    totalrecs = db(q0).count()
    disprecs = db(q).count()
    return dict(aaData=data,
                iTotalRecords=totalrecs,
                iTotalDisplayRecords=disprecs,
                sEcho=int(request.vars.sEcho))

def children():
    t = db.taxon
    rec = t(request.args(0))
    q = (t.parent==rec.id)
    rows = list(db(q).select())

def browse():
    rec = db.taxon(request.args(0)) or redirect("index")
    u = URL("children", args=[rec.id])

def stree():
    i = int(request.args(0) or 0)
    rec = db.stree(i)
    assert rec
    t = db.snode
    q = ((t.tree==i)&(t.label!=None))
    rows = db(q).select(t.id, t.label, t.taxon)
    return dict(tree=rec, nodes=rows)

def snode_widget():
    i = int(request.args(0) or 0)
    return LOAD("taxon", "view_snode.load",
                args=[i], vars=request.vars, ajax=True)

def view_snode():
    i = int(request.args(0) or 0)
    rec = db.snode(i)
    s = "None assigned"
    avars = dict(target=request.vars.target,edit=1)
    if rec.taxon:
        s = rec.taxon.name
        if rec.taxon.ncbi_taxon:
            s = s+" [%s]" % rec.taxon.ncbi_taxon.taxid
    c = None
    cvars = dict(target=request.vars.target,edit=1,cancel=1)
    if (((not request.vars.edit) and
         ("_autocomplete_name" not in request.vars)) or
        request.vars.cancel):
        form = None
        a = A(s, _href=URL("snode_widget", args=[i], vars=avars),
              cid=request.vars.target, _style="background-color:yellow")

    else:
        a = None
        f = Field("taxid", "integer",
                  requires=[IS_NULL_OR(IS_IN_DB(db, "taxon.id"))],
                  widget=SQLFORM.widgets.autocomplete(
                      request, db.taxon.name, id_field=db.taxon.id
                      ))
        form = SQLFORM.factory(f)
        c = A("Cancel", _href=URL("snode_widget", args=[i], vars=cvars),
              cid=request.vars.target)
        if form.accepts(request.vars, session):
            taxon = db.taxon(form.vars.taxid)
            if taxon and (not request.vars.cancel):
                rec.update_record(taxon=taxon)
                s = rec.taxon.name
                if rec.taxon.ncbi_taxon:
                    s = s+" [%s]" % rec.taxon.ncbi_taxon.taxid
            elif (not taxon) and (not request.vars.cancel):
                rec.update_record(taxon=None)
                s = "None assigned"
            else:
                pass
            form = None
            a = A(s, _href=URL("snode_widget", args=[i], vars=avars),
                  cid=request.vars.target, _style="background-color:yellow")
            c = None
    return dict(form=form, rec=rec, a=a, c=c)

def restore():
    lim = 100
    i = int(request.args(0) or 1)
    t = db.taxon
    r = t[i]
    q = (t.next>r.next)&(t.back<r.back)
    recs = db(q).select(limitby=(0,lim), orderby=t.next)
    R = r
    N = ivy.tree.Node(); N.isroot = True; N.rec = R
    for r in recs:
        n = ivy.tree.Node()
        n.rec = r
        if r.next==r.back-1:
            n.isleaf = True
        assert r.parent == N.rec.id
        N.add_child(n)
        if not n.isleaf:
            N = n
        elif r.back == N.rec.back-1:
            N = N.parent
    return N

def ncbi_search():
    rec = db.taxon(request.args(0)) or redirect("error")
    w = SQLFORM.widgets.autocomplete(
        request, db.ncbi_taxon.name, id_field=db.ncbi_taxon.id
        )
    db.taxon.ncbi_taxon.widget = w
    form = SQLFORM(db.taxon, rec, fields=["ncbi_taxon"], showid=False)
    if form.accepts(request.vars, session):
        form = DIV()
    return dict(form=form)

def error():
    return dict(form=DIV("no record"))

def test():
    component = LOAD(c="taxon", f="ncbi_search.load",
                     args=[request.args(0)], ajax=True)
    return jq("#modal").html(component)()

def search():
    t = db.taxon
    q = (t.ncbi_taxon==None)&(t.next!=t.back-1)
    recs = db(q).select(orderby=t.name)
    v = []
    for r in recs:
        d = DIV(r.name, _id="ncbi-taxon-%s" % r.id)
        event.listen("click", d, test, args=[r.id])
        v.append(d)
    parent_ids = [ x.parent for x in recs if x.parent ]
    i2p = dict([ (p.id, p.name) for p in
                 db(t.id.belongs(parent_ids)).select() ])
    parents = dict([ (r.id, i2p.get(r.parent) or "") for r in recs ])
    return dict(recs=recs, v=v, parents=parents)

