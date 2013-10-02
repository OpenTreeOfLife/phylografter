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
    special_clades = collect_special_clades(actions)
    current_row = None
    for action in actions:
        table,field,value = action        
        if (field == 'id'):
            if current_row:
                #print "updating: %d to %s" %(current_row.id,str(current_row))
                current_row.update_record()
                #print "updating id and record: %s" % str(current_row.id)
                if new_tags:
                    #print "updating tags: %s for table %s, id %d" % (str(new_tags),current_table,current_row.id)
                    update_tags(db,current_table,new_tags,current_row.id)
                if (current_table == 'node' and current_row.id in special_clades):
                    current_row['ingroup'] = True
            current_table = table
            current_id = value
            new_tags = set()  
            current_row = find_row(db,current_table,current_id,ele_table_map)
            if current_row is None:
                new_id = fixup_table[(current_table,current_id)]
                current_row = find_row(db,current_table,new_id,ele_table_map)
                old_tags = find_tags(db,current_table,current_id)
                if old_tags:
                    #print "%s old tag count = %d" % (current_table,len(old_tags))
                    remove_old_tags(db,current_table,old_tags,current_id)
                else:
                    pass
                    #print "%s no tags found id = %d" % (current_table,current_id)
        elif (field == 'tag'):
            print "found tag %s" % value
            new_tags.add(value)
        elif (field == 'in_group_clade'):
            pass
        else:
            if current_row:
                current_row[field] = value 
                #print "modifying field %s to %s" % (field,value)  

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
        
def collect_special_clades(actions):
    results = []
    for action in actions:
        table,field,value = action
        if table == 'tree' and field == 'in_group_clade':
           results.append(value)         
    return results  ##todo scan and fill this list


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
        rows = db.executesql('SELECT tag from study_tag WHERE study = %d' % id)
        tags = [row[0][0] for row in rows]
        return set(tags)
    elif (table == 'tree'):
        rows = db.executesql('SELECT tag from stree_tag WHERE stree = %d' % id)
        tags = [row[0][0] for row in rows]
        return set(tags)
    else:
        return None

def update_tags(db,table,tags,id):
    if table == 'study':
        for tag in tags:
            rows = db.executesql(
                 "SELECT id FROM study_tag WHERE study = %d AND tag = '%s'" % (id,tag))
            #rows = db((db.study_tag.study == id) & (db.study_tag.tag == tag)).select()
            if not rows:  #only need to add new tags
                print 'inserting study tag %s to study %d' % (tag,id)
                db.study_tag.insert(study=id,tag=tag)
    elif table == 'tree':
        for tag in tags:
            rows = db.executesql(
                 "SELECT id FROM stree_tag WHERE stree = %d AND tag = '%s'" % (id,tag))
            #rows = db((db.stree_tag.stree == id) & (db.stree_tag.tag == tag)).select()
            if not rows:  #only need to add new tags
                print 'inserting tree tag %s to tree %d' % (tag,id)
                db.stree_tag.insert(stree=id,tag=tag)

def remove_old_tags(db,table,tags,id):
    if table == 'study':
        for tag in tags:
            db.executesql("DELETE FROM study_tag WHERE (study = %d AND tag = '%s')" % (id,tag))       
            #db((db.study_tag.study == id) & (db.study_tag.tag == tag)).delete()
    if table == 'tree':
        for tag in tags:
            db.executesql("DELETE FROM stree_tag WHERE (stree = %d AND tag = '%s')" % (id,tag))           
            #db((db.stree_tag.stree == id) & (db.stree_tag.tag == tag)).delete()
