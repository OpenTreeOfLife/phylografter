from gluon.html import *
import re, enchant
DIGITS = re.compile(r'\d')
INFRANK = re.compile(r'(\s+(ssp|subsp|var|forma|f)([.]?)(?=\s+))', re.I)
NAMES = 'applications/phylografter/static/names.txt'
d = enchant.request_pwl_dict(NAMES)

def check(s):
    try: return d.check(s)
    except:
        print 'spellcheck.check error', s
        return None

def suggest(s):
    return d.suggest(s)

def process_label(db, otu):
    options = []
    s = otu.label.replace('_', ' ')
    if check(s):
        options = list(db(db.ottol_name.name==s).select())
        return (True, options)
    v = suggest(s)
    if not v:
        words = s.replace('.',' ').split()
        if words[-1].lower() == 'sp':
            words = words[:-1]
        s = DIGITS.sub('', ' '.join(words))
        if not s: return (False, options)
        if check(s):
            options = list(db(db.ottol_name.name==s).select())
            return (True, options)

        v = suggest(s)
        if not v and INFRANK.search(s):
            s = INFRANK.sub('', s)
            v = suggest(s)
        if not v:
            words = s.split()
            N = len(words)
            if N > 2:
                i = N-1
                while i >= 2:
                    t = ' '.join(words[:i])
                    v = suggest(t)
                    if v: break
                    else: i -= 1
    for w in v:
        for row in db(db.ottol_name.name==w).select():
            options.append(row)
    return (False, options)

