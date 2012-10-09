response.subtitle = "Data sets"

def index():
    response.subtitle = A("Source data", _href=URL(c='sdata',f="index"))
    t = db.sdata
    cit = Field("citation")
    t.year_published.requires = IS_NULL_OR(IS_IN_SET(
        [ x.year_published for x in
          db(t.id>0).select(t.year_published, orderby=t.year_published,
                            distinct=True) ]
        ))
    t.contributor.requires = IS_NULL_OR(IS_IN_SET(
        [ x.contributor for x in
          db(t.id>0).select(t.contributor, orderby=t.contributor,
                            distinct=True) ]
        ))
    form = SQLFORM.factory(
        cit, t.year_published, t.contributor,
        _id="searchform", _action=URL(c="sdata", f="search.load")
        )
    return dict(form=form)

def search():
    t = db.sdata
    q = (t.id>0)
    for k, v in [ (k, v) for k, v in request.vars.items()
                  if (k in t.fields) ]:
        if v:
            q &= (t[k].like("%"+v+"%"))
    fields = (t.id, t.citation, t.year_published, t.uploaded)
    rows = db(q).select(*fields)
    headers = dict(
        [ (str(x), (str(x).split(".")[1]).capitalize().replace("_", " "))
          for x in fields ]
        )
    results = SQLTABLE2(rows, headers=headers)
    return dict(results=results)

def load_record():
    i = int(request.args(0) or 0)
    return LOAD("sdata", "record.load", args=[i], vars=request.vars, ajax=True)
    
def record():
    t = db.sdata
    rec = t(int(request.args(0) or 0))
    t.focal_clade.requires = IS_NULL_OR(IS_IN_DB(db, db.taxon.id))
    t.focal_clade.widget = SQLFORM.widgets.autocomplete(
        request, db.taxon.name, id_field=db.taxon.id
        )
    form = SQLFORM(t, rec, _id="recordform", showid=False)
    v = [ LI(A(tr.type, _target="_blank",
               _href=URL(c="stree", f="html", args=[tr.id], extension="")))
          for tr in db(db.stree.sdata==rec).select() ]
    trees = UL(*v)
    if form.accepts(request):
        response.flash = "record updated"
    return dict(form=form, trees=trees)

def create():
    t = db.sdata
    t.focal_clade.widget = SQLFORM.widgets.autocomplete(
        request, db.taxon.name, id_field=db.taxon.id
        )
    t.uploaded.readable=False
    ## fields = ["focal_clade", "citation", "label", "year_published",
    ##           "data", "datafile",
    ##           "contributor", "comment", "uploaded"]
    ## form = SQLFORM(t, fields=fields)
    ## if form.accepts(request.vars, session):
    ##     redirect(URL("view", args=[form.vars.id]))

    form = crud.create(t, next="view/[id]")
    return dict(form=form)

def view():
    rec = db.sdata(request.args(0)) or redirect(URL("create"))
    form = SQLFORM(db.sdata, rec, deletable=True, upload=URL("download"),
                   fields = ["citation", "label", "year_published", "data",
                             "contributor", "datafile", "comment", "uploaded"],
                   showid=False, submit_button="Update record")
    if form.accepts(request.vars, session):
        pass
    label = _sdata_rep(rec)
    trees = db(db.stree.sdata==rec.id).select()
    return dict(form=form, label=label, trees=trees)
        
def download():
    return response.download(request, db)

def strees():
    rows = db(db.stree.sdata==int(request.args(0) or 0)).select()
    return dict(trees=rows)
