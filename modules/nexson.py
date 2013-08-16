#!/usr/bin/env python
# coding: utf8

#This module implements the export of nexml in JSON syntax.  The json follows the badgerfish 
#(http://badgerfish.ning.com - original site?) rules for mapping xml to json

#There are two entry points to this module: nexmlStudy (generate nexml for all the trees and otus for a study) and nexmlTree
#(complete nexml but just including a single tree - but currently all the otus for its containing study)

#local naming convention: get_XXX are DAL queries, generally returning an id or list of ids', everything else is generating
#dicts or lists that correspond to BadgerFish  mappings of Elements

#Output has been tested using the translator on http://dropbox.ashlock.us/open311/json-xml/ and validating the resulting
#xml with the validator at nexml.org

from gluon.storage import Storage
from gluon import *

# Note - the nexml root element can have meta elements as direct children; unlike everywhere else, there are no id or about
# attributes as seem to be required for other element types (e.g., otu, node) when they have meta children
def nexmlStudy(study_id,db):
    '''
    Exports the set of trees associated with a study as JSON Nexml
    study - the study to export
    db - database connection
    '''
    study_row = db.study(study_id)
    meta_elts = meta_elts_for_nexml(study_row,db) 
    otus = otus_elt_for_study(study_row,db)
    trees = trees_elt(study_row,db)
    header = nexml_header()
    body = {"@id":"study","@about":"#study"}
    body.update(header)
    body.update(meta_elts)
    body.update(otus)
    body.update(trees)
    return {"nexml":body}

def nexmlTree(tree,db):
    '''
    Exports one tree from a study (still a complete JSON NeXML with
    headers, otus, and trees blocks)
    '''
    study_row = db.study(get_single_tree_study_id(tree,db))
    meta_elts = meta_elts_for_nexml(study_row,db)
    tree_row = db.stree(tree)
    otus = otus_elt_for_tree(tree_row,study_row,db)
    trees = singleton_trees_elt(tree_row,study_row,db)
    header = nexml_header()
    body = {"@id":"study","@about":"#study"}
    body.update(otus)
    body.update(trees)
    body.update(header)
    body.update(meta_elts)
    return dict(nexml = body)

def nexml_header():
    '''
    Header for nexml - includes namespaces and version tag (see nexml.org)
    '''
    return {"@xmlns":xmlNameSpace(),
            "@version":'0.9',
            "@nexmljson":"http://opentree.wikispaces.com/NexSON",
            "@generator":"Phylografter nexml-json exporter"}

def xmlNameSpace():
    '''
    namespace definitions for nexml; will be value of xmlns attribute in header (per badgerfish 
    treatment of namespaces)
    '''
    return {"$":"http://www.nexml.org/2009",
            "nex":"http://www.nexml.org/2009",
            "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "ot":"http://purl.org/opentree-terms#",
            "xsd":"http://www.w3.org/2001/XMLSchema#"}

def createLiteralMeta(key, value):
    '''
    Creates a dict for the @property key -> value mapping of nex:LiteralMeta type
    '''
    return { "@xsi:type": "nex:LiteralMeta",
             "@property": key,
             "$": value,
           }

def createResourceMeta(key, value):
    '''
    creates a dict for the @property key -> value mapping of nex:ResourceMeta type
    '''
    return {"@xsi:type": "nex:ResourceMeta",
            "@property": key,
            "@href": value
           }

def meta_elts_for_nexml(study_row,db):
    '''
    generates nexml meta elements that are children of the root nexml element
    '''
    meta_array = []
    study_publication_meta = study_publication_meta_elt(study_row)
    if study_publication_meta:
        meta_array.append(study_publication_meta)
    doi_meta = doi_meta_for_study(study_row)
    if doi_meta:
        meta_array.append(doi_meta)
    curator_meta = curator_meta_for_study(study_row)
    if curator_meta:
        meta_array.append(curator_meta)
    treebase_deposit_meta = treebase_deposit_meta_for_study(study_row)
    if treebase_deposit_meta:
        meta_array.append(treebase_deposit_meta)
    phylografter_id_meta = phylografter_id_meta_for_study(study_row)
    if phylografter_id_meta:
        meta_array.append(phylografter_id_meta)
    year_meta = year_meta_for_study(study_row)
    if year_meta:
        meta_array.append(year_meta)
    focal_clade_meta = focal_clade_meta_for_study(study_row)
    if focal_clade_meta:
        meta_array.append(focal_clade_meta)
    study_tags = get_study_tags(study_row,db)
    if study_tags:
        for tag in study_tags:
           tag_elt = createLiteralMeta("ot:tag", tag)
           meta_array.append(tag_elt)
    return {"meta": meta_array}

def curator_meta_for_study(study_row):
    '''
    generates curator metadata element for a study
    '''
    curator = study_row.contributor
    if curator:
        return createLiteralMeta("ot:curatorName", curator)
    else:
        return

def treebase_deposit_meta_for_study(study_row):
    '''
    generates text citation metadata element for a study
    '''
    treebaseId = study_row.treebase_id
    if treebaseId:
        return createResourceMeta("ot:dataDeposit",
                                  "http://purl.org/phylo/treebase/phylows/study/TB2:S%d" % treebaseId)
    else:
        return

def year_meta_for_study(study_row):
    '''
    generates study year published metadata element for a study
    '''
    year = study_row.year_published
    if year:
        return createLiteralMeta("ot:studyYear",year)
    else:
        return

def doi_meta_for_study(study_row):
    '''
    generates returns an ot:studyPublication metadata element if a (possibly incomplete) doi or a 
    suitable URI is available for the study, else nothing
    '''
    doi = study_row.doi
    if doi:
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
        return createResourceMeta("ot:studyPublication", doi)
    else:
        return

def study_publication_meta_elt(study_row):
    '''
    generates text citation metadata element for a study
    '''
    cite = study_row.citation
    if (cite):
        return createLiteralMeta("ot:studyPublicationReference", cite)
    else:
        return

def phylografter_id_meta_for_study(study_row):
    '''
    generates phylografter study id metadata element for a study
    '''
    return createLiteralMeta("ot:studyId",str(study_row.id))
    
def focal_clade_meta_for_study(study_row):
    '''
    generates focal clade metadata element for a study
    '''
    focal_clade = study_row.focal_clade_ottol
    if (focal_clade):
        return createLiteralMeta("ot:focalClade", focal_clade)
    else:
        return
        
def get_study_tags(study_row,db):
    '''
    returns list of tags associated with the study; although
    name and value fields were defined for study tags, they were never used
    '''
    ta = db.study_tag
    q = (ta.study == study_row.id)
    rows = db(q).select()
    return [row.tag for row in rows]

def otus_elt_for_study(study_row,db):
    '''
    Generates an otus block
    '''
    otu_rows = get_otu_rows_for_study(study_row,db)
    meta_elts = meta_elts_for_otus(study_row,otu_rows,db)  #placeholder, no meta elements here
    otu_elements = [otu_elt(otu_row,db) for otu_row in otu_rows]
    otus_element = {"otu": otu_elements,
                    "@id": "otus%d" % study_row.id}
    return {"otus": otus_element}
    
def get_otu_rows_for_study(study_row,db):
    '''
    returns a tuple of list of otu ids for otu records that link to this study
    '''
    return db.executesql('SELECT otu.id, otu.label, otu.ottol_name, ottol_name.accepted_uid, ottol_name.name FROM otu LEFT JOIN ottol_name ON (otu.ottol_name = ottol_name.id) WHERE (otu.study = %d);' % study_row.id)
    
def meta_elts_for_otus(study_row,otuRows,db):
    '''
    generates nexml meta elements that are children of an otus element (currently none)
    '''
    return {}

def get_tree_rows_for_study(study_row,db):
    '''
    returns a list of the trees associated with the specified study
    '''
    s=db(db.stree.study==study_row.id)
    return s.select()

def otus_elt_for_tree(tree_row,study_row,db):
    '''
    get the otus for this tree (actually its study)
    '''
    otu_rows = get_otu_rows_for_study(study_row,db)
    node_rows = get_snode_recs_for_tree(tree_row,db)
    meta_elts = meta_elts_for_otus(study_row,otu_rows,db)
    otu_elements = [otu_elt(otu_row,db) for otu_row in otu_rows] 
    otus_element = {"otu": otu_elements,
                    "@id": "otus %s.%s" % (str(study_row.id),str(tree_row.id))}
    return {"otus",otus_element}
       
def otu_elt(otuRec,db):
    '''
    generates an otu element
    '''
    meta_elts = meta_elts_for_otu_elt(otuRec)
    otu_id,label,ottol_name,accepted_uid,name = otuRec
    result = {"@id": "otu%d" % otu_id}
    if (name):
        result["@label"] = name
    else:
        result["@label"] = label
    if meta_elts:
        result["@about"] = "#otu%d" % otu_id
        result.update(meta_elts)
    return result

def meta_elts_for_otu_elt(otuRec):
    '''
    generates meta elements for an otu element
    '''
    otu_id,label,ottol_name,accepted_uid,name = otuRec
    orig_label_el = createLiteralMeta("ot:originalLabel", label)
    if accepted_uid:
        a = createLiteralMeta("ot:ottolid", accepted_uid)
        return {"meta" : [a, orig_label_el]}
    return {"meta": orig_label_el}
    
def trees_elt(study,db):
    '''
    generate trees element
    '''
    row_list = get_tree_rows_for_study(study,db)
    tree_list = [tree_elt(tree_row,db) for tree_row in row_list]
    body={"@otus": "otus%d" % study.id,
          "@id": "trees%d" % study.id,
          "tree": tree_list}
    return {"trees": body}
    
def meta_elts_for_trees_elt(study,db):
    '''
    placeholder
    '''
    return dict()    

def singleton_trees_elt(tree_row,study_row,db):
    '''
    generate the singleton tree element for a tree request
    '''
    tree_list = [tree_elt(tree_row,db)]
    body={"@otus": "otus%d.%d" % (study_row.id, tree_row.id),
          "tree": tree_list
         }
    return {"trees": body}
    
def get_single_tree_study_id(tree,db):
    '''
    return the study that contains the specfied tree
    '''
    return db.stree(tree).study
    
def tree_elt(tree_row,db):
    '''
    generates a tree element
    '''
    meta_elts = meta_elts_for_tree_elt(tree_row,db)
    node_rows = get_snode_recs_for_tree(tree_row,db)
    result = {"@id": 'tree%d' % tree_row.id,
              "node": tree_nodes(node_rows),
              "edge": tree_edges(node_rows)
             }
    if meta_elts:
        result["@about"] = "#tree%d" % tree_row.id
        result.update(meta_elts)
    return result
    
bltypes = {"substitutions per site": "ot:substitutionCount",
           "character changes": "ot:changesCount",
           "time (Myr)": "ot:years",
           "bootstrap values": "ot:bootstrapValues",                            
           "posterior support": "ot:posteriorSupport"
           }

def meta_elts_for_tree_elt(tree_row,db):
    '''
    returns meta elements for a tree element
    '''
    result = []
    ingroup_node = tree_ingroup_node(tree_row,db)
    blRep = tree_row.branch_lengths_represent
    tree_tags = get_tree_tags(tree_row,db)
    if blRep in bltypes:
        lengthsElt = {"@xsi:type": "nex:LiteralMeta",
                      "@property": "ot:branchLengthMode",
                      "$": bltypes[blRep]}
        result.append(lengthsElt)
    if ingroup_node:
        ingroup_elt = dict()
        ingroup_elt["@xsi:type"] = "nex:LiteralMeta"
        ingroup_elt["@property"] = "ot:inGroupClade"
        ingroup_elt["$"] = 'node%d' % ingroup_node.id
        result.append(ingroup_elt)
    if tree_tags:
       for tag in tree_tags:
           tag_elt = dict()
           tag_elt["@xsi:type"] = "nex:LiteralMeta"
           tag_elt["@property"] = "ot:tag"
           tag_elt["$"] = tag
           result.append(tag_elt)
    if result:
        return dict(meta=result)
    else:
        return       #this is a silent fail, maybe better to return 'unknown'?

def tree_ingroup_node(tree_row,db):
    '''
    returns the id of a (the best) node that is tagged as the ingroup
    '''
    treeid = tree_row.id
    nodes = db((db.snode.tree==treeid) & (db.snode.ingroup=="T")).select()
    if len(nodes) == 0:
        return
    elif len(nodes) == 1: 
        return nodes.first()
    else:
        return deepest_ingroup(nodes)
        
def deepest_ingroup(nodes):
    '''
    chooses the deepest (closer to root) node when more than one is tagged
    '''
    best = nodes.first()
    for node in nodes:
        if (node.next < best.next) and (node.back > best.back):
            best = node
    return best
                        
def get_tree_tags(tree_row,db):
    '''
    returns a list of tag strings associated with the stree
    '''
    ta = db.stree_tag
    q = (ta.stree == tree_row.id)
    rows = db(q).select()
    result = [row.tag for row in rows]
    return result
                        
def tree_nodes(node_rows):
    '''
    formats the nodes corresponding to the rows in node_rows
    '''
    return [node_elt(node_row) for node_row in node_rows]
    
def tree_edges(node_rows):
    '''
    formats the edges leading to each node in the rows in node_rows
    '''
    return [edge_elt(node_row) for node_row in node_rows if node_row[1]]
    
def edge_elt(child_row):
    '''
    returns an element for a node - note that the information for this comes from the child node
    '''
    child_id,parent,otu_id,length = child_row
    result ={"@id": "edge%d" % child_id}
    result["@source"]='node%d' % parent
    result["@target"]='node%d' % child_id
    if (length):
        result["@length"]=length
    return result

def get_snode_recs_for_tree(tree_row,db):
    '''
    returns a list of the nodes associated with the specified study - now represented as tuples
    '''
    return db.executesql('SELECT id,parent,otu,length FROM snode WHERE (tree = %d);' % tree_row.id)
    
def node_elt(node_row):
    '''
    returns an element for a node
    '''
    node_id,parent,otu_id,length = node_row
    result = {"@id": "node%d" % node_id}
    if (otu_id):
        result["@otu"] = 'otu%d' % otu_id
    if parent:
        pass
    else:
        result["@root"] = 'true'
    return result
