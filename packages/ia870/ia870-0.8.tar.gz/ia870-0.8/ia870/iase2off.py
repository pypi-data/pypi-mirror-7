# -*- encoding: utf-8 -*-
# Module iase2off

import numpy as np
def iase2off(Bc,option='neigh'):
    '''Converts structuring element to list of neighbor offsets in graph image'''
    h,w = Bc.shape
    hc,wc = h/2,w/2
    B = Bc.copy()
    B[hc,wc] = 0  # remove origin
    off = np.transpose(B.nonzero()) - np.array([hc,wc])
    if option == 'neigh':
        return off  # 2 columns x n. of neighbors rows
    elif option == 'fw':
        i = off[:,0] * w + off[:,1]
        return off[i>0,:]  # only neighbors higher than origin in raster order
    elif option == 'bw':
        i = off[:,0] * w + off[:,1]
        return off[i<0,:]  # only neighbors less than origin in raster order
    else:
        assert 0,'options are neigh, fw or bw. It was %s'% option
        return None

