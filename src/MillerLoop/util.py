# debugging -- this investigates the repetition of points
def debug_points(P, F, key, huff):
    for i, p in enumerate(P):
        _p = (p.out, p.x, p.y, p.mod)
        huff.points[F][key][i].add(_p)
        huff.points["all"].add(_p)
        huff.loops["all"] += 1
    huff.loops[F][key] += 1