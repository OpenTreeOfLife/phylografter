# coding: utf-8
## tree = local_import("tree", reload=True)
## build = local_import("build", reload=True)
## link = local_import("link")
import sys
import tree
import build
import link
import ivy
import treeUtil
import nexson
import urllib
import sys
import os

## View a graph of the chosen tree and taxonomy

    
def index():

    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "TreeGraph of source tree %s" % rec.id


    return dict(rec=rec)

def view_ncbi():

    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "NCBI TreeGraph of source tree %s" % rec.id
   
    return dict(rec=rec)    

def view_ott():

    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "OTT TreeGraph of source tree %s" % rec.id
   

    return dict(rec=rec)                   

def graph_ncbi():
    
    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    working_dir = os.path.dirname(os.path.realpath(__file__))
    working_dir = working_dir[:-11]
    working_dir = str(working_dir)
    working_dir = working_dir + "static/taxonomy-stree-json/ncbi/"
    json_file_name = working_dir + "tree_" + treeid + ".JSON" #build filename variable 
    json = open(json_file_name, 'r').read() # read in the entire json as a string


    return json

def graph_ott():
    
    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    working_dir = os.path.dirname(os.path.realpath(__file__))
    working_dir = working_dir[:-11]
    working_dir = str(working_dir)
    working_dir = working_dir + "static/taxonomy-stree-json/ott/"
    json_file_name = working_dir + "tree_" + treeid + ".JSON" #build filename variable 
    json = open(json_file_name, 'r').read() # read in the entire json as a string


    return json