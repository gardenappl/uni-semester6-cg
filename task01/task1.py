import matplotlib.pyplot as plt
import sys


def is_left_turn(p1: tuple, p2: tuple, p3: tuple) -> bool:
    return ((p2[0] - p1[0])*(p3[1] - p1[1])) - ((p2[1] - p1[1])*(p3[0] - p1[0])) > 0


def is_inside_polygon(p: tuple, points: list[tuple]) -> bool:
    # Count intersections with ray from p to the left
    intersects = 0

    for i in range(len(points)):
        i_next = (i + 1) % len(points)

        if points[i][1] == points[i_next][1]:
            continue
        elif points[i][1] > points[i_next][1]:
            p_high = points[i]
            p_low = points[i_next]
        else:
            p_high = points[i_next]
            p_low = points[i]

        # Check that [p_low, p_high) intersects horizontal line at p
        if not (p_high[1] > p[1] and p_low[1] <= p[1]):
            continue

        if not is_left_turn(p_low, p_high, p):
            intersects += 1

    return intersects % 2 != 0


points = []

with open('points.txt') as points_file:
    for line in points_file:
        points.append(tuple([int(num) for num in line.split()]))

points_x, points_y = zip(*points)

# Locate point given by system args
x, y = [float(arg) for arg in sys.argv[-2:]]

plt.grid()
plt.plot(points_x, points_y, 'ro')
plt.plot(x, y, 'gx')


prev_point = None
for point in points:
    if prev_point:
        plt.plot([prev_point[0], point[0]], [prev_point[1], point[1]])
    else:
        # connect last point to first
        plt.plot([points[-1][0], points[0][0]], [points[-1][1], points[0][1]])
    prev_point = point

print("Belongs to polygon?", is_inside_polygon((x, y), points))


plt.show()
