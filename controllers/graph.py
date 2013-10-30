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
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "Graph of taxonomy and source tree %s" % rec.id
    fields = ["study", "contributor", "newick", "type",
              "clade_labels_represent", "clade_labels_comment",
              "branch_lengths_represent", "branch_lengths_comment",
              "comment"]
    path =  os.path.abspath("/static/json/" + "/../../")     
    dirList = os.listdir(path) # get a list of all files in the json directory
    file_name_date = dirList[0][:10]
    file_path = ##
    json_file_name =  file_path + file_name_date + "tree_" + rec 
    
    if any(json_file_name in s for s in dirList): ## Check if target JSON file is present:
      json = open(json_file_name, 'r').read() # read in the entire json as a string

    else:
      json = "No graph found for tree " + rec

  return dict(rec=rec, json=json)