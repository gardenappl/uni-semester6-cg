import matplotlib.pyplot as plt
import sys
import math
import numpy as np


def get_angle(p1, p2):
    return (math.atan2(p2[1]-p1[1], p2[0]-p1[0]) % (2*math.pi))


def is_left_turn(p1: tuple, p2: tuple, p3: tuple) -> bool:
    return ((p2[0] - p1[0])*(p3[1] - p1[1])) - ((p2[1] - p1[1])*(p3[0] - p1[0])) >= 0


def is_inside_polygon(p, points) -> bool:
    intersects = 0

    for i in range(len(points)):
        nextI = (i+1) % len(points)
        if points[i][1] == points[nextI][1]:
            continue

        p1, p2 = None, None
        if points[i][1] <= p[1] and points[nextI][1] > p[1]:
            p1 = points[i]
            p2 = points[nextI]
        elif points[i][1] > p[1] and points[nextI][1] <= p[1]:
            p1 = points[nextI]
            p2 = points[i]
        else:
            continue

        if is_left_turn(p, p1, p2):
            intersects += 1

    return intersects % 2 != 0


def hull_jarvis(points: np.ndarray) -> list[tuple]:
    points_list = points.tolist()
    print(points_list)

    lowest_p = min(points_list, key=lambda p: p[1])
    points_list.remove(lowest_p)

    # Go up
    hull = [lowest_p]
    while len(points_list) > 0:
        # Lowest angle from last point in hull
        next_p = min(points_list, key=lambda p: get_angle(hull[-1], p))
        if next_p[1] < hull[-1][1]:
            break
        points_list.remove(next_p)
        hull.append(next_p)

    # Go down
    while len(points_list) > 0:
        # Lowest angle from last point in hull

        # angle should not be 0 unless we're at the bottom
        def _down_get_angle(hull, p):
            angle = get_angle(hull[-1], p)
            if angle == 0 and p[1] != lowest_p[1]:
                return 2*math.pi
            else:
                return angle

        next_p = min(points_list, key=lambda p: _down_get_angle(hull, p))
        if next_p[1] > hull[-1][1]:
            break
        points_list.remove(next_p)
        hull.append(next_p)
    
    return hull
    

def graham_scan(points: list[tuple]):
    start_point = max(points, key=lambda p: p[0])

    i = points.index(start_point)
    while True:
        print("Graham scan points:", points)
        print(points[i], points[(i+1) % len(points)], points[(i+2) % len(points)])
        if (is_left_turn(points[i], points[(i+1) % len(points)], points[(i+2) % len(points)])):
            i = (i+1) % len(points)
        else:
            points.pop((i+1) % len(points))
            i = (i-1) % len(points)
        if points[(i+1) % len(points)] == start_point:
            break

    print("Grahan scan result:", points)
    


def hull_shamos(points: np.ndarray):
    if len(points) <= 2:
        return points.tolist()
    elif len(points) <= 5: 
        return hull_jarvis(points)

    def merge(rotateP: tuple, points1: list[tuple], points2: list[tuple]) -> list[tuple]:
        mergePoints = []

        i = 0
        i1 = points1.index(min(points1, key=lambda p: get_angle(rotateP, p)))
        i2 = points2.index(min(points2, key=lambda p: get_angle(rotateP, p)))
        i1merged, i2merged = 0, 0

        while i < len(points1) + len(points2):
            if i2merged == len(points2) or (i1merged < len(points1) and 
                    get_angle(rotateP, points1[i1]) < get_angle(rotateP, points2[i2])):
                mergePoints.append(points1[i1])
                i1 = (i1 + 1) % len(points1)
                i1merged += 1
            else:
                mergePoints.append(points2[i2])
                i2 = (i2 + 1) % len(points2)
                i2merged += 1
            i += 1

        return mergePoints



    hull1 = hull_shamos(points[0:int(len(points) / 2)])
    print("Hull 1: ", hull1)
    hull2 = hull_shamos(points[int(len(points) / 2):len(points)])
    print("Hull 2: ", hull2)

    p = np.average(hull1[0:3], 0).tolist()
    print("P: ", p)
    if is_inside_polygon(p, hull2):
        print("...is inside Hull 2!")
        merged_hull = merge(p, hull1, hull2)
        graham_scan(merged_hull)
        return merged_hull
    else:
        print("...is not inside Hull 2!")

        min_angle_p2 = min(hull2, key=lambda p2: get_angle(p, p2))
        print("Min. angle p2:", min_angle_p2)
        max_angle_p2 = max(hull2, key=lambda p2: get_angle(p, p2))
        print("Max. angle p2:", max_angle_p2)

        min_angle_i = hull2.index(min_angle_p2)
        max_angle_i = hull2.index(max_angle_p2)
        min_p2_next = hull2[(min_angle_i + 1) % len(hull2)]
        print(min_p2_next)
        min_p2_prev = hull2[(min_angle_i - 1) % len(hull2)]
        print(min_p2_prev)

        hull2_outer = []
        if (is_left_turn(min_p2_prev, min_angle_p2, min_p2_next)):
            if (min_angle_i < max_angle_i):
                for i in range(min_angle_i, max_angle_i + 1):
                    hull2_outer.append(hull2[i])
            else:
                for i in range(0, max_angle_i + 1):
                    hull2_outer.append(hull2[i])
                for i in range(min_angle_i, len(hull2)):
                    hull2_outer.append(hull2[i])
        else:
            if (min_angle_i > max_angle_i):
                for i in range(max_angle_i, min_angle_i + 1):
                    hull2_outer.append(hull2[i])
            else:
                for i in range(0, min_angle_i + 1):
                    hull2_outer.append(hull2[i])
                for i in range(max_angle_i, len(hull2)):
                    hull2_outer.append(hull2[i])

        print("Hull 2 outer:", hull2_outer)
        merged_hull = merge(p, hull1, hull2_outer)
        graham_scan(merged_hull)
        return merged_hull


points = []

with open('points.txt') as points_file:
    for line in points_file:
        points.append([int(num) for num in line.split()])


points_x, points_y = zip(*points)

plt.plot(points_x, points_y, 'ro')
plt.grid()

hull_points = hull_shamos(np.array(points))

print("Hull points:", hull_points)

prev_point = None
for hull_point in hull_points:
    if prev_point is not None:
        plt.plot([prev_point[0], hull_point[0]], [prev_point[1], hull_point[1]])
    prev_point = hull_point

# connect first point to last
plt.plot([hull_points[0][0], prev_point[0]], [hull_points[0][1], prev_point[1]])

plt.show()
