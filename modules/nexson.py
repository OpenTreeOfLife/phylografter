#!/usr/bin/env python
# coding: utf8
from gluon import *
from gluon.storage import Storage


def nexmlStudy(study,db):
    '''Exports the set of trees associated with a study as JSON Nexml
       study - the study to export
       db - database connection'''
    otus = otusElt(study,db)
    trees = treesElt(study,db)
    header = nexmlHeader()
    body = dict()
    body.update(otus)
    body.update(trees)
    body.update(header)
    body["id"] = study
    result = dict()
    result["nexml"] = body
    return result

def nexmlTree(tree,db):
    '''Exports one tree from a study (still a complete JSON NeXML with
    headers, otus, and trees blocks'''
    study = singleTreeStudyId(tree,db)
    otus = singleTreeOtusElt(tree,db)
    trees = singletonTreesElt(tree,db)
    header = singleTreeHeader()
    body = dict()
    body.update(otus)
    body.update(trees)
    body.update(header)
    body["id"] = study
    result = dict()
    result["nexml"] = body
    return result

def nexmlHeader():
    'Header for nexml - includes namespaces and version tag (see nexml.org)'
    result = dict()
    result["@xmlns"] = xmlNameSpace()
    result["@version"] = "0.9"
    result["@nexmljson"] = "http://www.somewhere.org"
    return result
    
def singleTreeHeader():
    'Header for singleton tree export - probably not different from header for study export'
    return nexmlHeader()
    
def xmlNameSpace():
    '''namespace definitions for nexml; will be value of xmlns attribute in header (per badgerfish 
    treatment of namespaces)'''
    result = dict()
    result["$"] = "http://www.nexml.org/2009"
    result["nex"] = "http://www.nexml.org/2009"
    result["xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    result["cdao"] = "http://www.evolutionaryontology.org/cdao/1.0/cdao.owl#"
    result["xsd"] = "http://www.w3.org/2001/XMLSchema#"
    return result


def otusElt(study,db):
    'Generates an otus block'
    #will studies have more than one set of otus?
    body = list([])
    ##get trees
    trees = getTreeIDsForStudy(study,db)
    ##for each tree get the otus
    result = dict()
    result["otus"] = body
    return result
    
def getTreeIDsForStudy(studyid,db):
    'returns a list of the trees associated with the specified study'
    treeStudy = db.stree.study
    s=db(treeStudy==studyid)
    rows = s.select()
    result = list([])
    for row in rows:
        result.append(row.id)
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
    
def treesElt(study,db):
    idList = getTreeIDsForStudy(study,db)
    if (len(idList) == 1):
        return singletonTreesElt(idList[0],db)
    body = list([])
    for tree_id in idList:
        body.append(treeElt(tree_id,db))
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
    nodeList = getSNodeIdsForTree(tree,db)
    body = list([])
    for node_id in nodeList:
        body.append(nodeElt(node_id,db))    
    return nodeList
    
def getSNodeIdsForTree(treeid,db):
    'returns a list of the nodes associated with the specified study'
    nodeSTree = db.snode.tree
    s=db(nodeSTree==treeid)
    rows = s.select()
    result = list([])
    for row in rows:
        result.append(row.id)
    return result
    
def nodeElt(nodeid,db):
    result = dict()
    result["@id"] = nodeid
    return result
    
def edgeElt():
    body = dict()
    result = dict()
    result["edge"] = body
    return result
