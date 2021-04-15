import matplotlib.pyplot as plt
from collections import deque


def is_right_turn(p1: tuple, p2: tuple, p3: tuple) -> bool:
    return ((p2[0] - p1[0])*(p3[1] - p1[1])) - ((p2[1] - p1[1])*(p3[0] - p1[0])) < 0


def _get_convex_hull_lee_curve(polygon, upper_curve: bool):
    if upper_curve:
        start = min(polygon, key=lambda p: p[0])
        end = max(polygon, key=lambda p: p[0])

        # Fictional point
        p0 = (start[0], start[1] - 1)
    else:
        start = max(polygon, key=lambda p: p[0])
        end = min(polygon, key=lambda p: p[0])

        # Fictional point
        p0 = (start[0], start[1] + 1)

    if polygon.index(start) < polygon.index(end):
        curve = deque(polygon[polygon.index(start) + 1:polygon.index(end) + 1])
    else:
        curve = deque(polygon[polygon.index(start) + 1:])
        curve.extend(polygon[:polygon.index(end) + 1])
    hull_curve = deque([p0, start])

    while curve:
        print("Curve:", curve)
        print("Hull curve:", hull_curve)
        p = curve.popleft()

        print("Step 1:", hull_curve[-2], hull_curve[-1], p)
        if is_right_turn(hull_curve[-2], hull_curve[-1], p):
            print("Correct turn")

            last_hull_index = polygon.index(hull_curve[-1])
            if last_hull_index - 1 >= polygon.index(start):
                prev_p = polygon[last_hull_index - 1]
            else:
                prev_p = p0

            print("Step 2:", prev_p, hull_curve[-1], p)
            if is_right_turn(prev_p, hull_curve[-1], p):
                print("Correct turn")

                print("Step 3:", end, hull_curve[-1], p)
                if is_right_turn(end, hull_curve[-1], p) or p == end:
                    print("Correct turn")
                    hull_curve.append(p)
                else:
                    print("Wrong turn")
                    while not (is_right_turn(end, hull_curve[-1], curve[0]) or curve[0] == end):
                        curve.popleft()
            else:
                print("Wrong turn")
                while not is_right_turn(hull_curve[-1], hull_curve[-2], curve[0]):
                    curve.popleft()
        else:
            print("Wrong turn")
            while not is_right_turn(hull_curve[-2], hull_curve[-1], p):
                hull_curve.pop()
            hull_curve.append(p)

    hull_curve.remove(p0)
    return hull_curve


def get_convex_hull_lee(polygon):
    print("-----------------")
    print(" Get upper curve ")
    print("-----------------")
    upper_curve = _get_convex_hull_lee_curve(polygon, upper_curve=True)
    print("------")
    print("Upper curve:", upper_curve)

    print("-----------------")
    print(" Get lower curve ")
    print("-----------------")
    lower_curve = _get_convex_hull_lee_curve(polygon, upper_curve=False)
    print("------")
    print("Lower curve:", lower_curve)

    upper_curve.extend(lower_curve)
    return list(upper_curve)
        

points = []

with open('points.txt') as points_file:
    for line in points_file:
        points.append(tuple([int(num) for num in line.split()]))

points_x, points_y = zip(*points)

plt.plot(points_x, points_y, 'ro')
plt.grid()

hull_points = get_convex_hull_lee(points)

print("Hull points:", hull_points)
print("Points:", points)


def plot_polygon(points, style):
    prev_point = None
    for point in points:
        if prev_point:
            plt.plot([prev_point[0], point[0]], [prev_point[1], point[1]], style)
        else:
            # connect last point to first
            plt.plot([points[-1][0], points[0][0]], [points[-1][1], points[0][1]], style)
        prev_point = point


plot_polygon(points, 'b')
plot_polygon(hull_points, 'r')


plt.show()
