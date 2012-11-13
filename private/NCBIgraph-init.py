"""
Instructions:

1. Put this script in a directory that contains names.dmp and
   nodes.dmp from NCBI.

2. Set your CLASSPATH to include the neo4j libs:

   export CLASSPATH=$NEO4J_HOME/lib/neo4j-kernel-1.8.jar:$NEO4J_HOME/lib/server-api-1.8.jar:$NEO4J_HOME/lib/geronimo-jta_1.1_spec-1.1.1.jar:$NEO4J_HOME/lib/lucene-core-3.5.0.jar:$NEO4J_HOME/lib/neo4j-lucene-index-1.8.jar

3. Run with jython and lots of memory, e.g.

   jython -J-Xmx5000M NCBIgraph-init.py

4. Set your neo4j server to point to the new database ('./ncbi.db' by
   default).
"""

import sys, pprint
from collections import defaultdict, OrderedDict
from itertools import izip_longest, ifilter
from org.neo4j.unsafe.batchinsert import BatchInserters as Batch
from org.neo4j.unsafe.batchinsert import LuceneBatchInserterIndexProvider
from org.neo4j.graphdb import DynamicRelationshipType

NAME_OF = DynamicRelationshipType.withName('NCBI_NAME_OF')
CHILD_OF = DynamicRelationshipType.withName('NCBI_CHILD_OF')

DBNAME = 'ncbi.db'
db = Batch.inserter(DBNAME, {'neostore.nodestore.db.mapped_memory': '4096M'})
idx = LuceneBatchInserterIndexProvider(db)
ncbi_node_idx = idx.nodeIndex('ncbi_node', {'type':'exact'})
ncbi_name_idx = idx.nodeIndex('ncbi_name', {'type':'exact'})
ncbi_unique_name_idx = idx.nodeIndex('ncbi_unique_name', {'type':'fulltext'})

node_fields = ["taxid", "parent_taxid", "rank", "embl_code", "division_id",
               "inherited_div_flag", "genetic_code_id", "inherited_gc_flag",
               "mt_gc_id", "inherited_mgc_flag", "genbank_hidden_flag",
               "hidden_subtree_root_flag", "comments"]
name_fields = ["taxid", "name", "unique_name", "name_class"]

def batch(iterable, n=100000):
    args = [iter(iterable)]*n
    return izip_longest(fillvalue=None, *args)

def process_nodes():
    print 'processing nodes'
    i = 0
    taxid2data = {}
    child2parent = {}
    with open('nodes.dmp') as f:
        for line in f:
            v = [ x.strip() or None for x in line.split("|") ]
            data = dict(zip(node_fields, v[:-1]))
            for k, v in data.items():
                if k.endswith('_flag'):
                    data[k] = bool(int(v))
                else:
                    try: data[k] = int(v)
                    except: pass
            tid = data['taxid']
            taxid2data[tid] = data
            if tid > 1: child2parent[tid] = data['parent_taxid']
            i += 1
            if (i % 100000 == 0): print i
    print 'done'
    return taxid2data, child2parent

def process_names(taxid2data):
    print 'processing names'
    i = 0
    seen = set()
    names = defaultdict(list)
    with open('names.dmp') as f:
        for line in f:
            v = [ x.strip() or None for x in line.split("|") ]
            v[0] = int(v[0])
            s = dict(zip(name_fields, v[:-1]))
            taxid = s['taxid']; name = s['name']
            s['type'] = 'taxonomic_name'
            s['source'] = 'ncbi'
            if s['unique_name'] or name in seen: s['homonym_flag'] = True
            seen.add(name)
            if s['name_class'] == 'scientific name':
                taxid2data[taxid]['name'] = name
            names[taxid].append(s)
            i += 1
            if i % 100000 == 0: print i
    print 'done'
    return names

def insert(taxid2data, child2parent, names):
    print 'inserting nodes'
    taxid2node = {}
    total = len(taxid2data)
    b = batch(taxid2data)
    i = 0
    for x in b:
        for taxid in ifilter(None, x):
            data = taxid2data[taxid]
            data['type'] = 'ncbi_node'
            for key in [ k for k in data if data[k] is None ]: del data[key]
            n = db.createNode(data)
            taxid2node[taxid] = n
            ncbi_node_idx.add(n, {'taxid': taxid})
            i += 1
                
        print 'inserted %s/%s nodes' % (i, total)

    print 'inserting names'
    total = len(names)
    b = batch(names)
    i = 0
    for x in b:
        for taxid in ifilter(None, x):
            ## v = synonyms[taxid]
            v = names[taxid]
            for data in v:
                for key in [ k for k in data if data[k] is None ]: del data[key]
                data['type'] = 'ncbi_name'
                n = db.createNode(data)
                db.createRelationship(n, taxid2node[taxid], NAME_OF, None)
                name = data['name']
                unique_name = data.get('unique_name') or data['name']
                ncbi_name_idx.add(n, {'name': name})
                ncbi_node_idx.add(taxid2node[taxid], {'name': name})
                ncbi_unique_name_idx.add(n, {'unique_name': unique_name})
            i += 1
        print 'inserted %s/%s names' % (i, total)

    print 'inserting parent-child edges'
    total = len(child2parent)
    b = batch(child2parent)
    i = 0
    for x in b:
        for taxid in ifilter(None, x):
            ptid = child2parent[taxid]
            c = taxid2node[taxid]
            p = taxid2node[ptid]
            db.createRelationship(c, p, CHILD_OF, None)
            i += 1
        print 'processed %s/%s children' % (i, total)

taxid2data, child2parent = process_nodes()
names = process_names(taxid2data)
insert(taxid2data, child2parent, names)
    
idx.shutdown()
db.shutdown()
