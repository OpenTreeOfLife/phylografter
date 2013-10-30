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
    response.subtitle = "Delete source tree %s" % rec.id
    fields = ["study", "contributor", "newick", "type",
              "clade_labels_represent", "clade_labels_comment",
              "branch_lengths_represent", "branch_lengths_comment",
              "comment"]
    path =  os.path.abspath("/static/json/" + "/../../")     
    dirList = os.listdir(path) # get a list of all files in the json directory
    filenamedate = dirList[0][:10]
    tree
    if ##FILE EXISTS:
      json = open('Path/to/file', 'r').read() # read in the entire json as a string

    else:
      json = "No Json Found."

  return dict(rec=rec, json=json)