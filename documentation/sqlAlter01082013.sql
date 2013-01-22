use phylografter;

delete from gtree;

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
    updatedValue LONGTEXT )
);
