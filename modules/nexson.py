#!/usr/bin/env python
# coding: utf8

# This module implements the export of nexml in JSON syntax.  The json follows
# the badgerfish (http://badgerfish.ning.com - original site?) rules for
# mapping xml to json

# There are two entry points to this module: nexmlStudy (generate nexml for all 
# the trees and otus for a study) and nexmlTree (complete nexml but just 
# including a single tree - but currently all the otus for its containing study)

# local naming convention: get_XXX are database queries (either high level web2py
# DAL calls or SQL passed through the DAL's executeSQL which is substantially
# faster.  These generally return an id or list of ids.
# Everything else is generating dicts or lists that correspond to BadgerFish  
# mappings of XML elements 

# Output has historically been tested using the translator on 
# http://dropbox.ashlock.us/open311/json-xml/ and validating the resulting
# xml with the validator at nexml.org.  Currently these files are tested 
# with the peyotl package (https://github.com/OpenTreeOfLife/peyotl)

from gluon.storage import Storage


# Note - the nexml root element can have meta elements as direct children;
# unlike everywhere else, there are no id or about
# attributes as seem to be required for other element types 
# (e.g., otu, node) when they have meta children
def nexmlStudy(study_id, db):
    """
    Exports the set of trees associated with a study as JSON Nexml
    study - the study to export
    db - database connection
    """
    study_row = db.study(study_id)
    meta_elts = meta_elts_for_nexml(study_row, db)
    study_label = study_row.label
    otus = otus_elt_for_study(study_row, db)
    trees = trees_elt(study_row, db)
    header = nexml_header()
    if study_label:
        body = {"@id": "study", "@about": "#study", "@label": study_label}
    else:
        body = {"@id": "study", "@about": "#study"}
    body.update(header)
    body.update(meta_elts)
    body.update(otus)
    body.update(trees)
    return {"nexml": body}


def nexmlTree(tree, db):
    """
    Exports one tree from a study (still a complete JSON NeXML with
    headers, otus, and trees blocks)
    """
    study_row = db.study(get_single_tree_study_id(tree,db))
    meta_elts = meta_elts_for_nexml(study_row, db)
    study_label = study_row.label
    tree_row = db.stree(tree)
    otus = otus_elt_for_tree(tree_row,study_row,db)
    trees = singleton_trees_elt(tree_row,study_row,db)
    header = nexml_header()
    if study_label:
        body = {"@id": "study", "@about": "#study", "@label": study_label}
    else:
        body = {"@id": "study", "@about": "#study"}
    body.update(otus)
    body.update(trees)
    body.update(header)
    body.update(meta_elts)
    return dict(nexml = body)


def nexml_header():
    """
    Header for nexml - includes namespaces and version tag (see nexml.org)
    """
    return {"@xmlns": xmlNameSpace(),
            "@version": '0.9',
            "@nexmljson": "http://purl.org/opentree/nexson",
            "@generator": "Phylografter nexml-json exporter"}


def xmlNameSpace():
    """
    namespace definitions for nexml; will be value of xmlns attribute in header (per badgerfish 
    treatment of namespaces)
    """
    return {"$": "http://www.nexml.org/2009",
            "nex": "http://www.nexml.org/2009",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "ot": "http://purl.org/opentree-terms#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"}


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
    """
    creates a dict for the @property key -> value mapping of nex:ResourceMeta type
    """
    return {"@xsi:type": "nex:ResourceMeta",
            "@rel": key,
            "@href": value
           }

def meta_elts_for_nexml(study_row,db):
    """
    generates nexml meta elements that are children of the root nexml element
    """
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
    specified_root_meta = specified_root_meta_for_study(study_row, db)
    if specified_root_meta:
        meta_array.append(specified_root_meta)
    comment_meta = comment_meta_for_study(study_row, db)
    if comment_meta:
        meta_array.append(comment_meta)
    # these next two are primarily to support phylografter round tripping
    # they should be coverted ti annotation elements and deprecated ASAP
    last_modified_meta = last_modified_meta_for_study(study_row, db)
    if last_modified_meta:
        meta_array.append(last_modified_meta)
    uploaded_date_meta = uploaded_date_meta_for_study(study_row, db)
    if uploaded_date_meta:
        meta_array.append(uploaded_date_meta)
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


def specified_root_meta_for_study(study_row, db):
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


def comment_meta_for_study(study_row, db):
    """
    generates a comment element for a study
    """
    return createLiteralMeta("ot:comment",str(study_row.comment))


def last_modified_meta_for_study(study_row, db):
    """
    generates an element capturing phylografter's last modified date for a study.
    this should be deprecated when phylografter properly handles annotations
    """
    return createLiteralMeta("ot:last_modified",str(study_row.last_modified))


def uploaded_date_meta_for_study(study_row, db):
    """
    generates an element capturing when a study was uploaded to phylografter
    this should be deprecated when phylografter properly handles annotations
    """
    return createLiteralMeta("ot:uploaded",str(study_row.uploaded))

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
    meta_elts = meta_elts_for_otus(study_row,otu_rows,db)  #placeholder, no meta elements here
    otu_elements = [otu_elt(otu_row) for otu_row in otu_rows]
    ## print '  otu_elements done'
    otus_element = {"otu": otu_elements,
                    "@id": "otus%d" % study_row.id}
    return {"otus": otus_element}

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
    if name:
        meta_list.append(createLiteralMeta("ot:ottTaxonName", name))
    if len(meta_list)>0:
       meta_list.append(orig_label_el)
       return {"meta": meta_list}
    return {"meta": orig_label_el}

def trees_elt(study, db):
    '''
    generate trees element
    '''
    row_list = get_tree_rows_for_study(study,db)
    ## print '  tree_rows done'
    tree_list = [tree_elt(tree_row, db) for tree_row in row_list]
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

def tree_elt(tree_row, db):
    '''
    generates a tree element
    '''
    meta_elts = meta_elts_for_tree_elt(tree_row,db)
    node_rows = get_snode_recs_for_tree(tree_row,db)
    node_label_mode = tree_row.clade_labels_represent
    result = {"@id": 'tree%d' % tree_row.id,
              "node": tree_nodes(node_rows, db, node_label_mode),
              "edge": tree_edges(node_rows)
             }
    if meta_elts:
        result["@about"] = "#tree%d" % tree_row.id
        result.update(meta_elts)
    return result


# These vocabularies are documented here: 
# https://github.com/OpenTreeOfLife/phylesystem-api/wiki/NexSON
bltypes = {"substitutions per site": "ot:substitutionCount",
           "character changes": "ot:changesCount",
           "time (Myr)": "ot:time",
           "bootstrap values": "ot:bootstrapValues",
           "posterior support": "ot:posteriorSupport"
           }


# Note the last three are defined in the NexSON specification
# but not in the table definition of stree (models/A_define_tables.py)
NODE_LABEL_TYPES = {"taxon Names": "ot:taxonNames",
                    "bootstrap values": "ot:bootstrapValues",
                    "posterior support": "ot:posteriorSupport",
                    "other": "ot:other",
                    "undefined": "ot:undefined",
                    "root node id": "ot:rootNodeId"
                    }


def meta_elts_for_tree_elt(tree_row,db):
    """
    returns meta elements for a tree element
    """
    result = []
    node_label_rep = tree_row.clade_labels_represent
    tree_tags = get_tree_tags(tree_row,db)
    tree_type = tree_row.type
    tb_tree_id = tree_row.tb_tree_id
    contributor = tree_row.contributor
    uploaded = tree_row.uploaded
    blComment = tree_row.branch_lengths_comment
    clComment = tree_row.clade_labels_comment
    author_contributed = tree_row.author_contributed
    comment = tree_row.comment
    blRep = tree_row.branch_lengths_represent
    if blRep in bltypes:
        lengthsElt = createLiteralMeta("ot:branchLengthMode",bltypes[blRep])
        result.append(lengthsElt)
        if blRep == "time (Myr)":
            timeUnitElt = createLiteralMeta("ot:branchLengthTimeUnit", "Myr")
            result.append(timeUnitElt)
    if node_label_rep in NODE_LABEL_TYPES:
        nlabelElt = createLiteralMeta("ot:nodeLabelMode",NODE_LABEL_TYPES[node_label_rep])
        result.append(nlabelElt)
    ingroup_node = tree_ingroup_node(tree_row,db)
    if ingroup_node:
        ingroup_elt = createLiteralMeta("ot:inGroupClade",'node%d' % ingroup_node.id)
        result.append(ingroup_elt)
    if tb_tree_id:
        result.append(createLiteralMeta("ot:tb_tree_id", tb_tree_id))
    if contributor:
        result.append(createLiteralMeta("ot:contributor", contributor))
    if uploaded:
        result.append(createLiteralMeta("ot:uploaded", uploaded))
    if blComment:
        result.append(createLiteralMeta("ot:branch_lengths_comment", blComment))
    if clComment:
        result.append(createLiteralMeta("ot:clade_labels_comment", clComment))
    if comment:
        result.append(createLiteralMeta("ot:comment", comment))
    if author_contributed:
        result.append(createLiteralMeta("ot:author_contributed", True, "xsd:boolean"))
    if tree_tags:
       for tag in tree_tags:
           tag_elt = createLiteralMeta("ot:tag",tag)
           result.append(tag_elt)
    if (tree_type != ""):  # this is supposed to be not null, but might still be blank
        curatedType_elt = createLiteralMeta("ot:curatedType",tree_type)
        result.append(curatedType_elt)
    if result:
        return {"meta": result}


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

def get_tree_tags(tree_row, db):
    '''
    returns a list of tag strings associated with the stree
    '''
    ta = db.stree_tag
    q = (ta.stree == tree_row.id)
    rows = db(q).select()
    return [row.tag for row in rows]


def tree_nodes(node_rows, db, tree_label_mode):
    '''
    formats the nodes corresponding to the rows in node_rows
    '''
    return [node_elt(node_row, db, tree_label_mode) for node_row in node_rows]

def tree_edges(node_rows):
    '''
    formats the edges leading to each node in the rows in node_rows
    '''
    #node_row[1] is parent - test excludes root node
    return [edge_elt(node_row) for node_row in node_rows if node_row[1]]

def edge_elt(node_row):
    """
    returns an edge element for a node - note that the information for this comes from the child node
    """
    (child_id,parent,_,length,_,_,_,_,_,_,_,_) = node_row
    meta_elts = meta_elts_for_edge_support(node_row)
    edge_id = "edge%d" % child_id
    result ={"@id": edge_id,
             "@source": 'node%d' % parent,
             "@target":'node%d' % child_id}
    if length:
        result["@length"]=length
    if meta_elts:
        result["@about"] = '#' + edge_id
        result.update(meta_elts)        
    return result

def meta_elts_for_edge_support(edge):
    (child,parent,_,length,_,_,_,_,bootstrap_support,posterior_support,other_support,other_support_type) = edge
    result = []
    if bootstrap_support:
        result.append(createLiteralMeta("ot:bootstrap_support", bootstrap_support, "xsd:double"))
    if posterior_support:
        result.append(createLiteralMeta("ot:posterior_support", posterior_support, "xsd:double"))
    if other_support:
        result.append(createLiteralMeta("ot:other_support", other_support, "xsd:double"))
    if other_support_type:
        result.append(createLiteralMeta("ot:other_support_type", othersupport_type))
    if result:
        return {'meta': result}

def get_snode_recs_for_tree(tree_row,db):
    """
    returns a list of the nodes associated with the specified study - now represented as tuples
    """
    query = ''.join(['SELECT id,parent,otu,length,isleaf,age,age_min,age_max,bootstrap_support,',
                    'posterior_support,other_support,other_support_type FROM snode WHERE (tree = %d);'])
    return db.executesql(query % tree_row.id)


def node_elt(node_row, db, node_label_mode):
    """
    returns an element for a node
    """
    (node_id,parent,otu_id,length,isleaf,_,_,_,_,_,_,_) = node_row
    meta_elts = meta_elts_for_node_elt(node_row, db)
    result = {"@id": "node%d" % node_id}
    if otu_id:
        result["@otu"] = 'otu%d' % otu_id
    if parent:
        pass
    else:
        result["@root"] = True
    if meta_elts:
        result["@about"] = "#node%d" % node_id
        result.update(meta_elts)
    return result

def meta_elts_for_node_elt(node_row, db):
    """
    returns metadata elements for a node (currently ot:isLeaf)
    """
    result=[]
    (_,_,_,_,isleaf,age,age_min,age_max,_,_,_,_) = node_row
    if isleaf == 'T':
        isLeaf_elt = createLiteralMeta("ot:isLeaf",True,"xsd:boolean")
        result.append(isLeaf_elt)
    #ottTaxonName has moved several times between nodes and otus - 
    #currently on otus so no need to retrieve ott_node.name here
    if result:
        return dict(meta=result)
    return
