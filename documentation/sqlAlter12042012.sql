
alter table clipboard add user int;


alter table gtree_edit add newNodeOriginId INT;
alter table gtree_edit add newNodeOriginType VARCHAR(100);

alter table gtree_edit drop foreign key gtree_edit_ibfk_3;
alter table gtree_edit drop foreign key gtree_edit_ibfk_5;
drop index source_node__idx on gtree_edit;
drop index clipboard_node__idx on gtree_edit;
alter table gtree_edit drop column source_node;
alter table gtree_edit drop column clipboard_node;
