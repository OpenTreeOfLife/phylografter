#!/usr/bin/env python
# coding: utf8
from gluon import *


def sql_process(actions, db):
    study_contributor = ""
    study_id = -1
    tree_id = -1
    ele_table_map = init_map(db)
    first_table,first_field,first_id= actions[0]
    if (first_table != 'study' or first_field != 'id'):
        raise HTTP(400,"Head of nexson file was not a study identifier - exiting")
        return
    fixup_table = insert_new_rows(actions,db)
    db.commit()  # think this is necessary
    special_clades = collect_special_clades(actions)
    current_row = None
    for action in actions:
        table,field,value = action
        if (field == 'id'):  #time to update the previous element
            if current_row:
                if current_table == 'otu':
                    current_row['study']= study_id
                elif current_table == 'tree':
                    current_row['study'] = study_id
                elif current_table == 'node':
                    print "Trying to update nodes's tree to %d" % tree_id
                    current_row['tree'] = tree_id
                print "updating: %d to %s" %(current_row.id,str(current_row))
                current_row.update_record()
                if new_tags:
                    update_tags(db,current_table,new_tags,current_row.id)
                if (current_table == 'node' and current_row.id in special_clades):
                    current_row['ingroup'] = True
            current_table = table
            current_id = value
            new_tags = set()
            current_row = find_row(db,current_table,current_id,ele_table_map)
            if current_row is None:
                if (current_table,current_id) in fixup_table:
                    new_id = fixup_table[(current_table,current_id)]
                else:
                    new_id = current_id
                print 'about to retrieve %s with id %d' % (current_table,new_id)  
                current_row = find_row(db,current_table,new_id,ele_table_map)
                current_id = new_id    
            print 'retrieved %s' % str(current_row)
            old_tags = find_tags(db,current_table,current_id)
            if old_tags:
                #print "%s old tag count = %d" % (current_table,len(old_tags))
                remove_old_tags(db,current_table,old_tags,current_id)
            if (current_table == 'study'):
                study_id = current_id
            elif (current_table == 'tree'):
                tree_id = current_id
        elif (field == 'tag'):
            print "found tag %s" % value
            new_tags.add(value)
        elif (field == 'in_group_clade'):
            pass
        else:
            if current_row:
                if (table,field) in fixup_table:  #sometimes updatable fields may have names different from their value tables
                    final_value = fixup_table[(table,field)]
                else:
                    final_value = value 
                current_row[field] = final_value
                print "modifying field %s to %s" % (field,final_value)
                if (table == 'study' and field=='contributor'):
                    study_contributor = final_value
    return finish_trees(db,study_id)  

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

# should return true if existing row with matching id is compatible                
def validate_row(db, table,id,ele_table):
    return True
        
def collect_special_clades(actions):
    return [action[2] for action in actions if special_clade_test(action)]    
#    for action in actions:
#        if _special_clade_test(action):
#           results.append(action[2])         
#    return results

def special_clade_test(action):
    table,field,value = action
    return (table == 'tree' and field == 'in_group_clade')
    
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
                        if immediately_updateable(table,field):
                            update_obj[field] = value
                        action = action_gen.next()
                        field = action[1]
                    table,field,value = action # update for next record
                    print "About to update: table= %s, update_obj = %s, update_id = %d" % (str(update_table),str(update_obj),update_id)
                    new_id = insert_new(db,update_table,update_obj,update_id)
                    print "just updated, update_table is %s, new_id is %d" % (str(update_table),new_id)
                    if new_id > 0: # if restore to original id works, no need to add to fixup
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
def insert_new(db,table,values,old_id=None):
    if table=='study':
        if 'citation' in values and 'contributor' in values:
            if old_id:
                new_id = db.study.insert(id=old_id,citation=values['citation'],contributor=values['contributor'])
            else:
                new_id = db.study.insert(citation=values['citation'],contributor=values['contributor'])
            print "new row is %s" % str(new_id)
            return new_id
    if table=='study_tag':  #maybe this should be interned, rather than generate - no id is saved
        return db.study_tag.insert()
    if table=='otu':
        if 'label' in values:
            if old_id:
                return db.otu.insert(id=old_id,label=values['label'])
            else:
                return db.otu.insert(label=values['label'])
    if table=='tree':
        if 'contributor' in values:
            if old_id:
                new_id = db.stree.insert(id=old_id,contributor=values['contributor'],newick='')
            else:
                new_id = db.stree.insert(contributor=values['contributor'],newick='',type='')
        else: 
            if old_id:
                new_id = db.stree.insert(id=old_id,contributor='',newick='',type='')
            else:
                new_id = db.stree.insert(contributor='',newick='',type='')
            return new_id  
    if table=='node':
        return db.snode.insert()


immediately_updateable_table = {"study": ("citation","contributor"),
                                "study_tag": None,
                                "otu": ("label",),
                                "tree": ("contributor","newick","type"),
                                "node": None}
                                
def immediately_updateable(table,value):
    if immediately_updateable_table[table]:
        return value in immediately_updateable_table[table]
    else:
        return False
        
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


def finish_trees(db,study_id):
   from ivy.tree import index
   trees = db.executesql("SELECT id FROM stree WHERE study = %d" % study_id)
   for tree_result in trees:
       index_nodes(db,tree_result[0])
   return study_id

def index_nodes(db,tree_id):
    root_nodes = db.executesql("SELECT id FROM snode WHERE tree = %d AND parent IS NULL")
