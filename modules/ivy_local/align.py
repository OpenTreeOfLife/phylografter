import os
from subprocess import Popen, PIPE
from Bio import AlignIO
from cStringIO import StringIO

def muscle(seqs, bin="/usr/bin/muscle"):
    #assert os.path.exists(bin)
    p = Popen(bin, stdin=PIPE, stdout=PIPE)
    write = p.stdin.write
    for x in seqs:
        write(">%s\n%s\n" % (x.id, x.seq))
    out = p.communicate()[0]
    aln = AlignIO.read(StringIO(out), 'fasta')
    return aln
    
def read(data, format=None, name=None):
    from Bio import AlignIO
    from cStringIO import StringIO
    from types import StringTypes
    
    def strip(s):
        fname = os.path.split(s)[-1]
        head, tail = os.path.splitext(fname)
        tail = tail.lower()
        if tail in (".fasta", ".nex", ".nexus"):
            return head
        else:
            return fname

    if (not format):
        if (type(data) in StringTypes) and os.path.isfile(data):
            s = data.lower()
            if s.endswith("fasta"):
                format="fasta"
            for tail in ".nex", ".nexus":
                if s.endswith(tail):
                    format="nexus"
                    break

    if (not format):
        format = "fasta"

    if type(data) in StringTypes:
        if os.path.isfile(data):
            name = strip(data)
            with open(data) as f:
                return AlignIO.read(f, format)
        else:
            f = StringIO(data)
            return AlignIO.read(f, format)

    elif (hasattr(data, "tell") and hasattr(data, "read")):
        treename = strip(getattr(data, "name", None))
        return AlignIO.read(data, format)

    raise IOError, "unable to read tree from '%s'" % data
    
def find(aln, substr):
    """
    generator that yields (seqnum, pos) tuples for every position of
    ``subseq`` in `aln`
    """
    from seq import finditer
    N = len(substr)
    for i, rec in enumerate(aln):
        for j in finditer(rec.seq, substr):
            yield (i,j)
            
