import build
from ivy import layout

def index():
    return dict()

def force():
    return dict()

def nodepos():
    t = request.args(0)
    i = int(request.args(1))
    if t == "stree":
        root = build.stree(db, i)
    elif t == "gtree":
        root = build.gtree(db, i)

    n2c = layout.calc_node_positions(root, 0.95, 0.95, scaled=False)
    return response.json(
        [ dict(id=k.id, x=v.x, y=v.y,
               px=n2c[k.parent].x if n2c.get(k.parent) else None,
               py=n2c[k.parent].y if n2c.get(k.parent) else None)
          for k,v in n2c.items() ]
        )

def forcenodepos():
    t = request.args(0)
    i = int(request.args(1))
    if t == "stree":
        r = build.stree(db, i)
    elif t == "gtree":
        r = build.gtree(db, i)

    nodes = [ dict(index=i, id=n.id, label=n.label) for i, n in enumerate(r) ]
    id2i = dict([ (n.id, i) for i, n in enumerate(r) ])
    links = [ dict(source=i, target=id2i[n.parent.id])
              for i, n in enumerate(r) if n.parent ]

    return dict(nodes=nodes, links=links)
