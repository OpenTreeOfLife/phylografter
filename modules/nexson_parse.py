#!/usr/bin/env python
# coding: utf8
from gluon import *


def parse_nexson(f,db):
    ''' f is a file-like object'''
    from json import load
    tree = load(f)
    return parse_nexml(tree,db)
    
#put this in one place so it can be turned off easily when the time comes    
def encode(str):
    return str.encode('ascii')
    
def process_meta_element_sql(contents, results, db):
    metaEle = contents[u'meta']
    studyid,studydoi,studyref,studyyear,studycurator,studydeposit,studyfocalclade,studytags = \
        parse_study_meta(metaEle)
    if studyid:
        results = [('study','id',studyid)]
    else:
        return results  #no id, nothing to do
    if studydoi:
        results.append(('study','doi',studydoi))
    if studyref:
        results.append(('study','citation',studyref))
    if studyyear:
        results.append(('study','year_published',studyyear))
    if studycurator:
        results.append(('study','contributor',studycurator))
    if studyfocalclade:
        results.append(('study','focal_clade',studyfocalclade))
    if studytags:
        for tag in studytags:
            results.append(('study_tag','tag',tag))    
    return results
    
def parse_study_meta(metaEle):
    studyid = None
    studydoi = None
    studyref = None
    studyyear = None
    studycurator = None
    studydeposit = None
    studyfocalclade = None
    studytags = []
    for p in metaEle:
        prop = p[u'@property']
        if prop == u'ot:studyId':
            studyid = int(p[u'$'])
        elif prop == u'ot:studyPublication':
            studydoi = encode(p[u'@href'])
        elif prop == u'ot:studyYear':
            studyyear = int(p[u'$'])
        elif prop == u'ot:studyPublicationReference':
            studyref = encode(p[u'$'])
        elif prop == u'ot:curatorName':
            studycurator = encode(p[u'$'])
        elif prop == u'ot:dataDeposit':
            studydeposit = encode(p[u'@href'])
        elif prop == u'ot:contributor':
            studycurator = encode(p[u'$'])
        elif prop == u'ot:dataDeposit':
            studydeposit = encode(p[u'@href'])
        elif prop == u'ot:tag':
            studytags.append(encode(p[u'$']))
        elif prop == u'ot:focalClade':
            studyfocalclade= int(p[u'$'])
    return (studyid,studydoi,studyref,studyyear,studycurator,studydeposit,studyfocalclade,studytags)


def process_otus_element_sql(contents, results, db):
    otus_ele = contents[u'otus']  #needed?
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
    if ottid:
        ottid_internal_row = db.ottol_name(uid = ottid)
        if ottid_internal_row:
           internal_id = ottid_internal_row.id
           results.append(('otu','ottolid',internal_id))  #need to do something special here
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
    results.append(('tree','id',int(id)))
    edge_table = make_edge_table(edges)
    for node in nodes:
        results = process_node_element_sql(node, edge_table, results, db)
    return results
    
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
    return results
        
def make_edge_table(edges):
    edge_table = {}
    for edge in edges:
        edge_table[edge[u'@target']] = edge
    return edge_table
    
def process_nexml_element_bson(contents, results, db):
    return None

def process_xmlns_element_bson(contents, results, db):
    return None
            
def process_nexmljson_element_bson(contents, results, db):
    return None

def process_about_element_bson(contents, results, db):
    return None
                
def process_generator_element_bson(contents, results, db):
    return None

def process_id_element_bson(contents, results, db):
    return None

def process_version_element_bson(contents, results, db):
    return None

def process_meta_element_bson(contents, results, db):
    return None

def process_otus_element_bson(contents, results, db):
    return None

def process_trees_element_bson(contents, results, db):
    return None
    
nexson_elements = [u'@xmlns', u'@nexmljson',u'@about',
                   u'@generator',u'@id', u'@version',
                   u'meta',u'otus',u'trees']

    
sql_parse_methods = [process_meta_element_sql,
                     process_otus_element_sql,
                     process_trees_element_sql]

bson_parse_methods = [process_nexml_element_bson,
                      process_xmlns_element_bson,
                      process_about_element_bson,
                      process_nexmljson_element_bson,
                      process_generator_element_bson,
                      process_id_element_bson,
                      process_version_element_bson,
                      process_meta_element_bson,
                      process_otus_element_bson,
                      process_trees_element_bson]

target_parsers= {'sql': sql_parse_methods, 'bson': bson_parse_methods} 
   
def parse_nexml(tree,db):
    from nexson_sql_update import sql_process
    if not u'nexml' in tree:
        raise SyntaxError
    target = determine_target(db)
    target_parser_set = target_parsers[target]
    results = {}
    contents = tree[u'nexml']
    for parser in target_parser_set:
        results = parser(contents,results,db)
    sql_process(results,db)
    return contents

def determine_target(db):
    #TODO infer whether sql or document store based on properties of db
    return 'sql'