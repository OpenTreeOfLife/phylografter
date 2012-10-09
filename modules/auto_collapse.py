def auto_collapse_info(node, collapsed, visible=True):
    """
    gather information to determine if a node should be collapsed

    collapsed is a set or dictionary containing node.id values of
    those nodes that are already collapsed

    node.data is a gluon.storage.Storage object
    """
    if visible and (node.id in collapsed):
        visible = False
    nnodes = 1 # total number of nodes, including node
    # number of visible leaves
    nvisible = int((visible and bool(len(node.children))) or node.id in collapsed)
    ntips = bool(len(node.children))
    ntips_visible = int(bool(len(node.children)) and visible)
    node.has_labeled_descendant = False

    node.depth = 1

    #if node.common_prefix and (not node.label):
        #node.label = node.common_prefix

    for child in node.children:
        auto_collapse_info(child, collapsed, visible)
        nnodes += child.nnodes
        nvisible += child.nvisible
        ntips += child.ntips
        ntips_visible += child.ntips_visible
        if (child.label and (not bool(len(child.children)))) \
           or (child.has_labeled_descendant):
            node.has_labeled_descendant = True
        if child.depth >= node.depth:
            node.depth = child.depth+1
    node.nnodes = nnodes
    node.nvisible = nvisible
    node.ntips = ntips
    node.ntips_visible = ntips_visible

def auto_collapse(root, collapsed, keep_visible, max_tips_visible=125):
    """
    traverse a tree and find nodes that should be collapsed in order
    to satify max_tips_visible

    collapsed is a set or dict for storing node.id values of collapsed
    nodes

    keep_visible is a set or dict containing node.id values that
    should not be placed in collapsed
    """

    ntries = 0
    while True:
        if ntries > 10:
            return
        ntries += 1
        auto_collapse_info(root, collapsed)
        nvisible = root.nvisible
        if nvisible <= max_tips_visible:
            return
        
        v = []
        for node in root.iternodes():
            if node.label and (not bool(len(node.children))) and node.parent and \
                   (node.id not in keep_visible):
                w = node.nvisible/float(node.depth)
                if node.has_labeled_descendant:
                    w *= 0.25
                v.append((w, node))
        v.sort(); v.reverse()

        for w, node in v:
            if node.id not in keep_visible and node.nvisible < (nvisible-1):
                collapsed[str(node.id)] = 1
                nvisible -= node.nvisible
            if nvisible <= max_tips_visible:
                break
