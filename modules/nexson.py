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

# Note - the nexml root element can have meta elements as direct children; unlike everywhere else, there are no id or about
# attributes as seem to be required for other element types (e.g., otu, node) when they have meta children
def nexmlStudy(study_id,db):
    """
    Exports the set of trees associated with a study as JSON Nexml
    study - the study to export
    db - database connection
    """
    study_row = db.study(study_id)
    meta_elts = meta_elts_for_nexml(study_row,db)
    ## print 'meta done'
    otus, otu_id2name = otus_elt_for_study(study_row,db)
    ## print 'otus done'
    trees = trees_elt(study_row, db, otu_id2name)
    ## print 'trees done'
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
            "@nexmljson":"http://purl.org/opentree/nexson",
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

def createLiteralMeta(key, value, datatype=None):
    """
    Creates a dict for the @property key -> value mapping of nex:LiteralMeta type
    """
    meta= { "@xsi:type": "nex:LiteralMeta",
             "@property": key,
             "$": value,
           }
    if datatype:
        meta["@datatype"] =  datatype
    return meta

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
    focal_clade_name_meta = focal_clade_name_meta_for_study(study_row,db)
    if focal_clade_name_meta:
        meta_array.append(focal_clade_name_meta)
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

DOI_PREFIX = 'http://dx.doi.org/'
def doi_meta_for_study(study_row):
    '''
    generates returns an ot:studyPublication metadata element if a (possibly incomplete) doi or a 
    suitable URI is available for the study, else nothing
    '''
    doi = study_row.doi
    if doi:
        if (doi.startswith(DOI_PREFIX)):
            pass  #fine, leave as is
        elif (doi.startswith('http://www.')): #not a doi, but an identifier of some sort
            pass
        elif (doi.startswith('doi:')):    #splice the http prefix on
           doi = DOI_PREFIX + doi[4:]
        elif not(doi.startswith('10.')):  #not a doi, or corrupted, treat as blank
            return
        else:
           doi = DOI_PREFIX + doi
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
    focal_clade = study_row.focal_clade_ott
    if (focal_clade):
        return createLiteralMeta("ot:focalClade", focal_clade)

def focal_clade_name_meta_for_study(study_row,db):
    """
    generates a metadata element containing the OTT name of the focal clade
    (i.e., the name of the node returned in the preceeding function
    """
    focal_clade = study_row.focal_clade_ott
    if (focal_clade):
        name_query = db.executesql('SELECT ott_node.name FROM ott_node WHERE (ott_node.id = %s)' % focal_clade);
        if name_query:
            ((name,)) = name_query[0]
            return createLiteralMeta("ot:focalCladeOTTTaxonName",name)


def specified_root_meta_for_study(study_row):
    """
    generates a specified root element for a study (if available)
    """
    if 'specified_root' in db.study.fields:
       root = study_row.specified_root
       if (root):
           return createLiteralMeta("ot:specifiedRoot",root)
       else:
           return
    else:
        return

def get_study_tags(study_row,db):
    '''
    returns list of tags associated with the study; 
    '''
    ta = db.study_tag
    q = (ta.study == study_row.id)
    rows = db(q).select()
    # although name and value fields were defined for study tags, they were never used
    return [row.tag for row in rows]

def otus_elt_for_study(study_row,db):
    '''
    Generates an otus block
    '''
    otu_rows = get_otu_rows_for_study(study_row,db)
    ## print '  otu_rows done'
    otu_id2name = dict([ (x[0], x[4]) for x in otu_rows if x[4] ])
    meta_elts = meta_elts_for_otus(study_row,otu_rows,db)  #placeholder, no meta elements here
    otu_elements = [otu_elt(otu_row) for otu_row in otu_rows]
    ## print '  otu_elements done'
    otus_element = {"otu": otu_elements,
                    "@id": "otus%d" % study_row.id}
    return {"otus": otus_element}, otu_id2name

def get_otu_rows_for_study(study_row,db):
    '''
    returns a tuple of list of otu ids for otu records that link to this study
    '''
    return db.executesql('SELECT otu.id, otu.label, otu.ott_node, ott_node.id, ott_node.name, otu.tb_nexml_id FROM otu LEFT JOIN ott_node ON (otu.ott_node = ott_node.id) WHERE (otu.study = %d);' % study_row.id)

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
    otu_elements = [otu_elt(otu_row) for otu_row in otu_rows] 
    otus_element = {"otu": otu_elements,
                    "@id": "otus %s.%s" % (str(study_row.id),str(tree_row.id))}
    return {"otus",otus_element}

def otu_elt(otuRec):
    '''
    generates an otu element
    '''
    meta_elts = meta_elts_for_otu_elt(otuRec)
    otu_id,label,ott_node,accepted_uid,name,tb_name = otuRec
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
    otu_id,label,ott_node,accepted_uid,name,tb_name = otuRec
    orig_label_el = createLiteralMeta("ot:originalLabel", label)
    meta_list = []
    if accepted_uid:
        meta_list.append(createLiteralMeta("ot:ottId", accepted_uid))
    if tb_name:
        meta_list.append(createLiteralMeta("ot:treebaseOTUId", tb_name))
    if len(meta_list)>0:
       meta_list.append(orig_label_el)
       return {"meta": meta_list}
    return {"meta": orig_label_el}

def trees_elt(study, db, otu_id2name):
    '''
    generate trees element
    '''
    row_list = get_tree_rows_for_study(study,db)
    ## print '  tree_rows done'
    tree_list = [tree_elt(tree_row, db, otu_id2name) for tree_row in row_list]
    ## print '  tree_list done'
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

def tree_elt(tree_row, db, otu_id2name):
    '''
    generates a tree element
    '''
    meta_elts = meta_elts_for_tree_elt(tree_row,db)
    ## print '    tree_meta_elts done'
    node_rows = get_snode_recs_for_tree(tree_row,db)
    ## print '    tree_snode_recs done'
    result = {"@id": 'tree%d' % tree_row.id,
              "node": tree_nodes(node_rows, db, otu_id2name),
              "edge": tree_edges(node_rows)
             }
    ## print '    tree_nodes_and_edges done'
    if meta_elts:
        result["@about"] = "#tree%d" % tree_row.id
        result.update(meta_elts)
    return result

bltypes = {"substitutions per site": "ot:substitutionCount",
           "character changes": "ot:changesCount",
           "time (Myr)": "ot:time",
           "bootstrap values": "ot:bootstrapValues",
           "posterior support": "ot:posteriorSupport"
           }

def meta_elts_for_tree_elt(tree_row,db):
    """
    returns meta elements for a tree element
    """
    result = []
    ingroup_node = tree_ingroup_node(tree_row,db)
    blRep = tree_row.branch_lengths_represent
    tree_tags = get_tree_tags(tree_row,db)
    tree_type = tree_row.type
    if blRep in bltypes:
        lengthsElt = createLiteralMeta("ot:branchLengthMode",bltypes[blRep])
        result.append(lengthsElt)
        if blRep == "time (Myr)":
            timeUnitElt = createLiteralMeta("ot:branchLengthTimeUnit", "Myr")
            result.append(timeUnitElt)
    if ingroup_node:
        ingroup_elt = createLiteralMeta("ot:inGroupClade",'node%d' % ingroup_node.id)
        result.append(ingroup_elt)
    if tree_tags:
       for tag in tree_tags:
           tag_elt = createLiteralMeta("ot:tag",tag)
           result.append(tag_elt)
    if (tree_type != ""):  # this is supposed to be not null, but might still be blank
        curatedType_elt = createLiteralMeta("ot:curatedType",tree_type)
        result.append(curatedType_elt)
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

def tree_nodes(node_rows, db, otu_id2name):
    '''
    formats the nodes corresponding to the rows in node_rows
    '''
    return [node_elt(node_row, db, otu_id2name) for node_row in node_rows]

def tree_edges(node_rows):
    '''
    formats the edges leading to each node in the rows in node_rows
    '''
    #node_row[1] is parent - test excludes root node
    return [edge_elt(node_row) for node_row in node_rows if node_row[1]]

def edge_elt(child_row):
    '''
    returns an element for a node - note that the information for this comes from the child node
    '''
    child_id,parent,otu_id,length,ignore = child_row
    result ={"@id": "edge%d" % child_id}
    result["@source"]='node%d' % parent
    result["@target"]='node%d' % child_id
    if (length):
        result["@length"]=length
    return result

def get_snode_recs_for_tree(tree_row,db):
    """
    returns a list of the nodes associated with the specified study - now represented as tuples
    """
    return db.executesql('SELECT id,parent,otu,length,isleaf FROM snode WHERE (tree = %d);' % tree_row.id)

def node_elt(node_row, db, otu_id2name):
    """
    returns an element for a node
    """
    node_id,parent,otu_id,length,isleaf = node_row
    meta_elts = meta_elts_for_node_elt(node_row, db, otu_id2name)
    result = {"@id": "node%d" % node_id}
    if otu_id:
        result["@otu"] = 'otu%d' % otu_id
    if parent:
        pass
    else:
        result["@root"] = 'true'
    if meta_elts:
        result["@about"] = "#node%d" % node_id
        result.update(meta_elts)
    return result

def meta_elts_for_node_elt(node_row, db, otu_id2name):
    """
    returns metadata elements for a node (currently ot:isLeaf,ot:ottTaxonName)
    """
    result=[]
    node_id,parent,otu_id,length,isleaf = node_row
    if isleaf == 'T':
        isLeaf_elt = createLiteralMeta("ot:isLeaf","true","xsd:boolean")
        result.append(isLeaf_elt)
    if otu_id and otu_id in otu_id2name:
        result.append(createLiteralMeta("ot:ottTaxonName",otu_id2name[otu_id]))
    if result:
        return dict(meta=result)
    return
