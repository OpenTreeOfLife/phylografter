#!/usr/bin/env python
# coding: utf8

#This module implements the export of nexml in JSON syntax.  The json follows the badgerfish () rules for mapping xml to json

#There are two entry points to this module: nexmlStudy (generate nexml for all the trees and otus for a study) and nexmlTree
#(complete nexml but just including a single tree - but currently all the otus for its containing study)

#local naming convention: getXXX are DAL queries, generally returning an id or list of ids', everything else is generating
#dicts or lists that correspond to BadgerFish (http://badgerfish.ning.com - original site?) mappings of Elements

#Output has been tested using the translator on http://dropbox.ashlock.us/open311/json-xml/ and validating the resulting
#xml with the validator at nexml.org

from gluon.storage import Storage
from gluon import *


def nexmlStudy(studyId,db):
    '''Exports the set of trees associated with a study as JSON Nexml
       study - the study to export
       db - database connection'''
    metaElts = metaEltsForNexml(studyId,db)
    otus = otusEltForStudy(studyId,db)
    trees = treesElt(studyId,db)
    header = nexmlHeader()
    body = dict()
    body.update(otus)
    body.update(trees)
    body.update(header)
    body.update(metaElts)
    body["@id"] = studyId
    return dict(nexml = body)

def nexmlTree(tree,db):
    '''Exports one tree from a study (still a complete JSON NeXML with
    headers, otus, and trees blocks)'''
    studyId = getSingleTreeStudyId(tree,db)
    metaElts = metaEltsForNexml(studyId,db)
    otus = otusEltForTree(tree,studyId,db)
    trees = singletonTreesElt(tree,studyId,db)
    header = nexmlHeader()
    body = dict()
    body.update(otus)
    body.update(trees)
    body.update(header)
    body["id"] = studyId
    return dict(nexml = body)

def nexmlHeader():
    'Header for nexml - includes namespaces and version tag (see nexml.org)'
    result = dict()
    result["@xmlns"] = xmlNameSpace()
    result["@version"] = "0.9"
    result["@nexmljson"] = "http://www.somewhere.org"
    result["@generator"] = "Phylografter nexml-json exporter"
    return result
        
def xmlNameSpace():
    '''namespace definitions for nexml; will be value of xmlns attribute in header (per badgerfish 
    treatment of namespaces)'''
    result = dict()
    result["$"] = "http://www.nexml.org/2009"
    result["nex"] = "http://www.nexml.org/2009"
    result["xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    result["cdao"] = "http://www.evolutionaryontology.org/cdao/1.0/cdao.owl#"
    result["ot"] = "http://opentreeoflife.org"  #need CURIE prefix, URI is placeholder
    result["xsd"] = "http://www.w3.org/2001/XMLSchema#"
    return result

def metaEltsForNexml(studyid,db):
    'generates nexml meta elements that are children of the root nexml element'
    metaArray = []
    yearMeta = pubYearMetaForStudy(studyid,db)
    if (yearMeta):
        metaArray.append(yearMeta)
    doiMeta = doiMetaForStudy(studyid,db)
    if (doiMeta):
        metaArray.append(doiMeta)
    studyPublicationMeta = studyPublicationMetaElt(studyid,db)
    if (studyPublicationMeta):
        metaArray.append(studyPublicationMeta)
    return dict(meta = metaArray)


def pubYearMetaForStudy(studyid,db):
    'generates a date meta element'
    mdate = db.study(studyid).year_published
    if (mdate):
        names = metaNSForDCTerm()
        result = dict()
        result["@xmlns"] = names
        result["@xsi:type"] = "ns:LiteralMeta" 
        result["@property"] = "ter:date"
        result["$"] = mdate
        return result
    else:
        return

#returns a doi metadata element if a proper doi is available, else nothing
def doiMetaForStudy(studyid,db):
    'generates doi metadata element for a study'
    doi = db.study(studyid).doi
    if (doi):
        if (doi.startswith('http://dx.doi.org/')):
            pass  #fine, leave as is
        elif (doi.startswith('http://www.')): #not a doi, but an identifier of some sort
            pass
        elif (doi.startswith('doi:')):    #splice the http prefix on
           doi = 'http://dx.doi.org/' + doi[4:]
        elif not(doi.startswith('10.')):  #not a doi, or corrupted, treat as blank
            return
        else:
           doi = 'http://dx.doi.org/' + doi
        names = metaNSForDCTerm()
        result = dict()
        result["@xmlns"] = names
        result["@xsi:type"] = "ns:ResourceMeta"
        result["@property"] = "ter:identifier"
        result["@href"] = doi
        return result
    else:
        return

def studyPublicationMetaElt(studyid,db):
    'generates text citation metadata element for a study'
    cite = db.study(studyid).citation
    if (cite):
        names = metaNSForDCTerm()
        result = dict()
        result["@xmlns"] = names
        result["@xsi:type"] = "ns:LiteralMeta"
        result["@property"] = "ot:studyPublication"
        result["$"] = cite
        return result
    else:
        return

def metaNSForDCTerm():
    names = dict()
    names["$"] = "http://www.nexml.org/2009"
    names["ns"] = "http://www.nexml.org/2009"
    names["ter"] = "http://purl.org/dc/terms/"
    return names

def otusEltForStudy(studyId,db):
    'Generates an otus block'
    otuList = getOtuIDsForStudy(studyId,db)
    metaElts = metaEltsForOtus(studyId,otuList,db)
    otuElements = [otuElt(otu_id,db) for otu_id in otuList]
    otusElement = dict()
    otusElement["otu"] = otuElements
    otusElement["@id"] = "otus" + str(studyId)
    return dict(otus = otusElement)
    
def getOtuIDsForStudy(studyid,db):
    'returns a list of otu ids for otu records that link to this study'
    otuStudy = db.otu.study
    s=db(otuStudy==studyid)
    result = [row.id for row in s.select()]
    return result
    
def metaEltsForOtus(studyid,otuList,db):
    'generates nexml meta elements that are children of an otus element'
    result = dict()
    return result
    
def getTreeIDsForStudy(studyid,db):
    'returns a list of the trees associated with the specified study'
    treeStudy = db.stree.study
    s=db(treeStudy==studyid)
    rows = s.select()
    result = [row.id for row in rows]
    return result
    
def otusEltForTree(tree,studyId,db):
    ##get the otus for this tree
    nodeList = getSNodeIdsForTree(tree,db)
    otuList = list([])
    for node_id in nodeList:
        nodeOtu = getOtuForNode(node_id,db)
        if (nodeOtu):
            otuList.append(nodeOtu)
    metaElts = metaEltsForOtus(studyId,otuList,db)
    otuElements = [otuElt(otu_id,db) for otu_id in otuList] 
    otusElement = dict()
    otusElement["otu"] = otuElements
    otusElement["@id"] = "otus" + str(studyId) + "." + str(tree)
    result = dict()
    result["otus"] = otusElement
    return result
       
def getOtuForNode(node_id,db):
    return db.snode(node_id).otu    
    
def otuElt(otu_id,db):
    ottol_name_id = db.otu(otu_id).ottol_name
    metaElts = metaEltsForOtuElt(otu_id,ottol_name_id,db)
    result = dict()
    result["@id"] = "otu" + str(otu_id)
    if (ottol_name_id):
        result["@label"]= db.ottol_name(ottol_name_id).name
    return result
    
def metaEltsForOtuElt(otu_id, ottol_name,db):
    return dict()    
    
    
def taxonIdMetaForStudy(ottol_name_id,db):
    'generates doi metadata element for a study'
    cite = db.study(studyid).citation
    if (cite):
        names = metaNSForDCTerm()
        result = dict()
        result["@xmlns"] = names
        result["@xsi:type"] = "ns:LiteralMeta"
        result["@property"] = "ter:bibliographicCitation"
        result["@href"] = cite
        return result
    else:
        return

def metaNSForDWCTerm():
    'returns namespace definitions for Darwin Core (v.s Dublin Core, which is DC)'
    names = dict()
    names["$"] = "http://www.nexml.org/2009"
    names["ns"] = "http://www.nexml.org/2009"
    names["ter"] = "http://rw.tdwg.org/dwc/terms/"
    return names
    
    
def taxonSetElt():
    body = dict()
    result = dict()
    result["taxonSet"] = body
    return result
    
def treesElt(study,db):
    'generate trees element'
    idList = getTreeIDsForStudy(study,db)
    if (len(idList) == 1):
        tree = idList[0]
        treeList = [treeElt(tree,db)]
        body=dict()
        body["@otus"] = "otus" + str(study)
        body["tree"] = treeList
        result = dict()
        result["trees"] = body
    else:
        treeElements = [treeElt(tree_id,db) for tree_id in idList]
        treesElement = dict()
        treesElement["tree"] = treeElements
        treesElement["@otus"] = "otus" + str(study)
        treesElement["@id"] = "trees" + str(study)
        result = dict()
        result["trees"] = treesElement
    return result
    
def metaEltsForTreesElt(study,db):
    return dict()    

def singletonTreesElt(tree,studyId,db):
    'generate the singleton tree element for a tree request'
    treeList = [treeElt(tree,db)]
    body=dict()
    body["@otus"] = "otus" + str(studyId) + "." + str(tree)
    body["tree"] = treeList
    result = dict()
    result["trees"] = body
    return result
    
def getSingleTreeStudyId(tree,db):
    return db.stree(tree).study
    
def treeElt(tree,db):
    t = db.stree(tree)
    result = dict()
    result["@id"]='tree' + str(t.id)
    result["node"]=treeNodes(tree,db)
    result["edge"]=treeEdges(tree,db)
    return result
    
def treeNodes(tree,db):
    nodeList = getSNodeIdsForTree(tree,db)
    body = [nodeElt(node_id,db) for node_id in nodeList]
    return body
    
def treeEdges(tree,db):
    nodeList = getSNodeIdsForTree(tree,db)
    edgeList = list([])
    for node_id in nodeList:
        parent = getNodeParent(node_id,db)
        child = node_id
        length = getEdgeLength(node_id,db)
        if (parent):
            edgeList.append(edgeElt(parent,child,length))
    return edgeList
    
def getNodeParent(childnode,db):
    return db.snode(childnode).parent

def getEdgeLength(childnode,db):
    return db.snode(childnode).length        
    
def edgeElt(parent, child,length):
    result = dict()
    result["@id"]='edge'+str(child)
    result["@source"]='node'+str(parent)
    result["@target"]='node'+str(child)
    if (length):
        result["@length"]=length
    return result

def getSNodeIdsForTree(treeid,db):
    'returns a list of the nodes associated with the specified study'
    nodeSTree = db.snode.tree
    s=db(nodeSTree==treeid)
    return [row.id for row in s.select()]
    
def nodeElt(nodeid,db):
    result = dict()
    otu_id = db.snode(nodeid).otu
    if (otu_id):
        result["@otu"] = 'otu' + str(otu_id)
    result["@id"] = 'node'+str(nodeid)
    return result
