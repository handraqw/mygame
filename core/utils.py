def circles_overlap(pos1, radius1, pos2, radius2):
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    d2 = dx * dx + dy * dy
    return d2 <= (radius1 + radius2) ** 2