# coding: utf8
# try something like


def index(): return dict(message="hello from phylesystem.py")


def update():
    # repository_test()  # uncomment soon
    pass

def test():
    repository_test()


# @auth.requires_membership('contributor')
def import_NexSON():
    """
    Imports a Nexson (JSON Nexml) file, updating an existing study record or
    creating a new one as needed
    """
    import datetime
    import cStringIO
    from nexson_parse import ingest_nexson,check_nexson
    if not(request.post_vars):
        raise HTTP(400)  # if no post, then it's a bad request
    # Per Massimo Di Pierro's answer for google groups question about @request.restful
    post_text = request.body.read()
    print datetime.datetime.now()
    try:
        study_exists = check_nexson(cStringIO.StringIO(post_text),db)
    except RuntimeError as e:
        print e
        redirect(URL('study','default'))
    if study_exists: # will contain study id; go delete it and replace
        print "Study exists returns: " + str(study_exists)
        redirect(URL('study','overwrite_from_opentree'))
    study_id = ingest_nexson(cStringIO.StringIO(post_text),db)
    print datetime.datetime.now()
    return study_id

def load_study_from_opentree():
    form = FORM()
    return {'form': form}

def make_opentree_fetch_url(study_id):
    return "".join(("http://",
                   test_server,
                   "/api/v1/study/",
                   str(study_id),
                   ".json?output_nexml2json=0.0.0"))


def make_opentree_study_list_url():
    return "http://api.opentreeoflife.org/phylesystem/v1/study_list"


def repository_test():
    """
    just for testing
    """
    import cProfile
    from nexson_parse import nexson_available, check_nexson, ingest_nexson
    phylesystem_studies = get_available_studies()
    # first delete everything (testing only)
    for study in db().select(db.study.ALL):
        del db.study[study.id]
    # for testing - create a couple of empty studies with conflicting id's
        result = db.study.insert(id=12,
                                 nexson_id='dm_12',
                                 doi='',
                                 citation='xxx',
                                 contributor="AAA")  
        result = db.study.insert(id=13,
                                 nexson_id='dm_13',
                                 doi='',
                                 citation='yyy',
                                 contributor="BBB")  
        result = db.study.insert(id=14,
                                 nexson_id='dm_14',
                                 doi='',
                                 citation='zzz',
                                 contributor="CCCc")  
    
    for study_id in phylesystem_studies:
        fetch_url = make_opentree_fetch_url(study_id)
        print "Processing %s at %s" % (fetch_url, datetime.datetime.now())
        study_exists = nexson_available(fetch_url)
        if not study_exists:
            print "study %s not found" % fetch_url
        else:
            study_id = ingest_nexson(fetch_url, db, None)
            print "time %s, %s" % (datetime.datetime.now(), study_id)

def get_available_studies():
    """
    """
    import requests
    r = requests.get(make_opentree_study_list_url())
    json_list = r.json()
    json_list.sort()
    print json_list
    return json_list


def overwrite_study():
    'Displays a page to ask for validation before deleting a study that is actively being viewed'
    from nexson_parse import check_nexson, ingest_nexson
    overwrite_id = request.args(0)
    opentree_id = request.args(1)
    opentree_url = make_opentree_fetch_url(opentree_id)
    t = db.study
    rec = t(overwrite_id) or redirect(URL("create"))
    readonly = not auth.has_membership(role="contributor")
    ## t.focal_clade.readable = t.focal_clade.writable = False
    t.focal_clade_ott.label = 'Focal clade'
    t.focal_clade_ott.widget = SQLFORM.widgets.autocomplete(
        request, db.ott_name.unique_name, id_field=db.ott_name.node,
        limitby=(0,20), orderby=db.ott_name.unique_name)
    form = SQLFORM(t, rec, deletable=False, readonly=False,
                   fields = ["citation", "year_published", "doi", "label",
                             "focal_clade_ott", "treebase_id",
                             "contributor", "comment", "uploaded"],
                   showid=False, submit_button="Overwrite Study")
    form.add_button('Cancel', URL('study', 'view', args=rec.id))
                       
    
    if form.accepts(request.vars, session):
	# Deletes the study from the database using the DAL. 
        del db.study[rec.id]
        # Alerts the user the study is gone; replacement about to loaded
        session.flash = "The Study will be overwritten"
        study_id = ingest_nexson(opentree_url, db, int(overwrite_id))
        redirect(URL(c="study", f="view", args=[rec.id]))
        session.flash = "The Study Has Been Deleted" #Alerts the user the study has been deleted.	
        redirect(URL('study', 'index'))
    return dict(form=form, rec = rec)
