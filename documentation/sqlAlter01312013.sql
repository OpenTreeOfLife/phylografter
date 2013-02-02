use phylografter;

//For some reason there are two foreign key constraints on the table gnode that do the same thing -- make sure the 'parent' column in a gnode row matches up with a gnode.id.  It is the right idea, but right now its necessary to delete gnode rows in serial ( when reverting a tree edit ) that may not always conform to this restraint.
alter table gnode drop foreign key gnode_ibfk_4;
alter table gnode drop foreign key gnode_ibfk_5;
