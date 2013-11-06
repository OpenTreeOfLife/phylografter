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

def view():
    
    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "TreeGraph of source tree %s" % rec.id
    working_dir = os.path.dirname(os.path.realpath(__file__))
    working_dir = working_dir[:-11]
    working_dir = str(working_dir)
    working_dir = working_dir + "static/treegraphjson/ncbi/"
    dirlist = os.listdir(working_dir)# get list of files in working_directory
    file_date = dirlist[0][:10]# snip the date stamp from one of those files to know what date to look for
    json_file_name = working_dir + file_date + "_tree_" + treeid + ".JSON" #build filename variable 
    json = open(json_file_name, 'r').read() # read in the entire json as a string


    return dict(rec=rec, json=json)