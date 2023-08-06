# -*- encoding: utf-8 -*-
# Module iacdil

from numpy import *
from iasecross import iasecross

def iacdil(f, g, b=iasecross(), n=1):
    from iaintersec import iaintersec
    from iadil import iadil
    from iaisequal import iaisequal

    y = iaintersec(f,g)
    for i in xrange(n):
        aux = y
        y = iaintersec( iadil(y,b),g)
        if iaisequal(y,aux): break
    return y

