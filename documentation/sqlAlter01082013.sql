use phylografter;

delete from gtree;

//originally, gtree_share referenced a table called 'unique_user', which was an attempt at normalizing the auth_user table ( many rows in this table could refer to the same person as the login is based on email address ).  I recently decided this was too difficult a problem to do well, so I reverted to using the auth_user table to reference privileges on grafted trees.
alter table gtree_share drop foreign key gtree_share_ibfk_1;

ALTER TABLE gtree_share
ADD CONSTRAINT gtree_share_ibfk_1
FOREIGN KEY (user)
REFERENCES auth_user(id);

CREATE TABLE userEdit (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR( 200 ),
    timestamp DATETIME,
    tableName VARCHAR( 100 ),
    rowId INT,
    fieldName VARCHAR( 100 ),
    previousValue LONGTEXT,
    updatedValue LONGTEXT
);
