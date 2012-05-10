"""
Copyright 2012 Joe Friedl
See LICENSE for licensing details.
"""

import math

def dot_product(u, v):
    return u[0] * v[0] + u[1] * v[1]

def normalize(v):
    mag = math.sqrt(v[0]**2 + v[1]**2)
    return (v[0]/mag, v[1]/mag)

def projection(edge, points):
    unit = normalize((-edge[1], edge[0]))
    minimum = None
    maximum = None
    for point in points:
        proj = dot_product(unit, point)
        if minimum is None or proj < minimum:
            minimum = proj
        if maximum is None or proj > maximum:
            maximum = proj
    return (minimum, maximum)
