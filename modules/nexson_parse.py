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
    studyid = None
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
            studydeposit = encode(p[u'$'])
        elif prop == u'ot:contributor':
            studycurator = encode(p[u'$'])
    existingRows = db.study[studyid]
    if existingRows:
        results['update'] = []
        actionList = results['update']
        print 'Study %d already in database, will update' % studyid
    else:
        results['add'] = []
        actionList = results['add']
    actionList.append(('study','id',studyid))
    actionList.append(('study','doi',studydoi))
    actionList.append(('study','citation',studyref))
    actionList.append(('study','year_published',studyyear))
    actionList.append(('study','contributor',studycurator))
    return results

def process_otus_element_sql(contents, results, db):
    otus_ele = contents[u'otus']  #needed?
    otus_id = otus_ele[u'@id']
    otu_set = otus_ele[u'otu']
    for otu in otu_set:
        results = process_otu_element_sql(otu,results,db)
    return results
    
def process_otu_element_sql(otu, results, db):
    if 'update' in results:
        actionList = results['update']
    else:
        actionList = results['add']
    id = otu[u'@id']
    if id.startswith('otu'):
        id = id[3:]
    actionList.append(('otu','id',int(id)))
    meta_ele = otu[u'meta']
    ottid = None
    olabel = None
    for p in meta_ele:
        prop = p[u'@property']
        if prop == u'ot:ottolid':
            ottid = int(p[u'$'])
        if prop == u'ot:ottid':
            ottid = int(p[u'$'])
        elif prop == u'ot:originalLabel':
            olabel = encode(p[u'$'])
    if ottid:
        ottid_internal_row = db.ottol_name(uid = ottid)
        if ottid_internal_row:
           internal_id = ottid_internal_row.id
           actionList.append(('otu','ottolid',internal_id))  #need to do something special here
        else:
            print "bad ott id: %d" % ottid
    return results

def process_trees_element_sql(contents, results, db):
    trees_ele = contents[u'trees']
    trees_id = trees_ele[u'@id']
    otus = trees_ele[u'@otus']
    tree_set = trees_ele[u'tree']
    for tree in tree_set:
        results = process_tree_element_sql(tree,results,db)
    return results

def process_tree_element_sql(tree, results, db):
    if 'update' in results:
        actionList = results['update']
    else:
        actionList = results['add']
    id = tree[u'@id']
    if id.startswith('tree'):
        id = id[4:]
    nodes = tree[u'node']
    edges = tree[u'edge'] 
    actionList.append(('tree','id',int(id)))
    edge_table = make_edge_table(edges)
    for node in nodes:
        results = process_node_element_sql(node, edge_table, results, db)
    return results
    
def process_node_element_sql(node, edge_table, results, db):
    if 'update' in results:
        actionList = results['update']
    else:
        actionList = results['add']
    raw_id = node[u'@id']
    if raw_id.startswith('node'):
        id = raw_id[4:]
    else:
        id = raw_id
    actionList.append(('node','id',int(id)))
    if u'@otu' in node:
        otu = node[u'@otu']
        if otu.startswith('otu'):
            otu = otu[3:]
        actionList.append(('node','otu',int(otu)))
    if raw_id in edge_table:
       parent_link = edge_table[raw_id]
       if u'@length' in parent_link:
           raw_length = parent_link[u'@length']
           actionList.append(('node','length',float(raw_length)))
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
    if not u'nexml' in tree:
        raise SyntaxError
    target = determine_target(db)
    target_parser_set = target_parsers[target]
    results = {}
    contents = tree[u'nexml']
    for parser in target_parser_set:
        results = parser(contents,results,db)
        print "After %s, results is %s" % (str(parser),str(results))
    return contents

def determine_target(db):
    #TODO infer whether sql or document store based on properties of db
    return 'sql'
