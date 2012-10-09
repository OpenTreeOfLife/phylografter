def plugin_treeViewer( p ):

    if( 'tree' in p ):
        session.treeViewerTree = p['tree']

    return LOAD( 'plugin_treeViewer', 'treeViewer.load', ajax=True, vars=p )
