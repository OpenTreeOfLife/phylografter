#!/usr/bin/env python
# coding: utf8
from gluon import *
from sys import maxsize


def parse_nexson(f,db):
    """
    Entry point - nexson is parsed and dispatched to the appropriate updater
    f - file like object (generally a CStringIO, retrieved from a post)
    db - web2py database object
    """
    from json import load
    tree = load(f)
    return parse_nexml(tree,db)

#put this in one place so it can be turned off easily when the time comes
def encode(str):
    return str  #.encode('ascii')

def process_meta_element_sql(contents, results, db):
    """
    Builds the list of database updates corresponding to the study
    element's child 'meta' elements.  Each tuple added to results 
    should contain study (the table), a valid field in the study table,
    and an appropriate value.  Note that this is mapping Nexson vocabulary
    to phylografter fields (should happen here and similar functions below)
    """
    metaEle = contents[u'meta']
    metafields = parse_study_meta(metaEle)
    if 'ot:studyId' in metafields:
        results = [('study','id',metafields['ot:studyId'])]
    else:
        return results  #no id, nothing to do
    if 'ot:studyPublication' in metafields:
        results.append(('study','doi',metafields['ot:studyPublication']))
    if 'ot:studyPublicationReference' in metafields:
        results.append(('study','citation',metafields['ot:studyPublicationReference']))
    if 'ot:studyYear' in metafields:
        results.append(('study','year_published',metafields['ot:studyYear']))
    if 'ot:curatorName' in metafields:
        results.append(('study','contributor',metafields['ot:curatorName']))
    if 'ot:focalClade' in metafields:
        results.append(('study','focal_clade_ottol',metafields['ot:focalClade']))
    if 'ot:dataDeposit' in metafields:
        results.append(('study','dataDeposit',metafields['ot:dataDeposit']))
    if 'ot:annotation' in metafields:
        results.append(('study','annotation',metafields['ot:annotation']))
    if 'ot:tag' in metafields:
        for tag in metafields['ot:tag']:
            results.append(('study','tag',tag))
    return results

def parse_study_meta(metaEle):
    """
    dereferences the collection of meta elements into a dict; keys are NexSON
    vocabulary, not phylografter fields (hopefully reusable)
    """
    studytags = []
    result = {}
    for p in metaEle:
        prop = p[u'@property']
        if prop == u'ot:studyId':
            result['ot:studyId'] = int(p[u'$'])
        elif prop == u'ot:studyPublication':
            result['ot:studyPublication'] = encode(p[u'@href'])
        elif prop == u'ot:studyYear':
            result['ot:studyYear'] = int(p[u'$'])
        elif prop == u'ot:studyPublicationReference':
            result['ot:studyPublicationReference'] = encode(p[u'$'])
        elif prop == u'ot:curatorName':
            result['ot:curatorName'] = encode(p[u'$'])
        elif prop == u'ot:dataDeposit':
            result['ot:dataDeposit'] = encode(p[u'@href'])
        elif prop == u'ot:contributor':
            result['ot:contributor'] = encode(p[u'$'])
        elif prop == u'ot:dataDeposit':
            result['ot:dataDeposit'] = encode(p[u'@href'])
        elif prop == u'ot:tag':
            studytags.append(encode(p[u'$']))
        elif prop == u'ot:focalClade':
            result['ot:focalClade'] = int(p[u'$'])
        elif prop == u'ot:specifiedRoot':
            result['ot:specifiedRoot'] = encode(p[u'$'])
        elif prop == u'ot:annotation':
            result['ot:annotation'] = process_annotation_metadata(p)
    if len(studytags)>0:
        result['ot:tag']=studytags
    return (result)

def process_annotation_metadata(p):
    import json
    #print "Entering annotation %s " % p[u'$']
    #print "Author: %s" % p['author']
    #print "isValid: %s" % p['isValid']
    #print "id: %s" % p['id']
    #print "date created: %s" % p['dateCreated']
    if 'dateModified' in p:
        print "date modified: %s" % p['dateModified']
    #print "Messages: %s" % str(p['messages'])
    print "About to test json.dumps"
    testString = json.dumps(p)
    print "testString length = %d" % len(testString)
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
    if id.startswith('otu'):
        id = id[3:]
    results.append(('otu','id',int(id)))
    meta_ele = otu[u'meta']
    if isinstance(meta_ele,dict):
        ottid,olabel,tbid = process_otu_meta([meta_ele])
    else:
        ottid,olabel,tbid = process_otu_meta(meta_ele)
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
    return (ottid,olabel,tbid)

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
    if id.startswith('tree'):
        id = id[4:]
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
    results.append(('tree','id',int(id)))
    if blmode:
        results.append(('tree','branch_lengths_represent',blmode))
    for tag in tags:
        results.append(('tree','tag',tag))
    if ingroup:
        results.append(('tree','in_group_clade',ingroup))
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
    return (blmode,tags,ingroup,ctype)    

def process_node_element_sql(node, edge_table, results, db):
    """
    translates a node element into sequence of sql update tuples
    each tuple is 'node' followed by a field in the phylografter 
    snode table and a value.  Some mess because phylografter stores
    parent and branch length with the node and has no edge table
    """
    raw_id = node[u'@id']
    if raw_id.startswith('node'):
        id = raw_id[4:]
    else:
        id = raw_id
    results.append(('node','id',int(id)))
    if u'@otu' in node:
        otu = node[u'@otu']
        if otu.startswith('otu'):
            otu = otu[3:]
        results.append(('node','otu',int(otu)))
    if raw_id in edge_table:
       parent_link = edge_table[raw_id]
       if u'@length' in parent_link:
           raw_length = parent_link[u'@length']
           results.append(('node','length',float(raw_length)))
       if u'@source' in parent_link:
           parent = parent_link[u'@source']
           if parent.startswith('node'):
               parent = parent[4:]
           #print "appending parent %s to node %s" %(parent,raw_id) 
           results.append(('node','parent',int(parent)))    
    return results

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

def parse_nexml(study,db):
    """
    Entry point -
       study is parsed JSON from a NexSON file
       db is DAL db to receive results of parse
    """
    from nexson_sql_update import sql_process
    if not u'nexml' in study:
        raise SyntaxError
    target = determine_target(db)
    target_parser_set = target_parsers[target]
    contents = study[u'nexml']
    results = []
    for parser in target_parser_set:
        results = parser(contents,results,db)
    if results:
        new_study = sql_process(results,db)
        return new_study
    else:
        raise(500,"NexSON study ingest failed")

def determine_target(db):
    #TODO infer whether sql or document store based on properties of db
    return 'sql'
