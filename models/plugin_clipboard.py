def plugin_clipboard( p ):
    return LOAD( 'plugin_clipboard', 'default.load', ajax=True, vars=p )


db.define_table( 'clipboard', Field( 'nodeId', 'integer', notnull=True ), 
                              Field( 'treeType', 'string' ),
                              Field( 'name', 'string' ),
                              Field( 'user', db.auth_user ),
                              Field( 'creationDate', 'datetime' ) )
