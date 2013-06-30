#!/usr/bin/env python
# coding: utf8

#This module implements the export of nexml in JSON syntax.  The json follows the badgerfish 
#(http://badgerfish.ning.com - original site?) rules for mapping xml to json

#There are two entry points to this module: nexmlStudy (generate nexml for all the trees and otus for a study) and nexmlTree
#(complete nexml but just including a single tree - but currently all the otus for its containing study)

#local naming convention: getXXX are DAL queries, generally returning an id or list of ids', everything else is generating
#dicts or lists that correspond to BadgerFish  mappings of Elements

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
    studyRow = db.study(studyId)
    metaElts = metaEltsForNexml(studyRow) 
    otus = otusEltForStudy(studyRow,db)
    trees = treesElt(studyRow,db)
    header = nexmlHeader()
    body = dict()
    body.update(otus)
    body.update(trees)
    body.update(header)
    body.update(metaElts)
    body["@id"] = "study"
    body["@about"] = "#study"
    return dict(nexml = body)

def nexmlTree(tree,db):
    '''Exports one tree from a study (still a complete JSON NeXML with
    headers, otus, and trees blocks)'''
    studyRow = db.study(getSingleTreeStudyId(tree,db))
    metaElts = metaEltsForNexml(studyRow)
    treeRow = db.stree(tree)
    otus = otusEltForTree(treeRow,studyRow,db)
    trees = singletonTreesElt(treeRow,studyRow,db)
    header = nexmlHeader()
    body = dict()
    body.update(otus)
    body.update(trees)
    body.update(header)
    body.update(metaElts)
    body["id"] = "study"
    body["@about"] = "#study"
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

def metaEltsForNexml(studyRow):
    'generates nexml meta elements that are children of the root nexml element'
    metaArray = []
    studyPublicationMeta = studyPublicationMetaElt(studyRow)
    if studyPublicationMeta:
        metaArray.append(studyPublicationMeta)
    doiMeta = doiMetaForStudy(studyRow)
    if doiMeta:
        metaArray.append(doiMeta)
    curatorMeta = curatorMetaForStudy(studyRow)
    if curatorMeta:
        metaArray.append(curatorMeta)
    treeBaseDepositMeta = treeBaseDepositMetaForStudy(studyRow)
    if treeBaseDepositMeta:
        metaArray.append(treeBaseDepositMeta)
    phylografterIdMeta = phylografterIdMetaForStudy(studyRow)
    if phylografterIdMeta:
        metaArray.append(phylografterIdMeta)
    yearMeta = yearMetaForStudy(studyRow)
    if yearMeta:
        metaArray.append(yearMeta)
    focalCladeMeta = focalCladeMetaForStudy(studyRow)
    if focalCladeMeta:
        metaArray.append(focalCladeMeta)
    return dict(meta = metaArray)

def curatorMetaForStudy(studyRow):
    'generates curator metadata element for a study'
    curator = studyRow.contributor
    if (curator):
        #names = metaNSForDCTerm()
        result = dict()
        result["@xsi:type"] = "nex:LiteralMeta"
        result["@property"] = "ot:curatorName"
        result["$"] = curator
        return result
    else:
        return

def treeBaseDepositMetaForStudy(studyRow):
    'generates text citation metadata element for a study'
    treebaseId = studyRow.treebase_id
    if (treebaseId):
        #names = metaNSForDCTerm()
        result = dict()
        result["@xsi:type"] = "nex:ResourceMeta"
        result["@property"] = "ot:dataDeposit"
        result["@href"] = "http://purl.org/phylo/treebase/phylows/study/TB2:S%d" % treebaseId
        return result
    else:
        return

def yearMetaForStudy(studyRow):
    'generates study year published metadata element for a study'
    year = studyRow.year_published
    if (year):
        #names = metaNSForDCTerm()
        result = dict()
        result["@xsi:type"] = "nex:LiteralMeta"
        result["@property"] = "ot:studyYear"
        result["$"] = year
        return result
    else:
        return

#returns an ot:studyPublication metadata element if a (possibly incomplete) doi or a 
#suitable URI is available, else nothing
def doiMetaForStudy(studyRow):
    'generates ot:studyPublication metadata element for a study'
    doi = studyRow.doi
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

def studyPublicationMetaElt(studyRow):
    'generates text citation metadata element for a study'
    cite = studyRow.citation
    if (cite):
        result = dict()
        result["@xsi:type"] = "nex:LiteralMeta"
        result["@property"] = "ot:studyPublicationReference"
        result["$"] = cite
        return result
    else:
        return

def phylografterIdMetaForStudy(studyRow):
    'generates phylografter study id metadata element for a study'
    result = dict()
    result["@xsi:type"] = "nex:LiteralMeta"
    result["@property"] = "ot:studyId"
    result["$"] = str(studyRow.id)
    return result
    
def focalCladeMetaForStudy(studyRow):
    'generates focal clade metadata element for a study'
    focal_clade = studyRow.focal_clade_ottol
    if (focal_clade):
        result = dict()
        result["@xsi:type"] = "nex:LiteralMeta"
        result["@property"] = "ot:focalClade"
        result["$"] = focal_clade
        return result
    else:
        return
        
def otusEltForStudy(studyRow,db):
    'Generates an otus block'
    otuRows = getOtuRowsForStudy(studyRow,db)
    metaElts = metaEltsForOtus(studyRow,otuRows,db)
    otuElements = [otuElt(otuRow,db) for otuRow in otuRows]
    otusElement = dict()
    otusElement["otu"] = otuElements
    otusElement["@id"] = "otus%d" % studyRow.id
    return dict(otus = otusElement)
    
def getOtuRowsForStudy(studyRow,db):
    'returns a list of otu ids for otu records that link to this study'
    return db.executesql('SELECT otu.id, otu.label, otu.ottol_name, ottol_name.accepted_uid, ottol_name.name FROM otu LEFT JOIN ottol_name ON (otu.ottol_name = ottol_name.id) WHERE (otu.study = %d);' % studyRow.id)
#    return db.executesql('SELECT otu.id, otu.label, otu.ottol_name, ottol_name.uid, ottol_name.parent_uid, ottol_name.accepted_uid, ottol_name.ncbi_taxid, ottol_name.gbif_taxid, ottol_name.namebank_taxid, ottol_name.treebase_taxid, ottol_name.name, ottol_name.unique_name, ottol_name.rank, ottol_name.comments FROM otu LEFT JOIN ottol_name ON (otu.ottol_name = ottol_name.id) WHERE (otu.study = %d);' % studyRow.id,as_dict="true")
#    return db.executesql('SELECT id,label,ottol_name FROM otu WHERE (study = %d);' % studyRow.id,as_dict="true")
    
def metaEltsForOtus(studyRow,otuRows,db):
    'generates nexml meta elements that are children of an otus element'
    result = dict()
    return result
    
def getTreeRowsForStudy(studyRow,db):
    'returns a list of the trees associated with the specified study'
    studyid = studyRow.id
    treeStudy = db.stree.study
    s=db(treeStudy==studyid)
    rows = s.select()
    return rows
    
def otusEltForTree(treeRow,studyRow,db):
    ##get the otus for this tree (actually its study)
    otuRows = getOtuRowsForStudy(studyRow,db)
    nodeRows = getSNodeRecsForTree(treeRow,db)
    metaElts = metaEltsForOtus(studyRow,otuRows,db)
    otuElements = [otuElt(otuRow,db) for otuRow in otuRows] 
    otusElement = dict()
    otusElement["otu"] = otuElements
    otusElement["@id"] = "otus" + str(studyRow.id) + "." + str(treeRow.id)
    result = dict()
    result["otus"] = otusElement
    return result
       
#Generates an otu Element             
def otuElt(otuRec,db):
    metaElts = metaEltsForOtuElt(otuRec)
    otu_id,label,ottol_name,accepted_uid,name = otuRec
    result = dict()
    result["@id"] = "otu%d" % otu_id
    if (name):
        result["@label"] = name
    else:
        result["@label"] = label
    if metaElts:
        result["@about"] = "#otu%d" % otu_id
        result.update(metaElts)
    return result
    
#Name suggests more than one meta element; expect more than current ot:ottolid
#will be added in the future.    
def metaEltsForOtuElt(otuRec):
    'generates meta elements for an otu element'
    otu_id,label,ottol_name,accepted_uid,name = otuRec
    if accepted_uid:
        idElt = dict()
        idElt["@xsi:type"] = "nex:LiteralMeta"
        idElt["@property"] = "ot:ottolid"
        idElt["$"] = accepted_uid
        return dict(meta = idElt)    
    else:
        return
    
def treesElt(study,db):
    'generate trees element'
    rowList = getTreeRowsForStudy(study,db)
    if (len(rowList) == 1):
        treeList = [treeElt(rowList[0],db)]
        body=dict()
        body["@otus"] = "otus%d" % study.id
        body["@id"] = "trees%d" % study.id
        body["tree"] = treeList
        result = dict()
        result["trees"] = body
    else:
        treeElements = [treeElt(treeRow,db) for treeRow in rowList]
        treesElement = dict()
        treesElement["tree"] = treeElements
        treesElement["@otus"] = "otus%d" % study.id
        treesElement["@id"] = "trees%d" % study.id
        result = dict()
        result["trees"] = treesElement
    return result
    
def metaEltsForTreesElt(study,db):
    return dict()    

def singletonTreesElt(treeRow,studyRow,db):
    'generate the singleton tree element for a tree request'
    treeList = [treeElt(treeRow,db)]
    body=dict()
    body["@otus"] = "otus%d.%d" % (studyRow.id, treeRow.id)
    body["tree"] = treeList
    result = dict()
    result["trees"] = body
    return result
    
def getSingleTreeStudyId(tree,db):
    return db.stree(tree).study
    
def treeElt(treeRow,db):
    'generates a tree element'
    metaElts = metaEltsForTreeElt(treeRow,db)
    nodeRows = getSNodeRecsForTree(treeRow,db)
    result = dict()
    result["@id"]='tree%d' % treeRow.id
    result["node"]=treeNodes(nodeRows)
    result["edge"]=treeEdges(nodeRows)
    if metaElts:
    	result["@about"] = "#tree%d" % treeRow.id
    	result.update(metaElts)
    return result
    
#Name suggests more than one meta element; expect more than current ot:branchLengthMode
#will be added in the future.    
def metaEltsForTreeElt(treeRow,db):
    'returns meta elements for a tree element'
    result = []
    ingroupNode = treeInGroupNode(treeRow,db)
    blRep = treeRow.branch_lengths_represent
    tree_tags = get_tree_tags(treeRow,db)
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
        result.append(lengthsElt)
    if ingroupNode:
        ingroupElt = dict()
        ingroupElt["xsi:type"] = "nex:LiteralMeta"
        ingroupElt["@property"] = "ot:inGroupClade"
        ingroupElt["$"] = 'node%d' % ingroupNode.id
        result.append(ingroupElt)
    if tree_tags:
       tags_elt = dict()
       tags_elt["xsi:type"] = "nex:LiteralMeta"
       tags_elt["@property"] = "ot:tags"
       tags_elt["$"] = tree_tags
       result.append(tags_elt)
    if result:
        return dict(meta=result)
    else:
        return

def treeInGroupNode(treeRow,db):
    'returns the id of a (the best) node that is tagged as the ingroup'
    treeid = treeRow.id
    nodes = db((db.snode.tree==treeid) & (db.snode.ingroup=="T")).select()
    if len(nodes) == 0:
        return
    elif len(nodes) == 1: 
        return nodes.first()
    else:
        return deepestIngroup(treeRow,nodes)
        
def deepestIngroup(treeRow,nodes):
    'chooses the deepest (closer to root) node when more than one is tagged'
    best = nodes.first()
    for node in nodes:
        if (node.next < best.next) and (node.back > best.back):
            best = node
    return best
                        
def get_tree_tags(tree_row,db):
    result = []
    ta = db.stree_tag
    q = (ta.stree == tree_row.id)
    rows = db(q).select()
    for row in rows:
        ##Note: name and value in stree_tag table are never used 
        result.append(row.tag)
    return
                        
def treeNodes(nodeRows):
    body = [nodeElt(nodeRow) for nodeRow in nodeRows]
    return body
    
def treeEdges(nodeRows):
    edgeList = [edgeElt(nodeRow) for nodeRow in nodeRows if nodeRow[1]]
    return edgeList
    
def edgeElt(childRow):
    result = dict()
    child_id,parent,otu_id,length = childRow
    childStr = str(child_id)
    result["@id"]='edge%d' % child_id
    result["@source"]='node%d' % parent
    result["@target"]='node%d' % child_id
    if (length):
        result["@length"]=length
    return result

def getSNodeRecsForTree(treeRow,db):
    'returns a list of the nodes associated with the specified study - now represented as tuples'
    return db.executesql('SELECT id,parent,otu,length FROM snode WHERE (tree = %d);' % treeRow.id)
    
def nodeElt(nodeRow):
    result = dict()
    node_id,parent,otu_id,length = nodeRow
    if (otu_id):
        result["@otu"] = 'otu%d' % otu_id
    if parent:
        pass
    else:
        result["@root"] = 'true'
    result["@id"] = 'node%d' % node_id
    return result
