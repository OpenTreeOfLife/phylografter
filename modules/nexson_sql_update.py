#!/usr/bin/env python
# coding: utf8
from gluon import *


def sql_process(actions, db, recycle_id):
    validate_actions(actions)
    study_id = -1
    tree_id = -1
    # print " (sql_process) recycle_id = %s" % recycle_id
    nexson_map = insert_new_rows(actions, db, recycle_id)
    db.commit()  # think this is necessary
    special_clades = collect_special_clades(actions)
    current_table = None
    sql_id = None
    current_row = {}
    new_tags = None
    for action in actions:
        table, field, value = action
        # print "Action is %s %s %s" % action
        # print "current row = %s" % str(current_row)
        if (field == 'nexson_id'):  # time to update the previous element
            # print "Only if current field is nexson_id"
            if current_table:
                # print "Need to be filling in a row here"
                if current_table in ['otu', 'tree']:
                    current_row['study'] = study_id
                elif current_table == 'node':
                    current_row['tree'] = tree_id
                # print "About to update: %s" % str(current_row)
                if sql_id is None:
                    assert current_table == 'annotation'
                    # hack to 'capture' study fields after an annotation
                    print "about to finish study with sql_id = %d and study_id = %d" % (sql_id, study_id)
                    finish_row(db, 'study', study_id, current_row, new_tags)
                elif current_table == 'study':
                    finish_row(db,
                               current_table,
                               study_id,
                               current_row,
                               new_tags)
                elif current_table == 'otu':
                    db.commit();   # slightly pathological
                    finish_row(db,
                               current_table,
                               sql_id,
                               current_row,
                               new_tags)
                else:
                    print "about to finish %s with sql_id = %d and study_id = %d" % (current_table, sql_id, study_id)
                    finish_row(db,
                               current_table,
                               sql_id,
                               current_row,
                               new_tags)
            if (table == 'study'):
                if recycle_id:
                    sql_id = recycle_id
                # print "Want to set sql_id to %s" % value
                elif (value[2] == '_'):
                    sql_id = int(value[3:])
                else:
                    sql_id = int(value)
            else:
                sql_id = nexson_map[value]
            current_row = dict()
            current_id = sql_id
            current_table = table
            new_tags = set()
            if (current_table == 'study'):
                study_id = sql_id
            elif (current_table == 'tree'):
                tree_id = sql_id
        elif (field == 'tag'):
            new_tags.add(value)
        elif (field == 'in_group_clade'):
            pass
        elif (field == 'dataDeposit'):
            if (table == 'study'):
                current_row['data_deposit'] = value
        else:
            current_row[field] = value
    # catch last record (probably node)
    finish_row(db,
               current_table,
               sql_id,
               current_row,
               new_tags)
    return finish_study(db, study_id)


def finish_study(db, study_id):
    restore_otu_mapping(db, study_id)
    return finish_trees(db, study_id)


# simple check, probably overkill
def validate_actions(actions):
    """
    checks that the first tuple in the actions list specifies
    the study's id
    """
    first_table, first_field, first_id = actions[0]
    assert first_table == 'study'
    assert first_field == 'nexson_id'


def finish_row(db, current_table, sql_id, current_row, new_tags):
    """
    """
    update_inserted_row(db, current_table, sql_id, current_row)
    if new_tags:
        update_tags(db, current_table, new_tags, sql_id)

NAMETABLEMAP = {'study': 'study',
                'study_tag': 'study_tag',
                'otu': 'otu',
                'tree': 'stree',
                'stree': 'stree',
                'node': 'snode',
                'snode': 'snode',
                'annotation': 'nexson_annotation'}


def get_sql_id(db, table, nexson_id):
    query = ('SELECT id FROM %s WHERE nexson_id = "%s" ' %
             (NAMETABLEMAP[table], nexson_id))
    id_results = db.executesql(query)
    if id_results:
        return id_results[0][0]


# annotation table is odd - no ids, so ignore web2py's id, use the study id
# note - if we decide in future to attach annotations to individual elements
# annotations will need to be special cased even more than they are already
def init_map(db):
    return {'study': db.study.id,
            'study_tag': db.study_tag.id,
            'otu': db.otu.id,
            'tree': db.stree.id,
            'node': db.snode.id,
            'annotation': db.nexson_annotation.study}


# should return true if existing row with matching id is compatible
def validate_row(db, table, id, ele_table):
    return True


def collect_special_clades(actions):
    return [action[2] for action in actions if special_clade_test(action)]


def special_clade_test(action):
    table, field, value = action
    return (table == 'tree' and field == 'in_group_clade')


def insert_new_rows(actions, db, recycle_id):
    action_gen = generate_actions(actions)
    update_obj = {}
    nexson_map = {}
    update_table = None
    dummy_counter = 0
    # print "recycle_id = %s" % recycle_id
    # print "Entering insert new rows"
    try:
        table, field, value = action_gen.next()
        while True:
            if usable_id(table, field):
                if ((table == 'study') and field == 'nexson_id' and recycle_id):
                    new_id = insert_new_study(db, value, recycle_id)
                    nexson_map[value]=new_id 
                    # value = recycle_id  may put this back later
                # print "table: %s, field %s, value %s" % (table, field, value)
                else:
                    update_table = table
                    update_id = value
                    update_obj = {field: update_id}
                    finish_update(db, update_table, update_id, nexson_map)
                action = action_gen.next()
                field = action[1]
                while not(usable_id(table, field)):
                    action = action_gen.next()
                    table, field, value = action
                table, field, value = action  # update for next record
            else:
                table, field, value = action_gen.next()
    except StopIteration:
        if update_table:
            sql_id = finish_update(db, update_table, update_id, nexson_map)
        return nexson_map


def usable_id(table, field):
    return (field == 'nexson_id')


def finish_update(db, table, nexson_id, nexson_map):
    # print ("About to insert new: table= %s, update_obj = %s, update_id = %s" %
    #       (str(update_table), str(update_obj), update_id))
    insert_new(db, table, nexson_id, nexson_map)


def generate_actions(actions):
    for action in actions:
        yield action


# this would be better with a lookup, but some tables need to be
# placated with dummy values
def insert_new(db, table, nexson_id, nexson_map):
    """
    """
    new_id = ''
    # maybe this should be 'interned', rather than generate - no id is saved
    if table == 'study_tag':
        return db.study_tag.insert()
    if table == 'study':
        # print "about to call insert new study: values = %s" % str(values)
        new_id = insert_new_study(db, nexson_id, None)
    if table == 'otu':
        new_id = insert_new_otu(db, nexson_id)
    if table == 'tree':
        new_id = insert_new_tree(db, nexson_id)
    if table == 'node':
        new_id = insert_new_node(db, nexson_id)
    if table == 'annotation':
        new_id = insert_new_annotation(db, nexson_id)
    nexson_map[nexson_id]=new_id 
    return 



def insert_new_study(db, nexson_id, recycle_id):
    if recycle_id:
        result = db.study.insert(id=recycle_id,
                                 nexson_id=nexson_id,
                                 doi='',
                                 citation='xxx',
                                 contributor="AAA")  
    else:
        result = db.study.insert(nexson_id=nexson_id,
                                 doi='',
                                 citation='xxx',
                                 contributor="AAA")  
    db.commit()
    return result

def insert_new_otu(db, nexson_id):
    return  db.otu.insert(nexson_id=nexson_id,label='')


def insert_new_tree(db, nexson_id):
    return db.stree.insert(nexson_id=nexson_id,contributor='',newick="(a,b):c",type="undefined")

def insert_new_node(db, nexson_id):
    return db.snode.insert(nexson_id=nexson_id,tree=None)


def insert_new_annotation(db, nexson_id):
    return db.nexson_annotation.insert(study=nexson_id)


LOOKUP_SQL_FIELDS = {"study": None,
                     "study_tag": None,
                     "otu": None,
                     "tree": None,
                     "node": ("otu", "parent"),
                     "annotation": None}

FIELD_TO_TABLE = {("node","otu"): "otu",
                  ("node","parent"): "node"}


def update_inserted_row(db, table, sql_id, row_data):
    import json
    print "Entering update inserted row with sql_id = %d" % sql_id
    for field in row_data:
        if field == 'nexson_id':
            pass
        elif field == 'other_metadata':
            token = row_data['other_metadata']
            ret = db(db.study.id == sql_id).validate_and_update(other_metadata=json.dumps(row_data['other_metadata']))
        else:
            resolved_data = row_data[field]
            if (table in LOOKUP_SQL_FIELDS):
                if LOOKUP_SQL_FIELDS[table] and field in LOOKUP_SQL_FIELDS[table]:
                    resolved_data = get_sql_id(db,FIELD_TO_TABLE[(table,field)],resolved_data)
            if resolved_data:
                if isinstance(resolved_data,basestring):
                    if resolved_data.find('"') == -1:
                        sqlstr = 'UPDATE %s SET %s = "%s" WHERE id = %d' % (NAMETABLEMAP[table],field,resolved_data,sql_id)
                        #print "*** " + sqlstr
                        #"updating %s field in table %s with id %d" % (field,NAMETABLEMAP[table],sql_id)
                        db.executesql(sqlstr)
                    else:   # need to use slower DAL methods
                        #tb = db[NAMETABLEMAP[table]]
                        #print "Updated field %s of table %s to %s using DAL" % (field,NAMETABLEMAP[table],sql_id)
                        db(db[NAMETABLEMAP[table]]._id==sql_id).update(**{field:resolved_data}) 
                else:
                    sqlstr = 'UPDATE %s SET %s = "%s" WHERE id = %d' % (NAMETABLEMAP[table],field,resolved_data,sql_id)
                    # print "** " + sqlstr
                    # print "updating %s field in table %s with id %d" % (field,NAMETABLEMAP[table],sql_id)
                    db.executesql(sqlstr)
    return sql_id


def find_tags(db, table, id):
    """
    returns set of rows of id records (from study_tag, or stree_tag as appropriate)
    """
    sqltable = NAMETABLEMAP[table]
    tags_table = get_tag_table(table)
    if tags_table:
        rows = db.executesql('SELECT tag from %s WHERE %s = %d' % (tags_table, NAMETABLEMAP[table], id))
        tags = [row[0][0] for row in rows]
        return set(tags)


def update_tags(db, table, tags, id):
    if table == 'study':
        for tag in tags:
            #print "tag is {0}".format(tag)
            rows = db.executesql(
                 'SELECT id FROM study_tag WHERE study = %d AND tag = "%s"' % (id, tag))
            #rows = db((db.study_tag.study == id) & (db.study_tag.tag == tag)).select()
            if not rows:  #only need to add new tags
                # print 'inserting study tag %s to study %d' % (tag,id)
                db.study_tag.insert(study=id, tag=tag)
    elif table == 'tree':
        for tag in tags:
            rows = db.executesql(
                 "SELECT id FROM stree_tag WHERE stree = %d AND tag = '%s'" % (id,tag))
            #rows = db((db.stree_tag.stree == id) & (db.stree_tag.tag == tag)).select()
            if not rows:  #only need to add new tags
                #print 'inserting tree tag %s to tree %d' % (tag,id)
                db.stree_tag.insert(stree=id, tag=tag)


def get_tag_table(table_name):
    if table_name in ('study','stree'):
        return table_name+'_tag'


def encode_annotation(value):
    """
    serializes the dictionary structure representing a 
    nexson (study) annotation back in textual json
    (might be worthwhile to zip compress the text as well)
    """
    import json
    import base64
    import zlib
    ej = json.JSONEncoder()
    jsonStr = ej.encode(value)
    checksum = zlib.adler32(jsonStr) & 0xffffffff
    zjson = zlib.compress(jsonStr)
    b64zjson = base64.b64encode(zjson)
    return (b64zjson, checksum)


def restore_otu_mapping(db, study_id):
    """
    restores mapping from otus to their mapped ot_names
    """
    otus_query = "SELECT id FROM otu WHERE study = %d" % study_id
    otus = db.executesql(otus_query)
    for otu_result in otus:
        assert len(otu_result) == 1
        otu = otu_result[0]
        otu_name_query = "SELECT ottol_name FROM otu WHERE id = %d " % otu
        ot_name_results = db.executesql(otu_name_query)
        assert len(ot_name_results) == 1
        ot_name = ot_name_results[0][0]
        if ot_name:
            accepted_uid_query = "SELECT accepted_uid FROM ottol_name WHERE id = %d" % ot_name
            accepted_uid_results = db.executesql(accepted_uid_query)
            if len(accepted_uid_results) == 1:
                accepted_uid = accepted_uid_results[0][0]
                if accepted_uid:
                    db.executesql("UPDATE otu SET ott_node = %d WHERE id = %d" % (accepted_uid, otu))

        
def finish_trees(db, study_id):
    """
    recomputes the binary indexing, retrieves ottol-based labels and regenerates
    the newick string for each tree in the study
    """
    trees = db.executesql("SELECT id FROM stree WHERE study = %d" % study_id)
    for tree_result in trees:
        tree = tree_result[0]
        db.commit()  # make sure everything is in before tree update
        index_nodes(db, tree)
        restore_labels(db, tree)
        restore_newick(db, tree)
    return study_id


def index_nodes(db, tree_id):
    """
    Reconstructs the next, back, and isleaf fields for each snode in the
    tree specified by tree_id
    """
    root_query = "SELECT id FROM snode WHERE (tree = %d) AND (parent IS NULL)"
    root_nodes = db.executesql(root_query % tree_id)
    assert len(root_nodes) == 1
    root = root_nodes[0]
    node_id = root[0]
    index_children(db, node_id, 0)


def index_children(db, id, n):
    """
    Recursive traversal of snodes in tree to assign nrxt, back, and isleaf for snodes
    below snode specified by id
    """
    n = n + 1
    primary_next = n
    cl = db.executesql("SELECT id FROM snode WHERE parent = %d" % id, as_dict="true")
    if cl:
        last_back = n
        for i, child in enumerate(cl):
            if (i > 0):
                n = last_back
            last_back = index_children(db, child.get('id'), n)
        next_back = last_back + 1
    else:
        next_back = n + 1
    primary_back = next_back
    if (primary_back == primary_next + 1):
        is_leaf = 'T'
    else:
        is_leaf = 'F'
    update = "UPDATE snode SET next=%d, back=%d, isleaf='%s' WHERE id = %d;"
    stmt = update  % (primary_next, primary_back, is_leaf, id)
    db.executesql(stmt)
    return next_back


def restore_labels(db, tree):
    """
    restores labels from otu taxa 
    """
    nodes_query = "SELECT id,otu FROM snode WHERE tree = %s AND otu IS NOT NULL"
    nodes = db.executesql(nodes_query % tree)
    for (id, otu) in nodes:
        ((olabel, ), ) = db.executesql("SELECT label FROM otu WHERE otu.id = %d" % otu)
        if olabel.find("'") != -1:
            olabel = "".join(olabel.split("'"))
        db.executesql("UPDATE snode SET label = '%s' WHERE id = %d" % (olabel, id))


def restore_newick(db, tree):
    """
    return newick string for specified tree.  Simplified version of
    code in stree controller, which assumes context (e.g., request.vars
    and global definition of db) not available in a module.   Simplified the
    leaf and internal node format code.
    """
    import build
    treeid = tree
    root = build.stree(db, treeid)
    lfmt = [x.split('.') for x in 'snode.id,otu.label'.split(',')]

    def proc(node, table, field):
        try: 
            s = str(getattr(getattr(node.rec, table), field))
        except AttributeError: 
            s = ''
        return "".join('_'.join(s.split()).split("'"))
    for n in root:
        n.label = ''
        if n.isleaf:
            n.label = '_'.join([proc(n, t, f) for t, f in lfmt])
        else:
            pass
        n.label = n.label.replace('(', '--').replace(')', '--')
    newick_str = root.write()
    db.executesql("UPDATE stree SET newick = '%s' WHERE id = %d" %
                  (newick_str, tree))
