use phylografter;

delete from gtree;

alter table gtree_share drop foreign key gtree_share_ibfk_1;

ALTER TABLE gtree_share
ADD CONSTRAINT gtree_share_ibfk_1
FOREIGN KEY (user)
REFERENCES auth_user(id);
