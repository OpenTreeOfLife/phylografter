class Coordinates:
    def __init__(self):
        pass

def smooth_xpos(node, n2coords, collapsed=None):
    collapsed = collapsed or set()
    if (not node.isleaf) and (node.id not in collapsed):
        children = node.children
        for ch in children:
            smooth_xpos(ch, n2coords=n2coords, collapsed=collapsed)
        
        if node.parent:
            px = n2coords[node.parent].x
            cx = min([ n2coords[ch].x for ch in children ])
            n2coords[node].x = (px + cx)/2.0

def depth_length_preorder_traversal(node, n2coords=None, collapsed=None):
    "calculate node depth (root = depth 0) and length to root"
    if n2coords is None:
        n2coords = {}
    collapsed = collapsed or set()
    coords = n2coords.get(node) or Coordinates()
    coords.node = node
    if not node.parent:
        coords.depth = 0
        coords.length_to_root = 0.0
    else:
        p = n2coords[node.parent]
        coords.depth = p.depth + 1
        coords.length_to_root = p.length_to_root + (node.length or 0.0)
    n2coords[node] = coords
    if not node.id in collapsed:
        for ch in node.children:
            depth_length_preorder_traversal(ch, n2coords=n2coords,
                                            collapsed=collapsed)

    return n2coords

def calc_node_positions(node, width, height,
                        lpad=0, rpad=0, tpad=0, bpad=0,
                        scaled=True, collapsed=None, n2coords=None
                        ):
    "origin is at upper left"
    width -= (lpad + rpad)
    height -= (tpad + bpad)

    collapsed = collapsed or set()
    
    node.parent = None
    
    if n2coords is None:
        n2coords = {}
    depth_length_preorder_traversal(node, n2coords=n2coords,
                                    collapsed=collapsed)
    leaves = list(
        node.iternodes(f=lambda x: x.isleaf and (x.id not in collapsed))
        )
    nleaves = len(leaves)
    maxdepth = max([ n2coords[lf].depth for lf in leaves ])
    unitwidth = width/float(maxdepth)
    unitheight = height/(nleaves-1.0)

    xoff = (unitwidth * 0.5)
    yoff = (unitheight * 0.5)

    if scaled:
        maxlen = max([ n2coords[lf].length_to_root for lf in leaves ])
        scale = width/maxlen

    for i, lf in enumerate(leaves):
        c = n2coords[lf]
        c.y = i * unitheight
        if not scaled:
            c.x = width
        else:
            c.x = c.length_to_root * scale

    for n in node.postiter(f=lambda x:x.id not in collapsed):
        c = n2coords[n]
        if (not n.isleaf) and (n.id not in collapsed) and n.children:
            children = n.children
            ymax = n2coords[children[0]].y
            ymin = n2coords[children[-1]].y
            c.y = (ymax + ymin)/2.0
            if not scaled:
                c.x = min([ n2coords[ch].x for ch in children ]) - unitwidth
            else:
                c.x = c.length_to_root * scale

    if not scaled:
        for i in range(10):
            smooth_xpos(node, n2coords, collapsed=collapsed)

    for coords in n2coords.values():
        coords.x += lpad
        coords.y += tpad

    for n, coords in n2coords.items():
        if n.parent:
            p = n2coords[n.parent]
            coords.px = p.x; coords.py = p.y
        else:
            coords.px = None; coords.py = None

    return n2coords

if __name__ == "__main__":
    import ivy
    node = ivy.tree.read("(a:3,(b:2,(c:4,d:5):1,(e:3,(f:1,g:1):2):2):2);")
    for i, n in enumerate(node.iternodes()):
        if not n.isleaf:
            n.label = "node%s" % i
    node.label = "root"
    calc_node_positions(node, width=10, height=10, scaled=True)
    
