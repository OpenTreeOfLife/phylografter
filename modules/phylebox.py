#coding: utf8
from gluon import *

LASTUPDATE = None


def load_NexSON_from_OpenTree():
    """
    """
    from nexson_parse import check_nexson, ingest_nexson
    opentree_id = request.args(0) or redirect(URL("create"))
    opentree_url = make_opentree_fetch_url(opentree_id)
    try:
        #does this url refer to a study that matches something already loaded?
        study_match_id = check_nexson(opentree_url,db)
    except RuntimeError as e:
        print "URL was %s" % opentree_url
        print "Error was %s" % str(e)
        session.flash = "URL was %s; Error was %s" % (opentree_url,str(e))
        redirect(URL('study','index'))
    print "match_id was %s" % str(study_match_id)
    if study_match_id:
        redirect(URL(c="study",f="overwrite_study",args=[study_match_id,opentree_id]))
        overwrite_study(opentree_url,study_match_id)
    else:
        study_id = ingest_nexson(opentree_url, db, None)
        redirect(URL(c="study", f="view", args=[study_id]))


test_server = "api.opentreeoflife.org"

def make_opentree_fetch_url(study_id):
    return "".join(("http://",
                   test_server,
                   "/phylesystem/v1/study/",
                   str(study_id),
                   ".json?output_nexml2json=0.0.0"))


def make_opentree_study_list_url():
    return "http://api.opentreeoflife.org/phylesystem/v1/study_list"


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



def get_study():
    """This is called to check if a study is upto date"""

def push_study():
    """Pushes a modified version of a study back to phylesystem on a branch"""

def merge_study():
    """Handles whatever portion of the merge process can be handled by phylografter"""



