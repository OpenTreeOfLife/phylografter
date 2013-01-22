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
        request, db.ottol_name.unique_name, id_field=db.ottol_name.id,
        limitby=(0,20), orderby=db.ottol_name.unique_name)
    t.ottol_name.widget = w

    form = SQLFORM(t, rec, showid=False, _id="updateform",
                   _action=URL(c="snode",f="update_snode.load",args=[rec.id]))
    
    def valid(f):
        ## print 'update snode', request.args(0), rec.label
        ## print ' form.vars.ingroup then', f.vars.ingroup
        ## print ' request.vars.ingroup then', request.vars.ingroup
        ## print ' rec.ingroup then', rec.ingroup
        pass

    if form.process(message_onsuccess='Node updated',
                    onvalidation=valid).accepted:

        for ( attr, value ) in rec.as_dict().iteritems():

            if( attr not in form.vars ):
                continue

            if( str( form.vars[attr] ) != str( rec[attr] ) ):

                if( attr == 'ottol_name' ):

                    updatedValue = db( db.ottol_name.id == form.vars[attr] ).select()[0].name

                    if re.match( "^[0-9]+$", str( rec[ attr ] ) ):

                        previousValue = db( db.ottol_name.id == rec[ attr ] ).select()[0].name

                    else:
                        
                        previousValue = str( rec[attr] )

                else:
                    updatedValue = form.vars[ attr ]
                    previousValue = str( rec[attr] )


                db.userEdit.insert( userName = ' '.join( [ auth.user.first_name, auth.user.last_name ] ),
                                    tableName = 'snode',
                                    rowId = rec.id,
                                    fieldName = attr,
                                    previousValue = previousValue,
                                    updatedValue = updatedValue )
                

        ## print ' form.vars.ingroup now', form.vars.ingroup
        ## print ' request.vars.ingroup now', request.vars.ingroup
        ## print ' rec.ingroup now', rec.ingroup

        name = form.vars.ottol_name
        if name and rec.otu:
            rec.otu.update_record(ottol_name=name)

    return dict(form=form)

def editSnodeTaxon():
    t = db.snode
    rec = t( int(request.args(0)) )
    ## t.taxon.readable = t.taxon.writable = False
    w = SQLFORM.widgets.autocomplete(
        request, db.ottol_name.name, id_field=db.ottol_name.id)
    t.ottol_name.widget = w

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
    if rec.ottol_name:
        label = db.ottol_name[rec.ottol_name].name
    u = URL(c="snode",f="update_snode.load", args=[rec.id])
    onclick = "hbranch_clicked(%s, '%s', 'mymodal', 'cmymodal');" % (rec.id, u)
    e = SPAN(A(label, _onclick=onclick), _style="background-color:yellow")
    return e#.xml()#dict(html=e.xml(), width=len(label))

    
def get_node_html():
    t = db.snode
    rec = t(int(request.args(0) or 0))
    root = build.stree(db, rec.tree)
    node = root[rec.id]
    if node.rec.ottol_name:
        label = db.ottol_name[node.rec.ottol_name].name
    node.label = label
    def onclick(nid):
        u = URL(c="snode",f="update_snode.load", args=[nid])
        return ("hbranch_clicked(%s, '%s', 'mymodal', 'cmymodal');"
                % (nid, u,mid,cid))
    width, height, style = tree.style_nodes(root, wscale=0.9)
    div = tree.render_node_html(node, style, onclick, session)
    return div.xml()
    
