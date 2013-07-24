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
    '''
    fill in next,back and depth fields in ottol_name - based on ivy indexing for snodes
    '''
    import tempfile
    import subprocess
    dtimeFormat = '%Y-%m-%dT%H:%M:%S'
    start_time = datetime.datetime.now()
    print "Start time: %s" % start_time.strftime(dtimeFormat)
    t = db.ottol_name
    setr = db(t.parent_uid==0)
    root_id = setr.select().first().id
    primary_sql_file = tempfile.NamedTemporaryFile(mode="r+w",delete=False);
    print "primary sql file name = %s" % primary_sql_file.name
    index_aux(root_id,0,primary_sql_file)
    primary_sql_file.close()
    primary_script_file = tempfile.NamedTemporaryFile(mode="r+w",delete=False);
    print "primary script file name = %s" % primary_script_file.name
    primary_script_contents = " ".join(["mysql","--user='tester'","--password='abc123'","phylografter","<" + primary_sql_file.name+"\n"])
    primary_script_file.write(primary_script_contents);
    primary_script_file.close()
    primary_args = ["/bin/sh", primary_script_file.name]
    print "About to launch"
    primary_update = subprocess.Popen(primary_args);
    result = primary_update.wait()
    print "primary script result: %d" % result
    end_time = datetime.datetime.now()
    print "Finished primary update: %s" % end_time.strftime(dtimeFormat)
    syn_sql_file = tempfile.NamedTemporaryFile(mode="r+w",delete=False);
    print "synonym sql file name = %s" % syn_sql_file.name
    index_ottol_synonyms(syn_sql_file)
    syn_sql_file.close()
    syn_script_file = tempfile.NamedTemporaryFile(mode="r+w",delete=False);
    print "synonym script file name = %s" % syn_script_file.name
    syn_script_contents = " ".join(["mysql","--user='tester'","--password='abc123'","phylografter","<" + syn_sql_file.name+"\n"])
    syn_script_file.write(syn_script_contents);
    syn_script_file.close()
    syn_args = ["/bin/sh", syn_script_file.name]
    print "About to launch"
    syn_update = subprocess.Popen(syn_args)
    result = syn_update.wait()
    print "synonym script result: %d" % result
    end_time = datetime.datetime.now()
    print "Finished synonym update: %s" % end_time.strftime(dtimeFormat)
    return db(t.id==root_id).select().first().name
    
def index_aux(node_id,n,tfile):
    rdict = db.executesql('SELECT id,accepted_uid,name FROM ottol_name WHERE (ottol_name.id = %d);' % node_id,as_dict="true")    
    n = n+1
    primary_next = n
    first = rdict[0]
    primary_id = first.get('id')
    cl = db.executesql('SELECT id FROM ottol_name WHERE(parent_uid = %d);' % first.get('accepted_uid'), as_dict="true")
    if cl:
        last_back = n  ##probably unnecessary
        for i,child in enumerate(cl):
            if (i > 0):
                n = last_back
            last_back = index_aux(child.get('id'),n,tfile)
        next_back = last_back + 1
    else:
        next_back=n+1
    primary_back = next_back
    tfile.write("UPDATE ottol_name SET next=%d, back=%d WHERE id = %d;\n" %(primary_next,primary_back,primary_id))
    return next_back
    
def index_ottol_synonyms(tfile):
    synrows = db.executesql('SELECT id,uid,accepted_uid,name from ottol_name WHERE uid != accepted_uid;', as_dict="true")
    counter = 0
    for row in synrows:
        valid_taxa = db.executesql('SELECT id,next,back from ottol_name WHERE uid = %d;' % 
            row.get('id'), as_dict="true")
        if valid_taxa:
            valid_taxon = valid_taxa[0]  #db(t.uid == row.accepted_uid).select().first()
            syn_id = row.get('id')
            #synset.update(next=valid_taxon.next)
            #synset.update(back=valid_taxon.back)
            valid_next = valid_taxon.get('next')
            valid_back = valid_taxon.get('back')
            valid_id = valid_taxon.get('id')
            if (valid_next and valid_back):
                tfile.write("UPDATE ottol_name SET next=%d, back=%d WHERE id = %d;\n" % 
                    (valid_next,valid_back,syn_id))
                #print "saving row %d %s" % (counter, row.get('name'))
            else:
                print "missing update; valid id = %s, synonym id = %s, next = %s, back = %s" % (valid_id, syn_id, valid_next, valid_back)
        else:
            print "no valid taxon found for %d" % row.get('accepted_uid')
        counter = counter + 1
    return
