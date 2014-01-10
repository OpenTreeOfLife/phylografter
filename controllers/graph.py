# coding: utf-8
## View a graph of the chosen tree and taxonomy
    
def index():
    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "TreeGraph of source tree %s" % rec.id
    return dict(rec=rec)

def view_ncbi():
    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "NCBI TreeGraph of source tree %s" % rec.id
    return dict(rec=rec)    

def view_ott():
    rec = db.stree(request.args(0))
    treeid = str(rec.id)
    def w(f,v):
        u = URL(c="study",f="view",args=[v])
        return A(_study_rep(db.study(v)), _href=u)
    db.stree.study.widget = w
    response.subtitle = "OTT TreeGraph of source tree %s" % rec.id
    return dict(rec=rec)                   
