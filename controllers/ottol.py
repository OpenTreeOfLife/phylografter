def nodexml(rec, load=False):
    t = db.ottol_node
    expanded = session.ottol_browse_expanded or set([1])
    print "nodexml start:", rec.name
    import nodetable
    nc = rec.back-rec.next
    ## rank = rec.rank
    url = URL("record", args=[rec.id], extension="html")
    edit = A("[edit]", _href=url, _title="Edit name data (author, etc.)")

    ## newrec = DIV(A('Add name here',
    ##                _href=URL('insert.load', args=[rec.id]),
    ##                cid='newrec%s'%rec.id, _id="addlink%s"%rec.id),
    ##              DIV(_id='newrec%s'%rec.id))

    if nc > 1: # not a leaf node
        print 'start'
        children = nodetable.children(t, rec)
        print 'end'
        q = (t.next>rec.next)&(t.back<rec.back)&(t.next==t.back-1)
        ntips = db(q).count()
        url = URL('browse', args=[rec.id], extension="html")
        sp = SPAN(rec.name, _style='font-style:italic',
                  _title="Browse this name")
        name = A(sp, " (%s/%s)" % (len(children), ntips), _href=url)
        url = URL("children.load", args = [rec.id])
        ## expandlink = A("(%s/%s)" % (len(children), ntips),
        ##                _href = url, cid = "children%s" % rec.id)
        expandlink = A("[+/-]",_href = url, cid = "children%s" % rec.id,
                       _title="expand/collapse")
        if rec.id in expanded:
            cv = [ LI(nodexml(c, False)) for c in children ]
            ## cv.append(LI(newrec))
            child_div = DIV(UL(*cv), _id="children%s" % rec.id)
        else:
            child_div = DIV(_id="children%s" % rec.id)
        if load is False:
            ## name = SPAN(rank, " ", name)
            name = SPAN(name)
            if rec.id in session.ottol_search_matches:
                name["_style"] = "background-color:orange"
            e = DIV(name, " ", expandlink, " ", edit, child_div)
        else:
            e = child_div
    else:
        ## name = SPAN(rank, " ", SPAN(rec.name, _style='font-style:italic'),
        name = SPAN(SPAN(rec.name, _style='font-style:italic'),
                    " ", edit)
        if rec.id in session.ottol_search_matches:
            name["_style"] = "background-color:orange"
        e = DIV(name)
    print "nodexml end:", rec.name
    return e

## this appears to be depreciated due to its use of ottol_node (PEM 6-20-2013)
def browse():
    if not request.args and not request.vars:
        session.ottol_browse_expanded = set([1])
        
    import nodetable
    session.ottol_search_matches = session.ottol_search_matches or set()
    s = session.ottol_browse_expanded or set([1])
    #print "browse: s:", s
    t = db.ottol_node
    root = t(int(request.args(0) or 1))
    path = []
    if root.next > 1:
        for rec in reversed(nodetable.rootpath(t, root)):
            url = URL('browse', args=[rec.id], extension="html")
            if path: path.append(SPAN(" :: "))
            path.append(A(rec.name, _href=url, _style='font-style:italic'))
    path = DIV(path)
    w = SQLFORM.widgets.autocomplete(request, db.ottol_node.name,
                                     min_length=2)
    st = request.vars.search or ""
    f = Field('search', widget=w, default=st)
    form = SQLFORM.factory(f, submit_button='Search')
    matches = set()
    if st:
        rows = db(t.name.like('%'+st+'%')).select()
        if rows: s = set([1])
        response.flash = '%s matches' % (len(rows) or "No")
        for r in rows:
            s.add(r.id)
            matches.add(r.id)
            if r.next > 1:
                for anc in nodetable.rootpath(t, r):
                    s.add(anc.id)
    session.ottol_search_matches = matches
    session.ottol_browse_expanded = s
    return dict(e=nodexml(root), path=path, form=form)

## this appears to be depreciated due to its use of ottol_node (PEM 6-20-2013)
def children():
    s = session.ottol_browse_expanded or set([1])
    ## import nodetable
    t = db.ottol_node
    root = t(int(request.args(0) or 1))
    if (root.id not in s) or (request.args(1)) or request.vars.expand:
        s.add(root.id)
        ## children = nodetable.children(t, root)
        e = nodexml(root, True)
    else:
        s.remove(root.id)
        ## children = ""
        e = ""
    session.ottol_browse_expanded = s
    ## return dict(children=children)
    return dict(e=e)

# provide (unsecured) autocomplete service for ottol names, used by the opentree app
# NOTE that we're using JSONP to overcome the same-domain origin policy
def autocomplete():
    searchText = request.vars['search']
    jsonCallback = request.vars['callback']
    if searchText is None:
        return "<p><i>No matching results</i></p>"
    t = db.ottol_name
    # for now, let's just match on the start
    q = (t.unique_name.like(searchText +"%"))
    ### TODO: also match on ottol ID?  q |= (t.id.like("%"+ searchText +"%")
    fields = (t.accepted_uid, t.unique_name)
    rows = db(q).select(*fields, limitby=(0,4))
    return "%s( %s )" % (jsonCallback, ['<a href="%s">%s</a>' % (r.accepted_uid, r.unique_name) for r in rows])

def index_ottol_names():
    '''fill in next,back and depth fields in ottol_name - based on ivy indexing for snodes'''
    t = db.ottol_name
    print "**"
    setr = db(t.parent_uid==0)
    root_id = setr.select().first().id
    index_aux(root_id,1);
    return db(t.id==root_id).select().first().name
    
def index_aux(node_id,n):
    t = db.ottol_name
    setr = db(t.id==node_id)
    setr.update(next=n)
    row = setr.select().first()
    print "row: %d, next: %d" % (node_id, row.next)
#    if (row.parent_uid==0):
#        setr.update(depth=0)
#    else:
#        parents = db(t.accepted_uid == row.parent_uid).select()
#        realParent = None
#        for parent in parents:
#           if (parent.uid == parent.accepted_uid):  # synonym uids won't match
#               realParent=parent
#        if (realParent == None):
#            print "No parent found for Node: %s (%d), parent uid: %s" % (row.name, row.id, row.parent_uid)
#        else:
#            print "Node: %s (%d), parent uid: %s" % (row.name, row.id, realParent.accepted_uid)
        #setr.update(depth=realParent.depth+1)
        #row = setr.select().first()  # update
        #print "row: %d,parent depth: %s, depth: %s" % (node_id, realParent.depth, row.depth)
    n += 1
    childList = db(t.parent_uid == row.accepted_uid).select()
    for i,child in enumerate(childList):
        if (i > 0):
            n = (db(t.id == childList[i-1].id).select().first().back)+1
            pass
        index_aux(child.id,n)
    if len(childList)>0:
        b = (db(t.id == childList[-1].id).select().first().back)+1
        setr.update(back=b)  #node.back = node.children[-1].back + 1
    else:
        setr.update(back=n)
    return row.back
