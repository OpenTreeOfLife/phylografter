#!/usr/bin/env python
# coding: utf8
from gluon import *


def sql_process(actions, db):
    validate_actions(actions)
    study_id = -1
    tree_id = -1
    ele_table_map = init_map(db)
    fixup_table = insert_new_rows(actions,db)
    db.commit()  # think this is necessary
    special_clades = collect_special_clades(actions)
    current_row = None
    for action in actions:
        table,field,value = action
        #print "Action is %s %s %s", action
        if (field == 'id'):  #time to update the previous element
            if current_row:
                if current_table in ['otu','tree']:
                    current_row['study']= study_id
                elif current_table == 'node':
                    current_row['tree'] = tree_id
                    if current_row.id in special_clades:
                        current_row['ingroup'] = True
                print "About to update: %s" % str(current_row)
                current_row.update_record()
                if new_tags:
                    update_tags(db,current_table,new_tags,current_row.id)
            current_table = table
            if (current_table,value) in fixup_table:
                current_id = fixup_table[(current_table,value)]
            else:
                current_id = value
            current_row = find_row(db,current_table,current_id,ele_table_map)
            if (current_row is None):
                print "id %d in table %s failed to retrieve a row" % (current_id,current_table)
            #print 'retrieved %s' % str(current_row)
            new_tags = set()
            old_tags = find_tags(db,current_table,current_id)
            if old_tags:
                #print "%s old tag count = %d" % (current_table,len(old_tags))
                remove_old_tags(db,current_table,old_tags,current_id)
            if (current_table == 'study'):
                study_id = current_id
            elif (current_table == 'tree'):
                tree_id = current_id
        elif (field == 'tag'):
            #print "found tag %s" % value
            new_tags.add(value)
        elif (field == 'in_group_clade'):
            pass
        elif (field == 'annotation'):
            current_row['raw_contents'] = encode_annotation(value)
        else:
            if current_row:
                if (table == 'study' and field=='dataDeposit'):
                    current_row['data_deposit'] = value
                elif (table == 'study' and field=='contributor'):
                    current_row['study_contributor'] = value
                else:
                    current_row[field] = value
    return finish_trees(db,study_id)  


#simple check, probably overkill
def validate_actions(actions):
    """
    checks that the first tuple in the actions list specifies the study's id
    """
    first_table,first_field,first_id= actions[0]
    if (first_table != 'study' or first_field != 'id'):
        print "actions[0] = %s,%s,%s\n" % actions[0]
        print "actions[1] = %s,%s,%s\n" % actions[1]
        raise HTTP(400,"Head of nexson file was not a study identifier - exiting")


#annotation table is odd - no ids, so ignore web2py's id, use the study id
#note - if we decide in future to attach annotations to individual elements
#annotations will need to be special cased even more than they are already 
def init_map(db):
    return {'study': db.study.id,
            'study_tag': db.study_tag.id,
            'otu': db.otu.id,
            'tree': db.stree.id,
            'node': db.snode.id,
            'annotation': db.nexson_annotation.study}

NAMETABLEMAP={'study': 'study',
              'study_tag': 'study_tag',
              'otu': 'otu',
              'tree': 'stree',
              'stree': 'stree',
              'node': 'snode',
              'snode': 'snode',
              'annotation': 'nexson_annotation'}

def find_row(db, table,id,ele_table):
    rows = db(ele_table[table] == id)
    if rows:
        return rows.select().first()
    else:
        return None

# should return true if existing row with matching id is compatible                
def validate_row(db, table,id,ele_table):
    return True

def collect_special_clades(actions):
    return [action[2] for action in actions if special_clade_test(action)]    

def special_clade_test(action):
    table,field,value = action
    return (table == 'tree' and field == 'in_group_clade')
    
def insert_new_rows(actions, db):
    ele_table_map = init_map(db)
    action_gen = generate_actions(actions)
    update_obj = {}
    fixup_table = {}
    update_table = None
    dummy_counter = 0
    try:
        table,field,value = action_gen.next()
        while True:
            if (field == 'id'):
                #print "loop check: %s, field %s, value %s" % (table,field,value)
                current_row = find_row(db,table,value,ele_table_map)
                if current_row is None:
                    update_table = table
                    update_id = value
                    update_obj = {}
                    action = action_gen.next()
                    field = action[1]
                    while not(field == 'id'):
                        table,field,value = action
                        if immediately_updateable(table,field):
                            update_obj[field] = value
                        action = action_gen.next()
                        field = action[1]
                    table,field,value = action # update for next record
                    finish_update(db,update_table,update_obj,update_id,fixup_table)
                else:
                    table,field,value = action_gen.next()
            else:
                table,field,value = action_gen.next()
    except StopIteration:
        if update_table:
            finish_update(db,update_table,update_obj,update_id,fixup_table)
        return fixup_table

def finish_update(db,update_table,update_obj,update_id,fixup_table):
    #print "About to update: table= %s, update_obj = %s, update_id = %d" % (str(update_table),str(update_obj),update_id)
    new_id = insert_new(db,update_table,update_obj,update_id)
    #print "just updated, update_table is %s, new_id is %d" % (str(update_table),new_id)
    if new_id > 0: # if restore to original id works, no need to add to fixup
        fixup_table[(update_table,update_id)] = new_id

def generate_actions(actions):
    for action in actions:
        yield action

#wish could do this with a lookup, but some tables need to be placated with dummy values
def insert_new(db,table,values,old_id=None):
    #print "Entering insert_new: %s,%s,%d" % (table,values,old_id)
    if table=='study':
        return insert_new_study(db,values,old_id)
    if table=='study_tag':  #maybe this should be interned, rather than generate - no id is saved
        return db.study_tag.insert()
    if table=='otu':
        return insert_new_otu(db,values,old_id)
    if table=='tree':
        return insert_new_tree(db,values,old_id)
    if table=='node':
        return insert_new_node(db,values,old_id)
    if table=='annotation':
        return insert_new_annotation(db,values,old_id)

def insert_new_study(db,values,old_id):
    if 'citation' in values and 'contributor' in values:
        if old_id:
            #new_id = db.study.insert(id=old_id,citation=values['citation'],contributor=values['contributor'])
            citation_clean = "'".join(values['citation'].split('"'))
            contrib_clean = "'".join(values['contributor'].split('"'))
            sqlstr = 'INSERT INTO study (id,citation,contributor) VALUES (%s, "%s", "%s")' % (old_id,citation_clean,contrib_clean)
            db.executesql(sqlstr)
            new_id = old_id
        else:
            citation_clean = "'".join(values['citation'].split('"'))
            contrib_clean = "'".join(values['contributor'].split('"'))
            sqlstr = 'INSERT INTO study (citation,contributor) VALUES ("%s", "%s")' % (citation_clean,contrib_clean)
            db.executesql(sqlstr)
            sqlstr = 'SELECT max(id) FROM study'
            id_result = db.executesql(sqlstr)
            if id_result:
                new_id = int(id_result[0])
            else:
                new_id = None
        return new_id

def insert_new_otu(db,values,old_id):
    if 'label' in values:
        #print "otu label is {0}".format(values['label'])
        if old_id:
            sqlstr = 'INSERT INTO otu (id,label) VALUES (%s, "%s")' % (old_id,values['label'])
            db.executesql(sqlstr)
            return old_id
        else:
            sqlstr = 'INSERT INTO otu (label) VALUES ("%s")' % values['label']
            db.executesql(sqlstr)
            sqlstr = 'SELECT max(id) FROM study'
            id_result = db.executesql(sqlstr)
            return id_result

def insert_new_tree(db,values,old_id):
    if 'contributor' in values:
        if old_id:
            sqlstr = 'INSERT INTO stree (id,contributor,newick) VALUES (%s, "%s","")' % (old_id,values['contributor'])
            db.executesql(sqlstr)
            return old_id
        else:
            sqlstr = 'INSERT INTO stree (contributor,newick) VALUES ("%s","")' % values['contributor']
            db.executesql(sqlstr)
            sqlstr = 'SELECT max(id) FROM study'
            id_result = db.executesql(sqlstr)
            return id_result
    else:
        if old_id:
            sqlstr = 'INSERT INTO stree (id,contributor,newick) VALUES (%s, "", "")' % (old_id)
            db.executesql(sqlstr)
            return old_id
        else:
            sqlstr = 'INSERT INTO stree (contributor,newick) VALUES ("","")'
            db.executesql(sqlstr)
            sqlstr = 'SELECT max(id) FROM study'
            id_result = db.executesql(sqlstr)
            return id_result


def insert_new_node(db,values,old_id):
    if old_id:
        sqlstr = 'INSERT INTO snode (id,tree) VALUES (%s, NULL)' % old_id
        db.executesql(sqlstr)
        return old_id
    else:
        sqlstr = 'INSERT INTO snode (tree) VALUES (NULL)'
        db.executesql(sqlstr)
        sqlstr = 'SELECT max(id) FROM study'
        id_result = db.executesql(sqlstr)
        return id_result

def insert_new_annotation(db,values,study_id):
    sqlstr = 'INSERT INTO nexson_annotation (study) VALUES (%s)' % study_id
    db.executesql(sqlstr)
    sqlstr = 'SELECT max(id) FROM study'
    id_result = db.executesql(sqlstr)
    return id_result


IMMEDIATELY_UPDATEABLE_TABLE = {"study": ("citation","contributor"),
                                "study_tag": None,
                                "otu": ("label",),
                                "tree": ("contributor","newick","type"),
                                "node": None,
                                "annotation": None}   ##this is pessimistic as long as we don't interpret annotations

def immediately_updateable(table,value):
    if IMMEDIATELY_UPDATEABLE_TABLE[table]:
        return value in IMMEDIATELY_UPDATEABLE_TABLE[table]
    else:
        return False

def find_tags(db,table,id):
    """
    returns set of rows of id records (from study_tag, or stree_tag as appropriate)
    """
    sqltable = NAMETABLEMAP[table]
    tags_table = get_tag_table(table)
    if tags_table:
        rows = db.executesql('SELECT tag from %s WHERE %s = %d' % (tags_table,NAMETABLEMAP[table],id))
        tags = [row[0][0] for row in rows]
        return set(tags)

def update_tags(db,table,tags,id):
    if table == 'study':
        for tag in tags:
            #print "tag is {0}".format(tag)
            rows = db.executesql(
                 'SELECT id FROM study_tag WHERE study = %d AND tag = "%s"' % (id,tag))
            #rows = db((db.study_tag.study == id) & (db.study_tag.tag == tag)).select()
            if not rows:  #only need to add new tags
                #print 'inserting study tag %s to study %d' % (tag,id)
                db.study_tag.insert(study=id,tag=tag)
    elif table == 'tree':
        for tag in tags:
            rows = db.executesql(
                 "SELECT id FROM stree_tag WHERE stree = %d AND tag = '%s'" % (id,tag))
            #rows = db((db.stree_tag.stree == id) & (db.stree_tag.tag == tag)).select()
            if not rows:  #only need to add new tags
                #print 'inserting tree tag %s to tree %d' % (tag,id)
                db.stree_tag.insert(stree=id,tag=tag)


def remove_old_tags(db,table,tags,id):
    """
    deletes all the tag records associated with the entity in table identified by by
    """
    sqltable = NAMETABLEMAP[table]
    tags_table = get_tag_table(table)
    if tags_table:
        for tag in tags:
            db.executesql("DELETE FROM %s WHERE (%s = %d AND tag = '%s')" % (tags_table,sqltable,id,tag))       
            #db((db.study_tag.study == id) & (db.study_tag.tag == tag)).delete()

def get_tag_table(table_name):
    if table_name in ['study','stree']:
        return table_name+'_tag'

def encode_annotation(value):
    """
    serializes the dictionary structure representing a nexson (study) annotation back in textual json
    (might be worthwhile to zip compress the text as well)
    """
    from json import JSONEncoder
    e = JSONEncoder()
    encoded = e.encode(value)
    print "Recoded, length = %d" % len(encoded)
    return encoded


def finish_trees(db,study_id):
   """
   recomputes the binary indexing, retrieves ottol-based labels and regenerates
   the newick string for each tree in the study
   """
   trees = db.executesql("SELECT id FROM stree WHERE study = %d" % study_id)
   for tree_result in trees:
       tree = tree_result[0]
       index_nodes(db,tree)
       restore_labels(db,tree)
       restore_newick(db,tree)
   return study_id

def index_nodes(db,tree_id):
    root_nodes = db.executesql("SELECT id FROM snode WHERE (tree = %d) AND (parent IS NULL)" % tree_id)
    for root in root_nodes:  # should be singleton
        node_id = root[0]
        index_children(db,node_id,0)

def index_children(db, id,n):
    n = n+1
    primary_next = n
    cl = db.executesql("SELECT id FROM snode WHERE parent = %d" % id, as_dict="true")
    if cl:
        last_back = n
        for i,child in enumerate(cl):
            if (i>0):
                n = last_back
            last_back = index_children(db,child.get('id'),n)
        next_back = last_back + 1
    else:
        next_back = n+1
    primary_back = next_back
    if (primary_back == primary_next + 1):
        is_leaf = 'T'
    else:
        is_leaf = 'F'
    #print "UPDATE snode SET next=%d, back=%d, isleaf='%s' WHERE id = %d;" %(primary_next,
    #               primary_back,is_leaf,id)
    db.executesql("UPDATE snode SET next=%d, back=%d, isleaf='%s' WHERE id = %d;" %(primary_next,
                   primary_back,is_leaf,id))
    return next_back

def restore_labels(db,tree):
    """
    restores labels from otu taxa (maybe should check for existing label first?)
    """
    nodes = db.executesql("SELECT id,otu FROM snode WHERE tree = %s AND otu IS NOT NULL" % tree)
    for (id,otu) in nodes:
        ((olabel,),) = db.executesql("SELECT label FROM otu WHERE otu.id = %d" % otu)
        if olabel.find("'") != -1:
            olabel = "".join(olabel.split("'"))
        db.executesql("UPDATE snode SET label = '%s' WHERE id = %d" % (olabel,id))
        
def restore_newick(db,tree):
    import build
    """
    return newick string for specified tree.  Simplified version of
    code in stree controller, which assumes context (e.g., request.vars
    and global definition of db) not available in a module.   Simplified the
    leaf and internal node format code.
    """
    treeid = tree
    root = build.stree(db, treeid)
    lfmt = [ x.split('.') for x in 'snode.id,otu.label'.split(',') ]
    def proc(node, table, field):
        try: s = str(getattr(getattr(node.rec, table), field))
        except AttributeError: s = ''
        return "".join('_'.join(s.split()).split("'"))
    for n in root:
        n.label = ''
        if n.isleaf: n.label = '_'.join([ proc(n, t, f) for t, f in lfmt ])
        else:
            pass
        n.label = n.label.replace('(','--').replace(')','--')
    newick_str = root.write()
    #print "newick_str is {0}".format(newick_str)
    db.executesql("UPDATE stree SET newick = '%s' WHERE id = %d" % (newick_str,tree))
