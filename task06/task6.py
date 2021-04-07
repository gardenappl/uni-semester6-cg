import matplotlib.pyplot as plt
import sys
import math
import numpy as np
import itertools as it


def get_angle(p1, p2):
    return (math.atan2(p2[1]-p1[1], p2[0]-p1[0]) % (2*math.pi))


def get_distance_sq(p1, p2):
    return pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[0], 2)


def is_left_turn(p1: tuple, p2: tuple, p3: tuple) -> bool:
    return ((p2[0] - p1[0])*(p3[1] - p1[1])) - ((p2[1] - p1[1])*(p3[0] - p1[0])) >= 0


def is_inside_polygon(p, points) -> bool:
    intersects = 0

    for i in range(len(points)):
        nextI = (i+1) % len(points)
        if points[i][1] == points[nextI][1]:
            continue

        if not ((points[i][1] <= p[1] and points[nextI][1] > p[1]) or
                (points[i][1] > p[1] and points[nextI][1] <= p[1])):
            continue

        angle1 = get_angle(p, points[i])
        angle2 = get_angle(p, points[nextI])

        bisect_angle = (angle1 + angle2) / 2
        if abs(angle1 - angle2) > math.pi:
            bisect_angle = (bisect_angle + math.pi) % (2*math.pi)
        if (bisect_angle < math.pi/2 or bisect_angle > 3*math.pi/2):
            intersects += 1

    return intersects % 2 != 0


def hull_jarvis(points: np.ndarray) -> list[tuple]:
    points_list = points.tolist()
    #print(points_list)

    lowest_p = min(points_list, key=lambda p: p[1])
    points_list.remove(lowest_p)

    # Go up
    hull = [lowest_p]
    while len(points_list) > 0:
        # Lowest angle (+ shortest distance) from last point in hull
        next_p = min(points_list, key=lambda p: (get_angle(hull[-1], p), get_distance_sq(hull[-1], p)))
        if next_p[1] < hull[-1][1]:
            break
        points_list.remove(next_p)
        hull.append(next_p)

    # Go down
    while len(points_list) > 0:
        # Lowest angle (+ shortest distance) from last point in hull

        # angle should not be 0 unless we're at the bottom
        def _down_get_angle_and_distance_sq(last_hull_p, p):
            angle = get_angle(last_hull_p, p)
            if angle == 0 and p[1] != lowest_p[1]:
                print("NOT BOTTOM!", last_hull_p, p)
                return (2*math.pi, get_distance_sq(last_hull_p, p))
            else:
                return (angle, get_distance_sq(last_hull_p, p))

        next_p = min(points_list, key=lambda p: _down_get_angle_and_distance_sq(hull[-1], p))
        if next_p[1] > hull[-1][1]:
            break
        if get_angle(hull[-1], next_p) > get_angle(hull[-1], lowest_p):
            break
        points_list.remove(next_p)
        hull.append(next_p)
    
    return hull
    

def graham_scan(points: list[tuple]):
    start_point = max(points, key=lambda p: p[0])

    i = points.index(start_point)
    went_backwards = False
    while True:
        print("Graham scan points:", points)
        print(points[i], points[(i+1) % len(points)], points[(i+2) % len(points)])
        if (is_left_turn(points[i], points[(i+1) % len(points)], points[(i+2) % len(points)])):
            i = (i+1) % len(points)
        else:
            points.pop((i+1) % len(points))
            if i == points.index(start_point):
                went_backwards = True
            i = (i-1) % len(points)

        if points[(i+1) % len(points)] == start_point:
            #print("Went backwards?:", went_backwards)
            if went_backwards:
                went_backwards = False
            else:
                break

    print("Grahan scan result:", points)
    


def hull_shamos(points: np.ndarray):
    print("Shamos hull for", points.tolist())
    if len(points) <= 2:
        return points.tolist()
    elif len(points) <= 10: 
        return hull_jarvis(points)

    def merge(rotateP: tuple, points1: list[tuple], points2: list[tuple]) -> list[tuple]:
        print("merging", points1, points2)
        mergePoints = []

        i = 0
        i1 = points1.index(min(points1, key=lambda p: get_angle(rotateP, p)))
        i2 = points2.index(min(points2, key=lambda p: get_angle(rotateP, p)))
        i1merged, i2merged = 0, 0

        while i < len(points1) + len(points2):
            if i2merged == len(points2) or (i1merged < len(points1) and 
                    get_angle(rotateP, points1[i1]) < get_angle(rotateP, points2[i2])):
                print("add", points1[i1])
                mergePoints.append(points1[i1])
                i1 = (i1 + 1) % len(points1)
                i1merged += 1
            else:
                print("add", points2[i2])
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

        last_angle = min_angle = max_angle = get_angle(p, hull2[0])
        min_angle_i, max_angle_i = 0, 0
        min_angle_p2 = max_angle_p2 = hull2[0]
        for i in range(1, len(hull2)):
            angle = get_angle(p, hull2[i])

            # these jumps can happen twice during scan
            if angle - last_angle > math.pi and angle - min_angle > math.pi:
                min_angle = angle
                min_angle_i = i
            elif last_angle - angle > math.pi and max_angle - angle > math.pi:
                max_angle = angle
                max_angle_i = i
            elif angle < min_angle and min_angle - angle < math.pi:
                min_angle = angle
                min_angle_i = i
            elif angle > max_angle and angle - max_angle < math.pi:
                max_angle = angle
                max_angle_i = i
            last_angle = angle

        min_angle_p2 = hull2[min_angle_i]
        print("Min. angle:", min_angle_p2)
        max_angle_p2 = hull2[max_angle_i]
        print("Max. angle:", max_angle_p2)

        split_smaller_i = min(min_angle_i, max_angle_i)
        split_bigger_i = max(min_angle_i, max_angle_i)

        hull2_half1 = []
        for i in range(split_smaller_i, split_bigger_i + 1):
            hull2_half1.append(hull2[i])

        hull2_half2 = []
        for i in it.chain(range(split_bigger_i, len(hull2)), range(0, split_smaller_i + 1)):
            hull2_half2.append(hull2[i])

        # Check if half1 is closer to p
        # Cut a line from min_angle_p2 to max_angle_p2 and check if a point on half1 is on the same side of the line as p
        if (hull2_half1[1] == min_angle_p2 or hull2_half1[1] == max_angle_p2 or 
                is_left_turn(p, min_angle_p2, max_angle_p2) == is_left_turn(hull2_half1[1], min_angle_p2, max_angle_p2)):
            hull2_outer = hull2_half2
        else:
            hull2_outer = hull2_half1

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
