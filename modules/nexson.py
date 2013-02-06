#!/usr/bin/env python
# coding: utf8
from gluon import *
from gluon.storage import Storage


def nexmlElt(study,db):
    '''Exports the set of trees associated with a study as JSON Nexml
       study - the study to export
       db - database connection
    '''
    otus = otusElt(study,db)
    trees = treesElt(tree,db)
    header = nexmlHeader(tree,db)
    result = dict()
    result["nexml"] = body
    return result

def nexmlTree(study,tree,db):
    otus = singleTreeOtusElt(tree,db)
    trees = singletonTreesElt(tree,db)
    header = singleTreeHeader(tree,db)
    body = dict()
    body.update(otus)
    body.update(trees)
    body.update(header)
    body["id"] = study
    result = dict()
    result["nexml"] = body
    return result

def nexmlHeader():
    result = dict()
    result["@xmlns"] = xmlNameSpace()
    return result
    
def singleTreeHeader(tree,db):
    result = dict()
    result["@xmlns"] = xmlNameSpace()
    result["@version"] = "0.9"
    return result

def xmlNameSpace():
    result = dict()
    result["$"] = "http://www.nexml.org/2009"
    result["nex"] = "http://www.nexml.org/2009"
    result["xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    result["cdao"] = "http://www.evolutionaryontology.org/cdao/1.0/cdao.owl#"
    result["xsd"] = "http://www.w3.org/2001/XMLSchema#"
    return result


def otusElt(study,db):
    body = list([])
    ##get trees
    ##for each tree get the outs
    result = dict()
    result["otus"] = body
    return result
    
def singleTreeOtusElt(tree,db):
    body = list([])
    ##get the otus for this tree
    result = dict()
    result["otus"] = body
    return result
    
def otuElt():
    body = dict()
    result = dict()
    result["otu"] = body
    return result
    
def taxonSetElt():
    body = dict()
    result = dict()
    result["taxonSet"] = body
    return result
    
def treesElt():
    body = dict()
    result = dict()
    result["trees"] = body
    return result
    
def singletonTreesElt(tree,db):
    treeList = list([])
    treeList.append(treeElt(tree,db))
    body=dict()
    body["@otus"] = "Insert_OTUS_label_here"
    body["tree"] = treeList
    result = dict()
    result["trees"] = body
    return result
    
def treeElt(tree,db):
    t = db.stree(tree)
    result = dict()
    result["@id"]=t.id
    result["node"]=treeNodes(tree,db)
    return result
    
def treeNodes(tree,db):
    nodeList = list([])
    nodeList.append(nodeElt())
    return nodeList
    
def nodeElt():
    result = dict()
    result["@id"] = "Insert_NodeID_here"
    return result
    
def edgeElt():
    body = dict()
    result = dict()
    result["edge"] = body
    return result
