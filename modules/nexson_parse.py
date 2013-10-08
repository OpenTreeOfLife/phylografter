#!/usr/bin/env python
# coding: utf8
from gluon import *


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
    metaEle = contents[u'meta']
    metafields = parse_study_meta(metaEle)
    if 'studyid' in metafields:
        results = [('study','id',metafields['studyid'])]
    else:
        return results  #no id, nothing to do
    if 'studydoi' in metafields:
        results.append(('study','doi',metafields['studydoi']))
    if 'studyref' in metafields:
        results.append(('study','citation',metafields['studyref']))
    if 'studyyear' in metafields:
        results.append(('study','year_published',metafields['studyyear']))
    if 'studycurator' in metafields:
        results.append(('study','contributor',metafields['studycurator']))
    if 'studyfocalclade' in metafields:
        results.append(('study','focal_clade',metafields['studyfocalclade']))
    if 'studytags' in metafields:
        for tag in metafields['studytags']:
            results.append(('study','tag',tag))    
    return results
    
def parse_study_meta(metaEle):
    studytags = []
    result = {}
    for p in metaEle:
        prop = p[u'@property']
        if prop == u'ot:studyId':
            result['studyid'] = int(p[u'$'])
        elif prop == u'ot:studyPublication':
            result['studydoi'] = encode(p[u'@href'])
        elif prop == u'ot:studyYear':
            result['studyyear'] = int(p[u'$'])
        elif prop == u'ot:studyPublicationReference':
            result['studyref'] = encode(p[u'$'])
        elif prop == u'ot:curatorName':
            result['studycurator'] = encode(p[u'$'])
        elif prop == u'ot:dataDeposit':
            result['studydeposit'] = encode(p[u'@href'])
        elif prop == u'ot:contributor':
            result['studycurator'] = encode(p[u'$'])
        elif prop == u'ot:dataDeposit':
            result['studydeposit'] = encode(p[u'@href'])
        elif prop == u'ot:tag':
            studytags.append(encode(p[u'$']))
        elif prop == u'ot:focalClade':
            result['studyfocalclade']= int(p[u'$'])
    if len(studytags)>0:
        result['studytags']=studytags
    return (result)


def process_otus_element_sql(contents, results, db):
    """
    returns actions for otus element - currently just the list
    of actions for the contained otu elements
    """
    otus_ele = contents[u'otus'] 
    otus_id = otus_ele[u'@id']
    otu_set = otus_ele[u'otu']
    for otu in otu_set:
        results = process_otu_element_sql(otu,results,db)
    return results
    
def process_otu_element_sql(otu, results, db):
    id = otu[u'@id']
    if id.startswith('otu'):
        id = id[3:]
    results.append(('otu','id',int(id)))
    meta_ele = otu[u'meta']
    ottid = None
    olabel = None
    if isinstance(meta_ele,dict):
        ottid,olabel = process_otu_meta([meta_ele])
    else:
        ottid,olabel = process_otu_meta(meta_ele)
    if ottid:  #redesign here?
        query_str = 'SELECT id FROM ottol_name WHERE uid = %d' % ottid
        internal_id = db.executesql(query_str)
        #print "querystr is '%s', result is %s" % (query_str,internal_id)
        if internal_id:
           results.append(('otu','ottol_name',internal_id[0][0]))  #need to do something special here
        else:
            print "bad ott id: %d" % ottid
    if olabel:
        results.append(('otu','label',olabel))
    return results
    
def process_otu_meta(meta_elements):
    ottid = None
    olabel = None
    for p in meta_elements:
        prop = p[u'@property']
        if prop == u'ot:ottolid':
            ottid = int(p[u'$'])
        elif prop == u'ot:ottid':
            ottid = int(p[u'$'])
        elif prop == u'ot:originalLabel':
            olabel = encode(p[u'$'])
    return (ottid,olabel)    

def process_trees_element_sql(contents, results, db):
    trees_ele = contents[u'trees']
    trees_id = trees_ele[u'@id']
    otus = trees_ele[u'@otus']
    tree_set = trees_ele[u'tree']
    for tree in tree_set:
        results = process_tree_element_sql(tree,results,db)
    return results

def process_tree_element_sql(tree, results, db):
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
        blmode,tags,ingroup = process_tree_meta([meta_ele])
    elif meta_ele:
        blmode,tags,ingroup = process_tree_meta(meta_ele)
    else:
        blmode,tags,ingroup = (None,[],None)
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


blmode_map = {"ot:substitutionCount": "substitutions per site",
              "ot:changeCount": "character changes",
              "ot:time": "time (Myr)", #these
              "ot:years": "time (Myr)", #need attention
              "ot:bootstrapValues": "bootstrap values",
              "ot:posteriorSupport": "posterior support",
              "ot:other": None,       # needs attention
              "ot:undefined": None}   # needs attention


def process_tree_meta(meta_elements):
    blmode = None
    tags = []
    ingroup = None
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
    return (blmode,tags,ingroup)    



def process_node_element_sql(node, edge_table, results, db):
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
           parent = parent_link[u'@length']
           results.append(('node','parent',int(parent)))    
    return results
        
def make_edge_table(edges):
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


target_parsers= {'sql': sql_parse_methods} #, 'bson': bson_parse_methods} 
   
def parse_nexml(tree,db):
    from nexson_sql_update import sql_process
    if not u'nexml' in tree:
        raise SyntaxError
    target = determine_target(db)
    target_parser_set = target_parsers[target]
    contents = tree[u'nexml']
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
