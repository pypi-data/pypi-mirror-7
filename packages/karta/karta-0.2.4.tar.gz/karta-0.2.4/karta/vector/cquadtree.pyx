# QuadTree functions

def iswithin(tuple bbox, tuple pt):
    """ Return whether a point is within a bounding box (planar approximation). """
    cdef float xmn = bbox[0]
    cdef float xmx = bbox[1]
    cdef float ymn = bbox[2]
    cdef float ymx = bbox[3]
    cdef float x = pt[0]
    cdef float y = pt[1]
    if (xmn <= x < xmx and ymn <= y < ymx):
        return True
    else:
        return False

def qthashpt(float xmin, float xmax, float ymin, float ymax, float x, float y):
    """ Returns a generator that returns successive quadrants [0-3] that
    constitute a geohash for *pt* in a global *bbox*. """
    cdef float xm, ym
    cdef int geohash
    while True:
        xm = 0.5 * (xmin + xmax)
        ym = 0.5 * (ymin + ymax)
        if x < xm:
            if y < ym:
                geohash = 0
                xmax = xm
                ymax = ym
            elif y >= ym:
                geohash = 2
                xmax = xm
                ymin = ym
            else:
                raise HashError
        elif x >= xm:
            if y < ym:
                geohash = 1
                xmin = xm
                ymax = ym
            elif y >= ym:
                geohash = 3
                xmin = xm
                ymin = ym
            else:
                raise HashError
        else:
            raise HashError
        yield geohash
        
class HashError(Exception):
    pass

