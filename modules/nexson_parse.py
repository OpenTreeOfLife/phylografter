#!/usr/bin/env python
# coding: utf8
from gluon import *
from sys import maxsize

def nexson_available(u):
    """
    """
    import requests
    r = requests.get(u)
    result = (r.status_code == 200)
    r.close()
    return result

def check_nexson(u, db, study_id):
    """
    checks if study with a matching identifier (doi or citation if no doi) is
    already present so user can be warned
    """
    #from json import load
    import requests
    r = requests.get(u)
    if r.status_code == 200:
       json_tree = r.json()       #want api call that returns study identifier(s)
       if u'data' in json_tree:
           nexml_tree = json_tree[u'data']
           return check_json_study(nexml_tree, db, study_id)
       elif u'error' in json_tree:
           description = json_tree[u'description']
           raise RuntimeException(description)
    else:
        raise HTTP(r.status_code,"Error retrieving study")

def check_json_study(nexml_tree, db, study_id):
    """
    Returns True if db contains a study with matching doi (best) or
    reference citation
    """
    contents = nexml_tree[u'nexml']
    metaEle = contents[u'meta']
    metafields = parse_study_meta(metaEle)
    if 'ot:studyPublication' in metafields:
        doi = metafields['ot:studyPublication']
        q = (db.study.doi == doi)
        rows = db(q).select()
        if len(rows) > 0:
            match = rows[0].id
            # print "matching on %s" % doi
            if not (match == study_id) :
                if worthless_study(nexml_tree):
                    # print "study is worthless"
                    if len(db(db.study.id == study_id).select()) > 0:
                        return study_id
                    else:
                        return False
                else:
                    return match
            else:
                return match
        else:
            return False  #bad study id is treated as resource not found
    elif 'ot:studyPublicationReference' in metafields:
        ref = metafields['ot:studyPublicationReference']
        q = (db.study.citation == ref)
        rows = db(q).select()
        if len(rows) > 0:
            match = rows[0].id
            # print "matching on %s" % ref
            # print "match %d, study %d" % (match, study_id)
            if not (match == study_id) :
                if worthless_study(nexml_tree):
                   # print "study is worthless"
                    if len(db(db.study.id == study_id).select()) > 0:
                        return study_id
                    else:
                        return False
                else:
                    return match
            else:
                return match
        else:
            return False
    else:
        # print "No study identifier found"
        return False

def worthless_study(tree):
    """
    """
    contents = tree[u'nexml']
    otus_ele = contents[u'otus']
    otu_ele = otus_ele[u'otu']
    if otu_ele is None or len(otu_ele) == 0:
        return True
    # print "otus is %s" % otu_ele 
    trees_ele = contents[u'trees']
    tree_ele = trees_ele[u'tree']
    if tree_ele is None or len(tree_ele) == 0:
        return True
    # print "trees is %s" % tree_ele 
    return False


def ingest_nexson(u,db,recycled_id):
    """
    Entry point - nexson is parsed and dispatched to the appropriate updater
    f - file like object (generally a CStringIO, retrieved from a post)
    db - web2py database object
    recycled_id - if a number, specifies the available id of a (now deleted) study
    """
    #from json import load
    import requests
    r = requests.get(u)
    json_tree = r.json()
    if u'data' in json_tree:
        nexml_tree = json_tree[u'data']
    else:
        nexml_tree = json_tree
    if recycled_id:
        study_id = recycled_id
    else:
        study_id = get_study_id(nexml_tree)
    return ingest_json_study(nexml_tree,db,study_id)


def get_study_id(nexml_tree):
    """
    extracts the previous study id if available
    """
    contents = nexml_tree[u'nexml']
    metaEle = contents[u'meta']
    metafields = parse_study_meta(metaEle)
    if 'ot:studyId' in metafields:
        if (metafields['ot:studyId'][2] == '_'):
            return int(metafields['ot:studyId'][3:])
        else:
            return int(metafields['ot:studyId'])
    else:
        # print "No study id found";
        return None  #no id, nothing to do


#put this in one place so it can be turned off easily when the time comes
def encode(str):
    return str  #.encode('ascii')

SQLFIELDS = {'ot:studyPublication': 'doi',
             'ot:studyPublicationReference': 'citation',
             'ot:studyYear': 'year_published',
             'ot:curatorName': 'contributor',
             'ot:focalClade': 'focal_clade_ott',
             'ot:dataDeposit': 'dataDeposit'}

def process_meta_element_sql(contents, results, db):
    """
    Builds the list of database updates corresponding to the study
    element's child 'meta' elements.  Each tuple added to results
    should contain the literal 'study' (the table), a valid field
    in the study table, and an appropriate value.  Note that this
    is mapping Nexson vocabulary to phylografter fields (should 
    happen here and in similar functions below)
    """
    metaEle = contents[u'meta']
    metafields = parse_study_meta(metaEle)
    if 'ot:studyId' in metafields:
        results.append(('study','nexson_id',metafields['ot:studyId']))
    else:
        # print "No study id found";
        return None  #no id, nothing to do
    for mf in metafields:
        if mf == 'ot:annotation':  #note that annotations don't seem to have their own id
            results.append(('annotation','nexson_id',metafields['ot:studyId'])) # use containing study's id
            results.append(('annotation','annotation',metafields['ot:annotation']))
        elif mf == 'ot:tag':
            for tag in metafields['ot:tag']:
                results.append(('study','tag',tag))
        elif mf in SQLFIELDS:
            results.append(('study',SQLFIELDS[mf],metafields[mf]))
        elif mf == 'ot:studyId':
            pass
        elif mf == 'other_metadata':
            results.append(('study','other_metadata',metafields['other_metadata']))
        else:
            print "Unrecognized meta field (this indicates a parsing bug): %s" % mf
    return results


def parse_study_meta(metaEle):
    """
    dereferences the collection of meta elements into a dict; keys are NexSON
    vocabulary, not phylografter fields (hopefully reusable)
    """
    studytags = []
    result = {'other_metadata': []}
    for p in metaEle:
        if u'@property' in p:
            predicate = p[u'@property']
        elif u'@rel' in p:
            predicate = p[u'@rel']
        if predicate in [u'ot:studyYear',u'ot:focalClade']:
            result[predicate] = int(p[u'$'])
        elif predicate in [u'ot:studyPublication',u'ot:dataDeposit']:
            result[predicate] = encode(p[u'@href'])
        elif predicate in [u'ot:studyPublicationReference',u'ot:curatorName',u'ot:contributor',u'ot:specifiedRoot']:
            result[predicate] = encode(p[u'$'])
        elif predicate in [u'ot:tag']:
            studytags.append(encode(p[u'$']))
        elif predicate in [u'ot:studyId']:
            result[predicate] = encode(p[u'$'])
        else:
            result['other_metadata'].append(p)
    if len(studytags)>0:
        result['ot:tag']=studytags
    return (result)

def reserialize_json(p):
    import json
    # print "reserializing metadata %s " % str(p)
    testString = json.dumps(p)
    # print "testString length = %d" % len(testString)
    return p


def process_otus_element_sql(contents, results, db):
    """
    returns actions for otus element - currently just the list
    of actions for the contained otu elements.  Only sql specific
    because it calls an sql translator
    """
    otus_ele = contents[u'otus'] 
    otus_id = otus_ele[u'@id']
    otu_set = otus_ele[u'otu']
    for otu in otu_set:
        results = process_otu_element_sql(otu,results,db)
    return results

def process_otu_element_sql(otu, results, db):
    from sys import maxsize
    id = otu[u'@id']
    results.append(('otu','nexson_id',otu[u'@id']))
    meta_ele = otu[u'meta']
    if isinstance(meta_ele,dict):
        ottid,olabel,tbid,extra = process_otu_meta([meta_ele])
    else:
        ottid,olabel,tbid,extra = process_otu_meta(meta_ele)
    if ottid:  #redesign here?
        #query suppresses synonyms
        query_str = 'SELECT id FROM ottol_name WHERE uid = %d and parent_uid IS NOT NULL' % ottid
        query_result = db.executesql(query_str)
        #print "querystr is '%s', result is %s" % (query_str,query_result)
        if query_result:
            if len(query_result) == 1:
               ((internal_id,),) = query_result
            else:
                best_id = maxsize
                for item in query_result:
                    (r_id,) = item
                    if r_id < best_id:
                        best_id = r_id
                internal_id = best_id
            results.append(('otu','ottol_name',internal_id))  #need to do something special here
        else:
            print "bad ott id: %d" % ottid
    if olabel:
        results.append(('otu','label',olabel))
    if tbid:
        results.append(('otu','tb_nexml_id',tbid))
    return results

def process_otu_meta(meta_elements):
    """
    returns a tuple rather than a dict because two elements 
    are required with an optional third
    """
    ottid = None
    olabel = None
    tbid = None
    extra = []
    for p in meta_elements:
        prop = p[u'@property']
        if prop == u'ot:ottId':
            ottid = int(p[u'$'])
        elif prop == u'ot:ottolid': # 'ot:ottolid' is deprecated (10-2013)
            ottid = int(p[u'$'])
        elif prop == u'ot:originalLabel':
            olabel = encode(p[u'$'])
        elif prop == u'ot:treebaseOTUId':
            tbid = encode(p[u'$'])
        else:
            extra.append(p)
    return (ottid,olabel,tbid,extra)

def process_trees_element_sql(contents, results, db):
    """
    currently otus and the id for the trees block are thrown away
    as there is only one set of otus and one set of trees per study
    in phylografter (so the ids just reference the study id)
    """
    trees_ele = contents[u'trees']
    trees_id = trees_ele[u'@id']
    otus = trees_ele[u'@otus']
    tree_set = trees_ele[u'tree']
    for tree in tree_set:
        results = process_tree_element_sql(tree,results,db)
    return results

def process_tree_element_sql(tree, results, db):
    """
    Processes a tree element, including child 'node' and
    'edge' elements.  It generates a couple of sql updates
    followed by the updates generated by the nodes in the tree.
    Edge elements get parsed and dumped in a table which is referenced
    during node parsing
    """
    id = tree[u'@id']
    nodes = tree[u'node']
    edges = tree[u'edge'] 
    if u'meta' in tree:
        meta_ele = tree[u'meta']
    else:
        meta_ele = None
    if isinstance(meta_ele,dict):
        blmode,tags,ingroup,ctype = process_tree_meta([meta_ele])
    elif meta_ele:
        blmode,tags,ingroup,ctype = process_tree_meta(meta_ele)
    else:
        blmode,tags,ingroup,ctype = (None,[],None,None)
    results.append(('tree','nexson_id',id))
    if blmode:
        results.append(('tree','branch_lengths_represent',blmode))
    for tag in tags:
        results.append(('tree','tag',tag))
    if ingroup:
        results.append(('tree','in_group_clade',ingroup))
    if ctype:
        results.append(('tree','type',ctype))
    edge_table = make_edge_table(edges)
    for node in nodes:
        results = process_node_element_sql(node, edge_table, results, db)
    return results

#This maps element vocabulary for ot:branchLengthMode to valid
#strings in the phylografter database
blmode_map = {"ot:substitutionCount": "substitutions per site",
              "ot:changeCount": "character changes",
              "ot:time": "time (Myr)", #these
              "ot:years": "time (Myr)", #need attention
              "ot:bootstrapValues": "bootstrap values",
              "ot:posteriorSupport": "posterior support",
              "ot:other": None,       # needs attention
              "ot:undefined": None}   # needs attention

def process_tree_meta(meta_elements):
    """
    extracts 'meta' element children of a tree element
    returns tuple because only three types parsed
    """
    blmode = None
    tags = []
    ingroup = None
    ctype = None
    extra = []
    for p in meta_elements:
        prop = p[u'@property']
        if prop == u'ot:branchLengthMode':
            raw_mode = encode(p[u'$'])
            if raw_mode in blmode_map:
                blmode = blmode_map[raw_mode]
        elif prop == u'ot:tag':
            tags.append(encode(p[u'$']))
        elif prop == u'ot:inGroupClade':
            ingroup = encode(p[u'$'])
        elif prop == u'ot:curatedType':
            ctype = encode(p[u'$'])
        else:
            extra.append(p)
    return (blmode,tags,ingroup,ctype)

def process_node_element_sql(node, edge_table, results, db):
    """
    translates a node element into sequence of sql update tuples
    each tuple is 'node' followed by a field in the phylografter 
    snode table and a value.  Some mess because phylografter stores
    parent and branch length with the node and has no edge table
    """
    id = node[u'@id']
    if u'meta' in node:
        meta_ele = node[u'meta']
    else:
        meta_ele = None
    if isinstance(meta_ele,dict):
        extra = process_node_meta([meta_ele])
    elif meta_ele:
        extra = process_node_meta(meta_ele)
    else:
        extra = None
    results.append(('node','nexson_id',id))
    if u'@otu' in node:
        otu = node[u'@otu']
        results.append(('node','otu', otu))
    if id in edge_table:
       parent_link = edge_table[id]
       if u'@length' in parent_link:
           raw_length = parent_link[u'@length']
           results.append(('node','length',float(raw_length)))
       if u'@source' in parent_link:
           parent = parent_link[u'@source']
           #print "appending parent %s to node %s" %(parent,raw_id) 
           results.append(('node','parent',parent))
    return results

def process_node_meta(meta_elements):
    """
    This is basically a stub, especially since there are no currently
    defined meta elements for nodes, but this should handle any 
    unrecognized that appear.
    """
    extra = []
    for p in meta_elements:
        extra.append(p)
    return extra

def make_edge_table(edges):
    """
    edge_table is a dict that maps the child node of the edge
    to the dict representing the edge element.  This would break
    if DAG's or anything more general were needed, but phylografter
    currently doesn't
    """
    edge_table = {}
    for edge in edges:
        edge_table[edge[u'@target']] = edge
    return edge_table

nexson_elements = [u'@xmlns', u'@nexmljson',u'@about',
                   u'@generator',u'@id', u'@version',
                   u'meta',u'otus',u'trees']


sql_parse_methods = [process_meta_element_sql,
                     process_otus_element_sql,
                     process_trees_element_sql]

#stub to support parsing in other formats
target_parsers= {'sql': sql_parse_methods} #, 'bson': bson_parse_methods} 

def ingest_json_study(study,db,id):
    """
    Entry point -
       study is parsed JSON from a NexSON file
       db is DAL db to receive results of parse
       id if numeric is value to force for study id
    """
    from nexson_sql_update import sql_process
    target = sql_parse_methods
    target_parser_set = sql_parse_methods
    contents = study[u'nexml']
    results = []
    for parser in target_parser_set:
        results = parser(contents,results,db)
    if results:
        print "(ingest_json_study) recycle_id = %s" % id
        new_study = sql_process(results,db,id)
        return new_study
    else:
        raise(500,"NexSON study ingest failed")
