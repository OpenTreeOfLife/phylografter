# coding: utf-8
## tree = local_import("tree", reload=True)
## build = local_import("build", reload=True)
## link = local_import("link")
import sys
import tree
import build
import link
import ivy_local as ivy
import treeUtil
import nexson
import urllib
## ivy = local_import("ivy")

from gluon.storage import Storage

ivy.newick.add_label_chars('?')

response.subtitle = "Source trees"

## def index():
##     t = db.stree

##     class Virtual(object):
##         @virtualsettings(label='Study')
##         def study_url(self):
##             study = t[self.stree.id].study
##             u = URL(c="study",f="view",args=[study.id])
##             s = study.citation
##             N = 50
##             if len(s)>N: s = s[:N-3]+" ..."
##             return A(s, _href=u, _title=study.citation)

##         @virtualsettings(label='Tree')
##         def tree_url(self):
##             stree = t[self.stree.id]
##             u = URL(c="stree",f="svgView",args=[self.stree.id])
##             return A(stree.type, _href=u)

##         @virtualsettings(label='Focal Clade')
##         def clade(self):
##             study = t[self.stree.id].study
##             fc = db.study[study].focal_clade
##             name = fc.name if fc else ""
##             return name

##         @virtualsettings(label='OTUs')
##         def ntax(self):
##             q = ((db.snode.tree==self.stree.id)&
##                  (db.snode.isleaf==True))
##             return db(q).count()

##     powerTable = plugins.powerTable
##     powerTable.datasource = t
##     powerTable.virtualfields = Virtual()
##     powerTable.dtfeatures["sScrollY"] = "100%"
##     powerTable.dtfeatures["sScrollX"] = "100%"
##     #powerTable.virtualfields = Virtual()
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
##     powerTable.columns = ["stree.id",
##                           "virtual.clade",
##                           "virtual.study_url",
##                           "virtual.tree_url",
##                           "virtual.ntax",
##                           ## "stree.contributor",
##                           "stree.uploaded"]
##     powerTable.hiddencolumns = ["stree.type"]

##     ## details = dict(detailscallback=URL(c="stree",f="details"))
##     powerTable.extra = dict(autoresize=True)
   
##     return dict(table=powerTable.create())

def index():
    theme = "smoothness"
    for x in (
        # 'DataTables-1.8.1/media/js/jquery.js',  # there's already a newer (Bootstrap-compatible) jQuery loaded!
        'DataTables-1.8.1/media/js/jquery.dataTables.min.js',
        'DataTables-1.8.1/media/css/bootstrap_table.css',
        'DataTables-1.8.1/media/ui/css/%s/jquery-ui-1.8.5.custom.css' % theme):
        response.files.append(URL('static',x))

    colnames = ["Id", "Focal clade", "Study", "Tree type",
                "Leaves", "Uploaded", "By"]
    widths = ["2%", "10%", "25%", "15%", "7%", "15%", "10%"]
    tid = "strees"
    table = TABLE(_id=tid, _class="display")
    table.append(THEAD(TR(*[ TH(f, _width=w)
                             for f, w in zip(colnames, widths) ])))
    table.append(TBODY(TR(TD("Loading data from server",
                             _colspan=len(colnames),
                             _class="dataTables_empty"))))
    table.append(TFOOT(TR(
        TH(INPUT(_name="search_id",
                 _style="width:100%",_class="search_init",
                 _title="search Id" )),
        TH(INPUT(_name="search_focal_clade",
                 _style="width:100%",_class="search_init",
                 _title="search focal clade" )),
        TH(INPUT(_name="search_study",
                 _style="width:100%",_class="search_init",
                 _title="search study" )),
        TH(INPUT(_name="search_type",
                 _style="width:100%",_class="search_init",
                 _title="search tree type" )),
        TH(),
        TH(INPUT(_name="search_uploaded",
                 _style="width:100%",_class="search_init",
                 _title="search uploaded" )),
        TH(INPUT(_name="search_person",
                 _style="width:100%",_class="search_init",
                 _title="search person" )))))

    
    return dict(tid=tid, table=table)
    
def dtrecords():
    ## for k, v in sorted(request.vars.items()):
    ##     print k, ":", v

    t = db.stree
    ## t.virtualfields.append(Virtual())
    leaf_count = db.snode.id.count()
    fields = [ t.id, db.study.focal_clade_ott, t.study, t.type,
               t.uploaded, t.contributor, leaf_count ]
    orderby = []
    if request.vars.iSortCol_0:
        for i in range(int(request.vars.iSortingCols or 1)):
            col = int(request.vars.get("iSortCol_%s" % i))
            scol = None
            if col == 0: scol = db.stree.id
            elif col == 1: scol = db.ott_node.name
            elif col == 2: scol = db.study.citation
            elif col == 3: scol = db.stree.type
            elif col == 4: scol = leaf_count
            elif col == 5: scol = db.stree.uploaded
            elif col == 6: scol = db.stree.contributor
            else: pass
            sdir = request.vars.get("sSortDir_%s" % i) or "asc"
            if scol:
                if sdir == "desc": scol = ~scol
                orderby.append(scol)
    start = int(request.vars.iDisplayStart or 0)
    end = start + int(request.vars.iDisplayLength or 10)
    limitby = (start,end)
    q = q0 = ((t.study==db.study.id)&
              ## (db.study.focal_clade_ott==db.ott_node.id)&
              (db.snode.tree==db.stree.id)&
              (db.snode.isleaf==True))
    filters = []
    for i in range(6):
        sterm = request.vars.get("sSearch_%s" % i)
        if sterm and len(sterm)>1:
            ## print 'sterm', i, sterm
            if i == 0: f = db.stree.id
            elif i == 1: f = db.ott_node.name
            elif i == 2: f = db.study.citation
            elif i == 3: f = db.stree.type
            elif i == 4: f = db.stree.uploaded
            elif i == 5: f = db.stree.contributor
            else: pass
            filters.append(f.like('%'+sterm+'%'))

    for x in filters: q &= x
                
    left = [db.snode.on(db.stree.id==db.snode.tree),
            db.study.on(db.stree.study==db.study.id),
            db.ott_node.on(db.study.focal_clade_ott==db.ott_node.id)]
    ## join = []
    rows = db(q).select(*fields, orderby=orderby, limitby=limitby,
                        left=left, groupby=db.stree.id)

    def clade(r):
        t = db.ott_node
        if r.study.focal_clade_ott: return r.study.focal_clade_ott.name
        return ''

    def study_url(r):
        study = r.stree.study
        u = URL(c="study",f="view",args=[study],extension="html")
        citation = s = db.study[study].citation.decode('utf8')
        N = 50
        if len(s)>N: s = s[:N-3]+" ..."
        return A(s, _href=u, _title=citation)

    def tree_url(r):
        i = r.stree.id
        u = URL(c="stree",f="svgView",args=[i],extension="html")
        return A(r.stree.type, _href=u)

    data = [ (r.stree.id,
              clade(r),
              study_url(r).xml(),
              tree_url(r).xml(),
              r[leaf_count],
              r.stree.uploaded,
              r.stree.contributor)
             for r in rows ]
    q = ((t.id>0)&(t.study==db.study.id))
    totalrecs = db(q).count()
    for x in filters: q &= x
    disprecs = db(q).count()
    ## print data
    return dict(aaData=data,
                iTotalRecords=totalrecs,
                iTotalDisplayRecords=disprecs,
                sEcho=int(request.vars.sEcho))

def details():
    return DIV()

def delete_stree(rec):
    snodes = db(db.snode.tree==i).select()
    for n in snodes:
        if n.otu.snode.count()==1:
            del db.otu[int(n.otu)]
        n.delete_record()
    rec.delete_record()

@auth.requires_membership('contributor')
def delete():
    i = int(request.args(0) or 0)
    rec = db.stree(i)
    assert rec
    delete_stree(rec)

def _lookup_taxa(nodes):
    def f(x):
        if not x.label:
            return False
        try:
            float(x.label)
            return False
        except:
            pass
        return True
    t = db.ott_name
    for n in nodes:
        n.ott_node = None
        if not f(n):
            continue
        sq = db(t.name==n.label.replace("_", " "))
        if sq.count()==1:
            n.ott_node = sq.select().first().node

def _study_otus(study):
    q = ((db.otu.study==db.study.id)&(db.study.id==study))
    return db(q).select(db.otu.ALL)

def _insert_stree(study, data):
    """
    given form submission data, insert a source tree
    """
    root = ivy.tree.read(data.newick)
    assert root, data.newick
    ivy.tree.index(root)
    nodes = list(root)
    _lookup_taxa(nodes)
    lab2otu = dict([ (x.label, x) for x in _study_otus(study) ])
    data['study'] = study.id
    stree = db.stree.insert(**data)
    i2n = {}
    for n in nodes:
        label = (n.label or "").replace("_", " ")
        taxid = n.ott_node
        otu = None
        if n.isleaf:
            otu = lab2otu.get(label)
            if otu and otu.ott_node:
                taxid = otu.ott_node
            if not otu:
                otu = db.otu.insert(study=study, label=label, ott_node=taxid)

        i = db.snode.insert(label=n.label, isleaf=n.isleaf, otu=otu,
                            next=n.next, back=n.back, depth=n.depth,
                            length=n.length, tree=stree, ott_node=taxid,
                            pruned=False)
        n.id = i
        i2n[i] = n
    ##     n.rec = Storage(taxon=taxid)

    ## node2anc, node2desc = link.suggest(db, root)
    ## for n, s in node2anc.items():
    ##     if s:
    ##         taxid = sorted(s)[-1][1]
    ##         db.snode[n.id].update_record(taxon=taxid)

    t = db.snode
    if data.clade_labels_represent == "bootstrap values":
        n2sup = {}
        for n in filter(lambda x: x.children and x.label, nodes):
            try: n2sup[n] = float(n.label)
            except ValueError: pass
        if n2sup:
            m = max(n2sup.values())
            if 1 <= m <= 101:
                for n, sup in n2sup.items(): n2sup[n] = sup/100.
            for n, sup in n2sup.items():
                t[n.id].update_record(bootstrap_support=sup, label=None)

    elif data.clade_labels_represent == "posterior support":
        n2sup = {}
        for n in filter(lambda x: x.children and x.label, nodes):
            try: n2sup[n] = float(n.label)
            except ValueError: pass
        for n, sup in n2sup.items():
            t[n.id].update_record(posterior_support=sup, label=None)
                
    for n in nodes:
        if n.parent:
            t[n.id].update_record(parent=n.parent.id)
        n.label = str(n.id)
        n.length = None
    db.stree[stree].update_record(newick_idstr=root.write())
    return stree

#@auth.requires_membership('contributor')
@auth.requires_login()
def create():
    t = db.stree
    study = db.study(request.args(0)) or redirect(URL("index"))
    ## def w(f,v):
    ##     u = URL(c="study",f="view",args=[study.id])
    ##     return A(_study_rep(study), _href=u)
    ## t.study.widget = w
    t.author_contributed.comment = (
        'Was this tree provided by the author (not downloaded from a public '
        'repository or regenerated from the data)?')
    t.type.comment = ('Optional. What kind of tree is it? Examples: '
                      '50% majority-rule bootstrap consensus, Bayesian MCC, '
                      'etc. This field will probably be deprecated in favor '
                      'of tags')
    fields = ["contributor", "newick",
              "author_contributed",
              "type",
              "clade_labels_represent", "clade_labels_comment",
              "branch_lengths_represent", "branch_lengths_comment",
              "comment"]
    form = SQLFORM(db.stree, fields=fields)
    form.vars.study=int(study)

    name = "%s %s" % (auth.user.first_name, auth.user.last_name)
    form.vars.contributor = name
    ## form.vars.newick = "(a,(b,((c,d),(e,f))));"
    ## form.vars.comment = "test test"
    ## base = "/home/rree/Dropbox/phylografter/private/Jansen-2007-PNAS/"
    ## form.vars.newick = file(base+"Jansen_2007.newick").read()
    ## form.vars.comment = "RAxML bootstrap tree; re-analysis of published data"
    ## form.vars.type = "RAxML 7.2.6 bootstrap"
    
    treestr = ""
    if form.accepts(request.vars, session, dbio=False):
        response.flash ="accepted"
        session.contributor = form.vars.contributor
        i = _insert_stree(study, form.vars)
        redirect(URL("svgView", args=[i]))

    return dict(form=form)
    
def edit():
    rec = db.stree(request.args(0))
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "Edit source tree %s" % rec.id
    fields = ["study", "contributor", "newick", "type",
              "clade_labels_represent", "clade_labels_comment",
              "branch_lengths_represent", "branch_lengths_comment",
              "comment"]
    readonly = not auth.has_membership(role="contributor")
    form = SQLFORM(db.stree, int(rec), fields=fields, showid=False,
                   deletable=False, submit_button="Update record",
                   readonly=readonly)
    form.vars.study = rec.study

    if form.accepts(request.vars, session):

        for ( attr, value ) in rec.as_dict().iteritems():

            if( attr not in form.vars ):
                continue

            if( str( form.vars[attr] ) != str( rec[attr] ) ):

                db.userEdit.insert( userName = ' '.join( [ auth.user.first_name, auth.user.last_name ] ),
                                    tableName = 'stree',
                                    rowId = rec.id,
                                    fieldName = attr,
                                    previousValue = str( rec[attr] ),
                                    updatedValue = str( form.vars[attr] ) )
                                    
        
        rec.update_record( last_modified = datetime.datetime.now() )
                                    
        response.flash = "record updated"

    return dict(form=form, rec=rec)

def view():
    return dict()

def sunburst():
    i = int(request.args(0))
    if i:
        rec = db.stree(i)
    return dict(rec=rec)

def d3():
    i = int(request.args(0))
    if i:
        rec = db.stree(i)
    return dict(rec=rec)


def svgView():

    #used for testing
    #del session.TreeViewer

    if( 'TreeViewer' not in session ):
        session.TreeViewer = Storage()

    session.TreeViewer.treeType = 'source'
    session.TreeViewer.strNodeTable = 'snode'

    i = int(request.args(0))
    if i:
        rec = db.stree(i)
    return dict(rec=rec)

def delete_tag():
    rec = db.stree(request.args(0))
    db.stree_tag(request.args(1)).delete_record()
    return dict()

def tag():
    t = db.stree_tag
    rec = db.stree(request.args(0))
    tags = db(t.stree==rec.id).select(orderby=t.tag)
    t.stree.readable = t.stree.writable = False
    t.tag.label = 'Add'
    t.stree.default = rec.id
    t.tag.widget = SQLFORM.widgets.autocomplete(request, t.tag)
    form = SQLFORM(t)
    if form.process().accepted:
        tags = db(t.stree==rec.id).select(orderby=t.tag)
    v = []
    for t in tags:
        u = URL('stree', 'delete_tag.load', args=[rec.id, t.id])
        cid = 'stree-tag-%s' % t.id
        a = A("[X]", _href=u, cid=cid, _title='delete tag')
        v.append(SPAN(t.tag, XML('&nbsp;'), a, _id=cid))
    return dict(tags=v, form=form)

def editOTUs():
    response.title = 'Edit OTUs'
    return dict()

def getNodeInfo():
    i = int(request.vars.nodeId)
    node = db.snode[i]
    color = "black"
    label = node.label or "[%s]" % node.id
    if node.ott_node:
        label = node.ott_node.name
        color = "green"
    return {'nodeId': node.id, 'label': label, 'labelcolor': color}

def v():
    rec = db.stree(request.args(0) or 0)
    study = db.study(rec.study)
    u = URL(c="study",f="view",args=[study.id])
    study = A(_study_rep(study), _href=u, _target="_blank")
    wscale = float(request.vars.wscale or 0.9)
    wider = wscale+0.1; narrower = max(0.1, wscale-0.1)
    wider = A("wider", _href=URL(args=request.args,
                                 vars=dict(wscale="%0.1f" % wider)))
    narrower = A("narrower", _href=URL(args=request.args,
                                       vars=dict(wscale="%0.1f" % narrower)))
    
    treeurl = URL(c='stree',f='treediv',args=request.args,vars=request.vars)
    return dict(treeurl=treeurl, wider=wider, narrower=narrower, study=study)

def load_html():
    i = int(request.args(0) or 0)
    root = build.stree(db, i)
    nodes = list(root.iternodes())
    for node in nodes:
        label = node.rec.label or node.label
        if node.rec.ott_node:
            label = db.ott_node[node.rec.ott_node].name
        node.label = label
    def onclick(nid):
        u = URL(c="snode",f="update_snode.load", args=[nid])
        return ("hbranch_clicked(%s, '%s', 'modal', 'modal_content');"
                % (nid, u))
    if auth.has_membership(role="contributor"): f = onclick
    else: f = ""
    div, mapping, w, h = tree.render_html(root, session, request,
                                          db, onclick=f)
    return dict(tree=div)

def treediv():
    i = int(request.args(0) or 0)
    root = build.stree(db, i)
    nodes = list(root.iternodes())
    for node in nodes:
        label = node.rec.label or node.label
        if node.rec.ott_node:
            label = db.ott_node[node.rec.ott_node].name
        node.label = label
    def onclick(nid):
        u = URL(c="snode",f="update_snode.load", args=[nid])
        return ("hbranch_clicked(%s, '%s', 'modal', 'modal_content');"
                % (nid, u))
    if auth.has_membership(role="contributor"): f = onclick
    else: f = ""
    wscale = float(request.vars.wscale or 0.9)
    div, mapping, w, h = tree.render_html(root, session, request,
                                          db, onclick=f,
                                          wscale=wscale)
    return div.xml()

def html():
    i = int(request.args(0) or 0)
    root = build.stree(db, i)
    nodes = list(root.iternodes())
    for node in nodes:
        label = node.rec.label or node.label
        if node.rec.ott_node:
            label = db.ott_node[node.rec.ott_node].name
        node.label = label

    modal = PluginMModal(id="mymodal", title="Edit node properties", content="")
    mid = modal.id; cid = "c"+mid
    def onclick(nid):
        u = URL(c="snode",f="update_snode.load", args=[nid])
        return "hbranch_clicked(%s, '%s', '%s', '%s');" % (nid, u, mid, cid)
    if auth.has_membership(role="contributor"): f = onclick
    else: f = ""
    div, mapping, w, h = tree.render_html(root, session, request,
                                          db, onclick=f)

    return dict(tree=div, root=root, modal=modal, w=w, h=h)


def modalTreeObj():
    return dict( tree = build.stree( db, request.args[0] ) )


def suggest():
    i = int(request.args(0) or 0)
    root = build.stree(db, i)
    
@auth.requires_membership('contributor')
def import_cached_nexml():
    key = "uploaded_nexml_%s" % auth.user.id
    contributor = "%s %s" % (auth.user.first_name, auth.user.last_name)
    ## nexml = cache.ram(key, lambda:None, time_expire=10000)
    nexml = cache.ram(key, lambda:None, time_expire=10000)
    if not nexml:
        session.flash = "Please upload the Nexml file again"
        redirect(URL('study','tbimport'))
    cache.ram(key, lambda:nexml, time_expire=10000)
    get = lambda x: nexml.meta.get(x) or None
    treebase_id = int(get('tb:identifier.study'))
    study = db(db.study.treebase_id==treebase_id).select().first()
    if not study:
        session.flash = 'Study record needed!'
        redirect(URL('study','tbimport2'))
    d = dict([ (x.attrib.id, x) for x in nexml.trees ])
    t = d.get(request.args(0))
    if not t:
        session.flash = 'Cannot find tree in cache'
        redirect(URL('study','tbimport2'))

    ivy.tree.index(t.root)

    for n in t.root.leaves():
        if not n.otu.otu:
            session.flash = 'Leaf node %s lacks OTU record' % (n.label or n.id)
            redirect(URL('study','tbimport2'))

    ## for leaf in t.root.leaves():
    ##     print leaf.__dict__
    ## for k, v in nexml.otus.items():
    ##     print v

    #print t.root.write()
    ## print t.attrib
    
    sdata = dict(study=study.id,
                 contributor=contributor,
                 newick=t.root.write().replace(" ", "_"),
                 author_contributed=True,
                 tb_tree_id=t.attrib.id,
                 type=t.attrib.label)

    for k,v in sdata.items():
        db.stree[k].default=v

    def w(f,v):
        u = URL(c="study",f="view",args=[study.id])
        return A(_study_rep(study), _href=u)
    db.stree.study.widget = w
    db.stree.uploaded.readable=False
    form = SQLFORM(db.stree)
    if form.accepts(request.vars, session):

        bootstraps = {}
        if form.vars.clade_labels_represent == "bootstrap values":
            for n in t.root.iternodes(lambda x: x.children and x.label):
                try: bootstraps[n] = float(n.label)
                except ValueError: pass
            for n in bootstraps:
                n.label = None

        elif form.vars.branch_lengths_represent == "bootstrap values":
            for n in t.root.iternodes(
                lambda x: x.children and x.length is not None):
                try: bootstraps[n] = float(n.label)
                except ValueError: pass
            for n in bootstraps:
                n.length = None

        if bootstraps:
            m = max(bootstraps.values())
            if 1 <= m <= 101:
                for n, sup in bootstraps.items():
                    bootstraps[n] = sup/100.

        posteriors = {}
        if form.vars.clade_labels_represent == "posterior support":
            for n in t.root.iternodes(lambda x: x.children and x.label):
                try: posteriors[n] = float(n.label)
                except ValueError: pass
            for n in posteriors:
                n.label = None

        elif form.vars.branch_lengths_represent == "posterior support":
            for n in t.root.iternodes(
                lambda x: x.children and x.length is not None):
                posteriors[n] = n.length
            for n in posteriors:
                n.length = None

        for d in filter(None, (bootstraps, posteriors)):
            m = max(d.values())
            if 1 <= m <= 101:
                for n, sup in d.items():
                    d[n] = sup/100.

        i2n = {}
        for n in t.root.iternodes():
            taxid = None
            label = n.otu.otu.label if n.isleaf and n.otu.otu else n.label
            if n.isleaf and n.otu.otu and n.otu.otu.ott_node:
                taxid = n.otu.otu.ott_node
            else:
                taxon = db(db.ott_node.unique_name==label).select().first()
                if taxon: taxid=taxon.id

            i = db.snode.insert(label=label,
                                isleaf=n.isleaf,
                                otu=n.otu.otu.id if n.isleaf and n.otu else None,
                                next=n.next, back=n.back, depth=n.depth,
                                length=n.length,
                                bootstrap_support=bootstraps.get(n),
                                posterior_support=posteriors.get(n),
                                tree=form.vars.id,
                                ott_node=taxid,
                                pruned=False)
            n.id = i
            i2n[i] = n

        for n in t.root.iternodes():
            if n.parent:
                db.snode[n.id].update_record(parent=n.parent.id)
            n.label = str(n.id)
            n.length = None
        db.stree[form.vars.id].update_record(newick_idstr=t.root.write(),
                                             study=study.id)

        session.flash = 'tree %s inserted' % t.attrib.id
        redirect(URL('study','tbimport_trees'))

    return dict(study=study, tree=t, form=form)

def otus_within():
    from collections import defaultdict

    any_all = Field("any_all", "string",
                    requires=IS_IN_SET(['any OTU','all OTUs']),
                    default=request.vars.any_all or 'any OTU',
                    widget=SQLFORM.widgets.options.widget)

    taxon = Field("taxon", "integer", requires=IS_NOT_EMPTY())
    taxon.widget = SQLFORM.widgets.autocomplete(
        request, db.ott_node.unique_name, id_field=db.ott_node.id,
        orderby=db.ott_node.unique_name)
    taxon.default = request.vars.taxon
    f = SQLFORM.factory(any_all, taxon)

    d = defaultdict(list)
    if f.process().accepted:
        t = db.ott_node
        r = t[int(f.vars.taxon)]
        if f.vars.any_all == 'any OTU':
            q = ('select distinct study.id, study.citation, '
                 'stree.id, stree.type '
                 'from stree, study, otu, ott_node '
                 'where stree.study = study.id '
                 'and otu.study = study.id '
                 'and otu.ott_node = ott_node.id '
                 'and ott_node.next >= %d '
                 'and ott_node.back <= %d '
                 'order by stree.id asc'
                 % (r.next, r.back))
        elif f.vars.any_all == 'all OTUs':
            q = ('select distinct stree.study, study.citation, '
                 'stree.id, stree.type '
                 'from stree, study, otu, ott_node '
                 'where stree.study = study.id '
                 'and otu.study = study.id '
                 'and otu.ott_node = ott_node.id '
                 'group by stree.id '
                 'having min(ott_node.next) >= %d '
                 'and max(ott_node.back) <= %d '
                 'order by stree.study, stree.id asc'
                 % (r.next, r.back))
        else:
            pass
        for study, citation, stree, stree_type in db.executesql(q):
            d[(study, citation)].append((stree, stree_type))
        response.flash = '%d studies found' % len(d)
    return dict(form=f, rows=sorted(d.items()))

def taxon_search():
    '''hook for advanced search for trees containing specified taxa, etc.'''
    anyTaxaForm = FORM('Any tree containing any taxa within: ', 
                      INPUT(_name='any_children'), 
                      INPUT(_type='submit'))
    allTaxaForm = FORM('Any tree containing only taxa within: ', 
                   INPUT(_name='all_children'), 
                   INPUT(_type='submit'))
    results = dict()
    if anyTaxaForm.accepts(request,session,formname="any_children"):
        any_parent = anyTaxaForm.vars.any_children
        tree_set = any_taxa_tree_test2(any_parent)
        response.flash = 'Any tree containing taxa with found %d trees containing taxa within %s' % (len(tree_set), any_parent)        
        session.any = True
        session.taxon = any_parent
        results = dict(treeset=tree_set)
        session.results = results
        redirect(URL('taxon_search_results'))
    elif allTaxaForm.accepts(request,session,formname="all_children"):
        all_parent = allTaxaForm.vars.all_children
        tree_set = all_taxa_tree_test(all_parent)
        response.flash = 'Any tree containing only taxa within found %d trees containing only taxa within %s' % (len(tree_set),all_parent)
        session.allParent = all_parent
        results = dict(treeset=tree_set)
        session.taxon = all_parent
        session.any = False
        session.results = results
        redirect(URL('taxon_search_results'))
    elif anyTaxaForm.errors :
        response.flash = 'Any taxa form reports errors'
        results = dict()
    elif allTaxaForm.errors :
        response.flash = 'All taxa form reports errors'
    return dict(anyTaxa=anyTaxaForm,allTaxa=allTaxaForm,results = results)

def taxon_search_results():
    return dict();

def any_taxa_tree_test(taxon):
    taxon_ottol = db.executesql("SELECT next,back FROM ott_node WHERE (name = '%s');" % taxon,as_dict="true")
    if len(taxon_ottol) == 0:
        return set()
    taxon_next = taxon_ottol[0].get('next')
    taxon_back = taxon_ottol[0].get('back')
    studies = db.executesql('SELECT id FROM study')
    good_study_ids = set()
    for study in studies:
        study_id = study[0]
        otulist = db.executesql('SELECT ott_node.next, ott_node.back FROM otu LEFT JOIN ott_node ON (otu.ott_node = ott_node.id) WHERE (otu.study = %d AND ott_node.next > %d AND ott_node.back < %d);' % (study_id,taxon_next,taxon_back))
        if otulist:
            good_study_ids.add(study_id) 
    good_tree_ids = set()
    t1_time = datetime.datetime.now()
    for good_id in good_study_ids:
        tree_list = db.executesql('SELECT id from stree WHERE stree.study = %d;' % good_id) 
        for tree in tree_list:
            tree_id = tree[0]
            tree_nodes = db.executesql('SELECT ott_node.next,ott_node.back FROM snode LEFT JOIN ott_node ON (snode.ott_node = ott_node.id) WHERE (snode.tree = %d AND ott_node.next > %d AND ott_node.back < %d);' % (tree_id,taxon_next,taxon_back))
            if tree_nodes:
                good_tree_ids.add(tree_id)
    return good_tree_ids
    
def all_taxa_tree_test(taxon):
    taxon_ottol = db.executesql("SELECT next,back FROM ott_node WHERE (name = '%s');" % taxon,as_dict="true")
    if len(taxon_ottol) == 0:
        return set()
    taxon_next = taxon_ottol[0].get('next')
    taxon_back = taxon_ottol[0].get('back')
    studies = db.executesql('SELECT id FROM study')
    good_study_ids = set()
    for study in studies:
        study_id = study[0]
        otulist = db.executesql('SELECT ott_node.next, ott_node.back FROM otu LEFT JOIN ott_node ON (otu.ott_node = ott_node.id) WHERE (otu.study = %d AND ott_node.next > %d AND ott_node.back < %d);' % (study_id,taxon_next,taxon_back))
        if otulist:
            good_study_ids.add(study_id) 
    good_tree_ids = set()
    t1_time = datetime.datetime.now()
    good_tree_ids = set()
    for good_id in good_study_ids:
        tree_list = db.executesql('SELECT id from stree WHERE stree.study = %d;' % good_id) 
        for tree in tree_list:
            tree_id = tree[0]
            good_nodes = db.executesql('SELECT COUNT(*) FROM snode LEFT JOIN ott_node ON (snode.ott_node = ott_node.id) WHERE (snode.tree = %d AND (ott_node.next > %d AND ott_node.back < %d));' % (tree_id,taxon_next,taxon_back))
            good_count =good_nodes[0][0]
            if good_count > 0 :
                all_nodes = db.executesql('SELECT COUNT(*) FROM snode WHERE (snode.tree = %d AND snode.ott_node IS NOT NULL);' % tree_id)
                all_count = all_nodes[0][0]
                if all_count == good_count:
                    good_tree_ids.add(tree_id)
    return good_tree_ids


def export_NexSON():
    ''' This exports the tree specified by the argument as JSON NeXML.
        The export will be a complete NeXML document, with appropriate otus block
        and singleton trees block.
    '''
    treeid = request.args(0)
    ## error checking here
    if db.stree(treeid) is None:
        raise HTTP(404)
    else:
        return nexson.nexmlTree(treeid,db)

def modified_list():
    'This reports a json formatted list of ids of modified trees'
    dtimeFormat = '%Y-%m-%dT%H:%M:%S'
    fromString = request.vars['from']
    if fromString is None:
        fromTime = datetime.datetime.now() - datetime.timedelta(1)
    else:
       fromTime = datetime.datetime.strptime(fromString,dtimeFormat)
    toString = request.vars['to']
    if toString is None:
        toTime = datetime.datetime.now()
    else:
        toTime = datetime.datetime.strptime(toString,dtimeFormat)
    #look for trees with uploaded in the interval
    upLoadQuery = (db.stree.uploaded > fromTime) & (db.stree.uploaded <= toTime) 
    trees = set()
    for t in db(upLoadQuery).select():
        trees.add(t.id)
    #as well as trees modified within the interval
    timeQuery = (db.stree.last_modified > fromTime) & (db.stree.last_modified <= toTime)
    for t in db(timeQuery).select():
        trees.add(t.id)
    #a modification to the parent study might involve changes to the otu mappings
    studyQuery = (db.study.last_modified > fromTime) & (db.study.last_modified <= toTime)
    for s in db(studyQuery).select():
        internalTreeQuery = (db.stree.study == s)
        for t in db(internalTreeQuery).select():
            trees.add(t.id)
    treeList = list(trees)
    wrapper = dict(trees = treeList)
    wrapper['from']=fromTime.strftime(dtimeFormat)
    wrapper['to']=toTime.strftime(dtimeFormat)
    return wrapper

def newick():
    """
    return newick string for stree.id = request.args(0)

    optional request.variables are 'lfmt' (leaf format) and 'ifmt'
    (internal node format), which are comma-separated table.field
    values to be pulled out of the node.rec Row objects. These are
    converted to strings, joined by '_', and attached to nodes as
    labels to be written in the newick string.
    """
    treeid = int(request.args(0) or 0)
    assert treeid
    root = build.stree(db, treeid)
    lfmt = [ x.split('.') for x in
             (request.vars['lfmt'] or 'snode.id,otu.label').split(',')
             if x ]
    ifmt = [ x.split('.') for x in
             (request.vars['ifmt'] or '').split(',')
             if x ]
    def proc(node, table, field):
        try: s = str(getattr(getattr(node.rec, table), field))
        except AttributeError: s = ''
        return '_'.join(s.split())
    for n in root:
        n.label = ''
        if n.isleaf: n.label = '_'.join([ proc(n, t, f) for t, f in lfmt ])
        else:
            if ifmt: n.label = '_'.join([ proc(n, t, f) for t, f in ifmt ])
        n.label = n.label.replace('(','--').replace(')','--')
    return dict(newick=root.write())


## Function to delete a tree from a study

def delete():
    t = db.stree
    rec = db.stree(request.args(0))
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "Delete source tree %s" % rec.id
    t.study.readable = t.study.writable = False
    t.contributor.readable = t.contributor.writable = False
    t.newick.readable = t.newick.writable = False
    t.comment.readable = t.comment.writable = False
    t.clade_labels_represent.readable = t.clade_labels_represent.writable = False
    t.clade_labels_comment.readable = t.clade_labels_comment.writable = False
    t.author_contributed.readable = t.author_contributed.writable = False
    t.tb_tree_id.readable = t.tb_tree_id.writable = False
    t.branch_lengths_represent.readable = t.branch_lengths_represent.writable = False
    t.branch_lengths_comment.readable = t.branch_lengths_comment.writable = False
    t.uploaded.readable = t.uploaded.writable = False
    t.type.readable = t.type.writable = False 
    readonly = not auth.has_membership(role="contributor")
    form = SQLFORM(db.stree, int(rec), showid=False,
                   deletable=False, submit_button="Delete Tree",
                   readonly=readonly)
    form.add_button('Cancel', URL('study', 'view', args=rec.study))              
    form.vars.study = rec.study
                              
         
    if form.accepts(request.vars, session):
     
         ## Delete the tree record, the remaining pieces will be removed by MySQL using ON DELETE CASCADE
         del db.stree[rec.id] 
         ## Selects all of the orphaned otus left behind after the snodes are deleted. Needed because there is no way to cascade a one to many from snode to otu
         query = db.executesql('SELECT otu.id FROM otu WHERE study="%s" AND NOT EXISTS (SELECT * FROM snode WHERE  snode.otu = otu.id);' %rec.study)
         ## Deletes all of the orphaned otus left behind after the snodes are deleted.
         ## Above result returns more than a single column. So multi-delete will give an error in MySQL. 
         ## Looped through a single delete call as it should be faster based on the SQL documentation because: 
         ## A) Only one plan will need to be generated
		 ## B) If you are running these from code, then there is less overhead with ODBC calls and network traffic
		 ## C) Any indexes will need to be refreshed just once, not many times.
         for q in query:
         	db.executesql('DELETE FROM otu WHERE id="%id";' %q)
         session.flash = "Tree Record Deleted" ## Inform the user
         redirect(URL('study', 'view', args=rec.study)) ## Return them to study page

    return dict(form=form, rec=rec)
