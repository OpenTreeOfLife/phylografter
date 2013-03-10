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

# Note - the nexml root element can have meta elements as direct children; unlike everywhere else, there are no id or about
# attributes as seem to be required for other element types (e.g., otu, node) when they have meta children
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
    result["ot"] = "http://purl.org/opentree-terms#"
    result["xsd"] = "http://www.w3.org/2001/XMLSchema#"
    return result

def metaEltsForNexml(studyid,db):
    'generates nexml meta elements that are children of the root nexml element'
    metaArray = []
    curatorMeta = curatorMetaForStudy(studyid,db)
    if (curatorMeta):
        metaArray.append(curatorMeta)
    treeBaseDepositMeta = treeBaseDepositMetaForStudy(studyid,db)
    if (treeBaseDepositMeta):
        metaArray.append(treeBaseDepositMeta)
    doiMeta = doiMetaForStudy(studyid,db)
    if (doiMeta):
        metaArray.append(doiMeta)
    studyPublicationMeta = studyPublicationMetaElt(studyid,db)
    if (studyPublicationMeta):
        metaArray.append(studyPublicationMeta)
    return dict(meta = metaArray)

def curatorMetaForStudy(studyid,db):
    'generates curator metadata element for a study'
    curator = db.study(studyid).contributor
    if (curator):
        #names = metaNSForDCTerm()
        result = dict()
        result["@xsi:type"] = "nex:LiteralMeta"
        result["@property"] = "ot:curatorName"
        result["$"] = curator
        return result
    else:
        return

def treeBaseDepositMetaForStudy(studyid,db):
    'generates text citation metadata element for a study'
    treebaseId = db.study(studyid).treebase_id
    if (treebaseId):
        #names = metaNSForDCTerm()
        result = dict()
        result["@xsi:type"] = "nex:LiteralMeta"
        result["@property"] = "ot:dataDeposit"
        result["$"] = treebaseId
        return result
    else:
        return


#returns an ot:studyPublication metadata element if a (possibly incomplete) doi or a 
#suitable URI is available, else nothing
def doiMetaForStudy(studyid,db):
    'generates ot:studyPublication metadata element for a study'
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
        result = dict()
        result["@xsi:type"] = "nex:ResourceMeta"
        result["@property"] = "ot:studyPublication"
        result["@href"] = doi
        return result
    else:
        return

def studyPublicationMetaElt(studyid,db):
    'generates text citation metadata element for a study'
    cite = db.study(studyid).citation
    if (cite):
        result = dict()
        result["@xsi:type"] = "nex:LiteralMeta"
        result["@property"] = "ot:studyPublicationReference"
        result["$"] = cite
        return result
    else:
        return


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

#Generates an otu Element             
def otuElt(otu_id,db):
    ottol_name_id = db.otu(otu_id).ottol_name
    metaElts = metaEltsForOtuElt(otu_id,ottol_name_id,db)
    result = dict()
    result["@id"] = "otu" + str(otu_id)
    if (ottol_name_id):
        result["@label"]= db.ottol_name(ottol_name_id).name
    else:
        result["@label"]= db.otu(otu_id).label
    if metaElts:
        result["@about"] = "#otu" + str(otu_id)
        result.update(metaElts)
    return result
    
#Name suggests more than one meta element; expect more than current ot:ottolid
#will be added in the future.    
def metaEltsForOtuElt(otu_id, ottol_name_id,db):
    'generates meta elements for an otu element'
    if db.ottol_name(ottol_name_id):
        idElt = dict()
        idElt["@xsi:type"] = "nex:LiteralMeta"
        idElt["@property"] = "ot:ottolid"
        idElt["$"] = db.ottol_name(ottol_name_id).preottol_taxid   # was opentree_uid
        return dict(meta = idElt)    
    else:
        return
    
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
    
def treeElt(tree_id,db):
    'generates a tree element'
    t = db.stree(tree_id)
    metaElts = metaEltsForTreeElt(tree_id,db)
    result = dict()
    result["@id"]='tree' + str(tree_id)
    result["node"]=treeNodes(tree_id,db)
    result["edge"]=treeEdges(tree_id,db)
    if metaElts:
    	result["@about"] = "#tree" + str(tree_id)
    	result.update(metaElts)
    return result
    
#Name suggests more than one meta element; expect more than current ot:branchLengthMode
#will be added in the future.    
def metaEltsForTreeElt(tree_id,db):
    'returns meta elements for a tree element'
    blRep = db.stree(tree_id).branch_lengths_represent
    if blRep:
        lengthsElt = dict()
        lengthsElt["@xsi:type"] = "nex:LiteralMeta"
        lengthsElt["@property"] = "ot:branchLengthMode"
        if (blRep == "substitutions per site"):
        	lengthsElt["$"] = "ot:substitutionCount"
        elif (blRep == "character changes"):
            lengthsElt["$"] = "ot:changesCount"
        elif (blRep == "time (Myr)"):
            lengthsElt["$"] = "ot:years"
        elif (blRep == "bootstrap values"):
            lengthsElt["$"] = "ot:bootstrapValues"                            
        elif (blRep == "posterior support"):
            lengthsElt["$"] = "ot:posteriorSupport"
        else:
        	return   #this is a silent fail, maybe better to return 'unknown'?
        return dict(meta=lengthsElt)
    else:
        return    
    
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
    if getNodeParent(nodeid,db):
        pass
    else:
        result["@root"] = 'true'
    result["@id"] = 'node'+str(nodeid)
    return result
