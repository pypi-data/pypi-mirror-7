# -*- encoding: utf-8 -*-
# Module iainfcanon

from numpy import *
from string import upper

def iainfcanon(f, Iab, theta=45, DIRECTION="CLOCKWISE"):
    from iaunion import iaunion
    from iainterot import iainterot
    from iaintersec import iaintersec
    from iainfgen import iainfgen

    DIRECTION = upper(DIRECTION)
    y = iaunion(f,1)
    for t in range(0,360,theta):
        Irot = iainterot( Iab, t, DIRECTION )
        y = iaintersec( y, iainfgen(f, Irot))

    return y

