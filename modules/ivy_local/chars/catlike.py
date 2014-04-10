import scipy, numpy
from numpy import zeros, ones, nonzero, diag_indices_from, arange
from scipy.linalg import expm

def lnL(k, rates, mu):
    Q = numpy.zeros((k,k))
    #Q.flat[K_idx] = rates
    Q[0,1] = rates; Q[1,0] = 1-rates
    Q *= mu
    Q[diag_idx] = Q.sum(1)*-1
    for i, n in enumerate(nodes):
        if not n.isleaf:
            Pv = [ (expm(Q*child.length)*nodecond[n2i[child]]).sum(1)
                   for child in n.children ]
            nodecond[i] = numpy.multiply(*Pv)
    lk = numpy.log((nodecond[-1]*pi).sum())
    return lk
