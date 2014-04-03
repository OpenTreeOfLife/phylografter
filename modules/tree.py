"""
module for rendering trees as html DIVs.
"""
import layout
from gluon.html import *
from gluon.html import URL
from gluon.validators import *
import datetime
from ivy_local.storage import Storage
from collections import defaultdict

is_year = IS_INT_IN_RANGE(1800, datetime.date.today().year+2)

def stree_abbrev(stree):
    '''
    Creates an abbreviated version of the source tree title.
    '''
    s = []
    if stree.tree_title:
        s.append(stree.tree_title)
    c = (stree.citation or "").replace(".", " ").replace(",", " ")
    c = c.replace("(", " ").replace(")", " ").split()
    srauth = (c or [""]).pop(0)
    for x in c:
        if not is_year(x)[1]:
            srauth = "%s, %s" % (srauth, x)
            break
    s.append(srauth)
    if stree.tree_label:
        s.append("".join(stree.tree_label.split()))
    s = ": ".join(s)
    return s
       
def collapse_snode_by_substr(root, substr, session):
    '''
    Collapse a node if the label contains the given substring
    '''
    for node in root.iternodes():
        if node.label and (substr in node.label) and node.parent \
                      and node.id not in session.snode_keep_visible:
            session.snode_collapsed[node.id] = 1

def getleaves(n, collapsed=None):
    collapsed = collapsed or set()
    return [ x for x in n.leaves() if x not in collapsed ]

def leaf_distances(n, collapsed):
    leaves = getleaves(n, collapsed)
    l2d = dict([ (lf, sum([ 1 for x in lf.rootpath() ])-1)
                 for lf in leaves ])
    return l2d

## def streerec2str(rec):
##     '''
##     Creates a string representation of a source tree record.
##     '''
##     s = []
##     if rec.tree_title:
##        s.append(rec.tree_title+":")
##     if rec.tree_type:
##        s.append(rec.tree_type)
##     if rec.tree_label:
##        s.append("(%s)" % rec.tree_label)
##     if rec.tree_title or rec.tree_type or rec.tree_label:
##        s.append("in")
##     s.append(rec.citation)
##     if rec.comment:
##        s.append("(%s)" % " ".join(rec.comment.split()))
##     s = " ".join(s)
##     return s

def newick2css(s, session, request):
    '''
    Converts a newick string to a tree and correspoding html for display.
    '''
    root = ivy.tree.read(s)
    for i, n in enumerate(root.iternodes()):
	n.id = i
    return render_html(root, session, request, interactive=False, wscale=1.0)

def style2str(style):
    s = []
    for k, v in style.items():
        if k in ("top", "height"):
            v = "%sex" % v
        elif k in ("width", "left"):
            v = "%sem" % v
        s.append("%s:%s;" % (k,v))
    return "".join(s)

def style_nodes(root, collapsed=None, selected_node_id=None, wscale=1.0):
    style = defaultdict(Storage)
    collapsed = collapsed or set()
    bgcolor = "gray"
    selcolor = "red"
    leaves = getleaves(root, collapsed=collapsed)
    l2d = leaf_distances(root, collapsed=collapsed)
    height = len(leaves)*2.5
    unit = 3.0
    width = max([ l2d[lf] for lf in leaves ]) * unit * wscale
    width = min(width, 65)
    rpad = max([ len(lf.label or "") for lf in leaves ]) * 0.7
    lpad = max(1, len(root.label or []) * 0.7)
    width += rpad+2 + lpad
    branchwidth = 0.75
    n2c = layout.calc_node_positions(
        root, width, height,
        lpad=lpad+1, tpad=1, bpad=2.5, rpad=rpad+1,
        collapsed=collapsed,
        scaled=False
        )
    n2c[root].px = 1
    for node in root.iternodes(f=lambda x:x.rec.id not in collapsed):
        coords = n2c[node]
        style[node].x = coords.x
        style[node].y = coords.y
        w = coords.x-coords.px
        pos = "absolute"
        style[node].hbranch = Storage()
        hbranch = style[node].hbranch
        hbranch["position"] = pos
        hbranch["width"] = w
        hbranch["height"] = branchwidth
        hbranch["top"] = coords.y+0.5
        hbranch["left"] = coords.px
        hbranch["background-color"] = bgcolor
        if float(node.rec.bootstrap_support or 0) > 0.70:
            hbranch["background-color"] = "green"

        if coords.py is None:
            coords.py = coords.y
        if coords.py < coords.y:
            h = coords.y-coords.py
            y = coords.py
        else:
            h = coords.py-coords.y
            y = coords.y
        style[node].vbranch = Storage()
        vbranch = style[node].vbranch
        vbranch["position"] = pos
        vbranch["width"] = 0.5 * branchwidth
        vbranch["height"] = h
        vbranch["top"] = y+0.5
        vbranch["left"] = coords.px
        vbranch["background-color"] = bgcolor

        style[node].label = Storage()
        label = style[node].label
        label["position"] = pos
        if node.isleaf or node.rec.id in collapsed:
            label["top"] = coords.y-0.75
            label["left"] = coords.x+0.25
            if node.rec.otu and node.rec.otu.taxon:
                s = node.rec.otu.taxon.name
                label["width"] = len(s)
            else:
                label["width"] = len(node.label or "")
            label["text-align"] = "left"
        else:
            label["text-align"] = "right"
            label["width"] = len(node.label or "")
            label["top"] = coords.y-0.75
            label["left"] = coords.x-len(str(node.label or ""))

        style[node].ref = Storage()
        ref = style[node].ref
        ref["position"] = pos
        ref["top"] = coords.y-0.5
        ref["left"] = coords.x+0.25
        
    if selected_node_id:
        for n in root.iternodes(f=lambda x:x.rec.id not in collapsed):
            if n.rec.id == selected_node_id:
                for m in n.iternodes():
                    style[m].vbranch["background-color"] = selcolor
                    style[m].hbranch["background-color"] = selcolor
                break
                
    return width, height, style

def render_node_label(node, isleaf, onclick=None):
    if not onclick: onclick = lambda x:""
    node_id = node.rec.id
    if isleaf and node.rec.otu.taxon:
        label = node.rec.otu.taxon.name
    else:
        label = node.label or ""
    style = Storage()
    if isleaf:
        anchor = A(label, _onclick=onclick(node_id))
        d = SPAN(anchor, _style="cursor:pointer;")
    else:
        anchor = A(label, _onclick=onclick(node_id))
        d = SPAN(anchor, _style="background-color:yellow;cursor:pointer;")
    return d

def render_node_html(node, isleaf, style, onclick, render_label):
    node_id = node.rec.id
    D = DIV(_id="snode-%s" % node_id)
    divid = "hbranch%s" % node_id
    anchor = A(str(node_id),
               _style="display:block;text-indent:-9999px;cursor:pointer;",
               _onclick=onclick(node_id))
    d = DIV(anchor, _style=style2str(style.hbranch), _id=divid,
            _class="hbranch", _title="node_id = %s" % node_id)
    D.append(d)

    divid = "vbranch%s" % node_id
    d = DIV(_style=style2str(style.vbranch), _id=divid,
            _title="node_id = %s" % node_id)
    D.append(d)

    if isleaf:
        divid = "label%s" % node_id
        d = DIV(render_label(node, isleaf, onclick),
                _style=style2str(style.label), _class="leafnode",
                _id=divid)
        D.append(d)
    else:
        divid = "label%s" % node_id
        d = DIV(render_label(node, isleaf, onclick),
                _style=style2str(style.label), _class="internalnode",
                _id=divid)
        D.append(d)
    return D

def render_html(root, session, request, db, onclick=None, wscale=0.9,
                render_label=None):
    """
    Creates the html for the tree for viewing.
    """
    render_label = render_label or render_node_label
    collapsed = session.snode_collapsed or []
    width, height, style = style_nodes(
        root, collapsed=collapsed,
        wscale=wscale, selected_node_id=session.selected_snode_id
        )
    divs = []
    if not session.snode_collapsed:
        session.snode_collapsed = set()

    html = defaultdict(Storage)

    if not onclick:
        onclick = lambda x:"false;"

    for node in root.iternodes(f=lambda x:x not in collapsed):
        node_id = node.rec.id
        st = style[node]
        divs.append(render_node_html(node, node.isleaf, st,
                                     onclick, render_label))
            
    divid = "stree-%s" % root.rec.tree
    d = DIV(_style="position:relative;width:%sem;height:%sex;" % (width,height), _id=divid, *divs)
    return d, html, width, height

def render_html_test(root, session, request, db, interactive=True, wscale=1.0):
    '''
    Creates the html for the tree for viewing.
    '''
    collapsed = session.snode_collapsed or set()
    width, height = style_nodes(root, collapsed=collapsed, wscale=wscale,
                                selected_node_id=session.selected_snode_id)
    divs = []
    if not session.snode_collapsed:
        session.snode_collapsed = set()
        
    for node in root.iternodes(f=lambda x:x not in session.snode_collapsed):
        node_id = node.rec.id
        label = node.rec.label or ""
        onclick = ""
        divs.append(DIV(
            _style="position:absolute;"\
            "width:%(width)sem; height:%(height)sex; "\
            "background-color:%(background-color)s; "\
            "top:%(top)sex; left:%(left)sem" % node.hbranch_style,
            _onclick=onclick, _id="hbranch%s" % node_id,
            _title="node_id = %s" % node_id
            ))
        divs.append(DIV(
            _style="position:absolute; height:%(height)sex; "\
            "width:%(width)sem; background-color:%(background-color)s; "\
            "top:%(top)sex; left:%(left)sem" % node.vbranch_style,
            _onclick=onclick, _id="vbranch%s" % node_id,
            _title="node_id = %s" % node_id
            ))

        if len(node.children) == 1 and node.parent:
            style = node.hbranch_style.copy()
            style["left"] = style["left"]+style["width"]-0.5
            style["width"] = 0.75
            style["top"] -= style["height"]*0.5
            style["height"] *= 1.75
            d = DIV(
                _style="position:absolute; "\
                "width:%(width)sem; height:%(height)sex; "\
                "background-color:%(background-color)s; "\
                "top:%(top)sex; left:%(left)sem" % style,
                _onclick=onclick, _id="singlechild%s" % node_id
                )
            divs.append(d)

        if node.rec.isleaf or node_id in (session.snode_collapsed or []):
            divid = "label%s" % node_id
            if node.rec.taxon:
                s = db.taxon[node.rec.taxon].name
                if node.rec.taxon.ncbi_taxon:
                    s = s+" [%s]" % node.rec.taxon.ncbi_taxon.taxid

            else: s = node.rec.label or "None assigned"
            avars = dict(target=divid,edit=1)
            u = URL(r=request, c="taxon", f="snode_widget",
                    args=[node_id], vars=avars)
            a = A(s, _href=u, cid=divid)
            divs.append(
                DIV(a, _style="position:absolute; top:%(top)sex; "\
                    "left:%(left)sem" % node.label_style,
                    _id="label%s" % node_id)
                )
        else:
            divid = "label%s" % node_id
            if node.rec.taxon:
                s = db.taxon[node.rec.taxon].name
                if node.rec.taxon.ncbi_taxon:
                    s = s+" [%s]" % node.rec.taxon.ncbi_taxon.taxid
            else: s = "None assigned"
            avars = dict(target=divid,edit=1)
            u = URL(r=request, c="taxon", f="snode_widget",
                    args=[node_id], vars=avars)
            a = A(s, _href=u, cid=divid)
            divs.append(
                DIV(SPAN(a, _style="background-color:yellow"),
                    _style="position:absolute; width:%(width)sem; "\
                    "text-align:%(text-align)s; top:%(top)sex; "\
                    "left:%(left)sem" % node.label_style,
                    _id=divid)
                )
    d = DIV(_style="width:%sem; height:%sex;"\
            % (width, height),
            *divs)
    return d
