#!/usr/bin/env python
# coding: utf8
from gluon import *


def sql_process(actions, db):
    ele_table_map = init_map(db)
    first_table,first_field,first_id= actions[0]
    if (first_table != 'study' or first_field != 'id'):
        print "First action is not a study identifier - exiting"
        return
    fixup_table = insert_new_rows(actions,db)
    current_row = None
    for action in actions:
        #print "action is %s, %s, %s" % action
        current_table,field,value = action        
        if (field == 'id'):
            current_id = value
            new_tags = set()  
            if current_row:
                #print "updating: %d to %s" %(current_row.id,str(current_row))
                current_row.update_record()
                #print "updating id and record: %s" % str(current_row.id)
            current_row = find_row(db,current_table,current_id,ele_table_map)
            current_tags = find_tags(db,current_table,current_id)
            if current_tags:
                print "%s tag count = %d" % (current_table,len(current_tags))
            else:
                pass
                #print "%s no tags found id = %id" % (current_table,current_id)
            if current_row is None:
                new_id = fixup_table[(current_table,current_id)]
                current_row = find_row(db,current_table,new_id,ele_table_map)
                if current_tags:
                    update_tags(db,current_table,current_tags,new_id)
        elif (field == 'tag'):
            print "found tag %s" % value
            new_tags.add(value)
        else:
            if current_row:
                current_row[field] = value 
                print "modifying field %s to %s" % (field,value)  

def init_map(db):
    return {'study': db.study.id,
            'study_tag': db.study_tag.id,
            'otu': db.otu.id,
            'tree': db.stree.id,
            'node': db.snode.id}
            

def find_row(db, table,id,ele_table):
    rows = db(ele_table[table] == id)
    if rows:
        return rows.select().first()
    else:
        return None


def insert_new_rows(actions, db):
    ele_table_map = init_map(db)
    action_gen = generate_actions(actions)
    update_obj = {}
    fixup_table = {}
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
                        if not(field == 'id'):
                            table,field,value = action
                            update_obj[field] = value
                        action = action_gen.next()
                        field = action[1]    
                    table,field,value = action  # update for next record
                    new_id = insert_new(db,update_table,update_obj)
                    fixup_table[(update_table,update_id)] = new_id
                else:
                    table,field,value = action_gen.next()
            else:
                table,field,value = action_gen.next()  
    except StopIteration:
        return fixup_table
 
def generate_actions(actions):
    for action in actions:
        yield action
        
#wish could do this with a lookup, but some tables need to be placated with dummy values
def insert_new(db,table,values):
    if table=='study':
        if 'citation' in values and 'contributor' in values:
            return db.study.insert(citation=values['citation'],contributor=values['contributor'])
    if table=='study_tag':  #maybe this should be interned, rather than generate - no id is saved
        return db.study_tag.insert()
    if table=='otu':
        if 'label' in values:
            return db.otu.insert(label=values['label'])
    if table=='tree':
        return db.stree.insert()
    if table=='node':
        return db.snode.insert()

def find_tags(db,table,id):
    """
    returns set of rows of id records (from study_tag, or stree_tag as appropriate)
    """
    if (table == 'study'):
        return db(db.study_tag.study == id).select()
    elif (table == 'stree'):
        return db(db.stree_tag.stree == id).select()
    else:
        return None

def update_tags(db,table,rows,new_id):
    for row in rows:
        print "updating tag %s study field %d to %d" % (row[tag],row[study],new_id)
        row[study]=new_id
