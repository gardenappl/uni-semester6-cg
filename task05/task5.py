import matplotlib.pyplot as plt
import sys


# Numerator of distance between line P1P2 and point P
# Abs. value of this should be divided by length of P1P2 to get actual distance!
# >0 if to the left, <0 if to the right
def line_point_distance_est(p1, p2, p):
    return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0])


def _quick_hull_recursive(l, r, points):
    print("lr:", l, r)
    print("Points:", points)
    if len(points) == 2:
        return [l, r]

    # Python max returns first largest element
    h = max(points, key=lambda p: line_point_distance_est(l, r, p))
    print("h:", h)

    left_of_lh = []
    left_of_hr = []

    for p in points:
        if line_point_distance_est(l, h, p) >= 0:
            left_of_lh.append(p)
        if line_point_distance_est(h, r, p) >= 0:
            left_of_hr.append(p)

    hull_points = _quick_hull_recursive(l, h, left_of_lh) + _quick_hull_recursive(h, r, left_of_hr)
    # Remove h once, because it will be contained twice
    hull_points.remove(h)

    return hull_points


def quick_hull(points):
    # Start with a vertical line on the leftmost point
    l = min(points, key=lambda p: p[0])
    r = [l[0], l[1] - 1]

    points.append(r)
    hull_points = _quick_hull_recursive(l, r, points)
    hull_points.remove(r)
    points.remove(r)

    return hull_points


points = []

with open('points.txt') as points_file:
    for line in points_file:
        points.append([int(num) for num in line.split()])


points_x, points_y = zip(*points)

plt.plot(points_x, points_y, 'ro')
plt.grid()

hull_points = quick_hull(points)

print("Hull points:", hull_points)

prev_point = None
for hull_point in hull_points:
    if prev_point:
        plt.plot([prev_point[0], hull_point[0]], [prev_point[1], hull_point[1]])
    prev_point = hull_point

# connect first point to last
plt.plot([hull_points[0][0], prev_point[0]], [hull_points[0][1], prev_point[1]])

plt.show()
