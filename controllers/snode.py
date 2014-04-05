tree = local_import("tree", reload=True)
build = local_import("build", reload=True)
util = local_import( "plugin_treeViewer", reload = True )
from pprint import pprint
import re

def index():
    return dict()

def update_snode():
    t = db.snode
    t.otu.readable = t.otu.writable = False
    rec = t(int(request.args(0) or 0))
    ## t.taxon.readable = t.taxon.writable = False

    w = SQLFORM.widgets.autocomplete(
        request, db.ott_node.unique_name, id_field=db.ott_node.id,
        limitby=(0,20), orderby=db.ott_node.unique_name)
    t.ott_node.widget = w

    form = SQLFORM(t, rec, showid=False, #_id="updateform",
                   _action=URL(c="snode",f="update_snode.load",args=[rec.id]))

    ## This form never gets submitted properly (web2py style) because
    ## of voodoo in static/modalBox.js. Instead when it gets submitted
    ## its vars are serialzed into request.vars. So we need to check
    ## for request.vars and handle them specially.

    # hack to check that form was submitted
    if request.vars.id and int(request.vars.id)==rec.id:
        fields = (('label', lambda s: s or None),
                  ('age', lambda s: float(s) if s else None),
                  ('age_min', lambda s: float(s) if s else None),
                  ('age_max', lambda s: float(s) if s else None),
                  ('length', lambda s: float(s) if s else None),
                  ('bootstrap_support', lambda s: float(s) if s else None),
                  ('posterior_support', lambda s: float(s) if s else None),
                  ('other_support', lambda s: float(s) if s else None),
                  ('other_support_type', lambda s: s or None),
                  ('ingroup', lambda s: True if s=='on' else False),
                  ('ott_node', lambda s: int(s) if s else None))
        data = {}
        for field, func in fields:
            v = func(request.vars[field])
            ## print field, rec[field], v
            if str(rec[field]) != str(v): data[field] = v
        
        if data:
            if data.get('ingroup'):
                db(db.snode.tree==rec.tree).update(ingroup=False)

            userName=' '.join([auth.user.first_name, auth.user.last_name])
            for k,v in data.items():
                db.userEdit.insert(userName=userName,
                                   tableName='snode',
                                   rowId=rec.id,
                                   fieldName=k,
                                   previousValue=str(rec[k]),
                                   updatedValue=str(v))

            rec.update_record(**data)
            session.flash = 'Node updated'
            if 'ott_node' in data and rec.otu:
                rec.otu.update_record(ott_node=data['ott_node'])
            mytree = db.stree(rec.tree)
            mytree.update_record(last_modified=datetime.datetime.now())

    return dict(form=form)

def editSnodeTaxon():
    t = db.snode
    rec = t( int(request.args(0)) )
    w = SQLFORM.widgets.autocomplete(
        request, db.ott_name.unique_name, id_field=db.ott_name.node,
        limitby=(0,20), orderby=db.ott_name.unique_name)
    t.ott_node.widget = w

    d = dict([ (k, v) for k, v in request.vars.items()
               if k in t.fields ])
    if d:
        rec.update_record(**d)

    form = SQLFORM(t, rec, fields=["label","taxon"], showid=False,
                   _id="updateForm",
                   _action=URL(c="snode",f="editSnodeTaxon.load",
                               args=[rec.id]))

    return dict(form=form)


def get_label_html():
    t = db.snode
    rec = t(int(request.args(0) or 0))
    label = rec.label
    if rec.ott_node:
        label = db.ott_node[rec.ott_node].name
    u = URL(c="snode",f="update_snode.load", args=[rec.id])
    onclick = "hbranch_clicked(%s, '%s', 'mymodal', 'cmymodal');" % (rec.id, u)
    e = SPAN(A(label, _onclick=onclick), _style="background-color:yellow")
    return e#.xml()#dict(html=e.xml(), width=len(label))

    
def get_node_html():
    t = db.snode
    rec = t(int(request.args(0) or 0))
    root = build.stree(db, rec.tree)
    node = root[rec.id]
    if node.rec.ott_node:
        label = db.ott_node[node.rec.ott_node].name
    node.label = label
    def onclick(nid):
        u = URL(c="snode",f="update_snode.load", args=[nid])
        return ("hbranch_clicked(%s, '%s', 'mymodal', 'cmymodal');"
                % (nid, u,mid,cid))
    width, height, style = tree.style_nodes(root, wscale=0.9)
    div = tree.render_node_html(node, style, onclick, session)
    return div.xml()
