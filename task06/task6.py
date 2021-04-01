import matplotlib.pyplot as plt
import sys
import math
import numpy as np
import itertools as it


def get_angle(p1, p2):
    return (math.atan2(p2[1]-p1[1], p2[0]-p1[0]) % (2*math.pi))


def get_distance(p1, p2):
    return math.sqrt((p2[0]-p1[0])*(p2[0]-p1[0]) + (p2[1]-p1[1])*(p2[1]-p1[1]))


def get_line_intersection(p1, p2, p3, p4):
    def line(p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0]*p2[1] - p2[0]*p1[1])
        return A, B, -C

    L1 = line(p1, p2)
    L2 = line(p3, p4)

    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False


def get_line_segment_intersection(p1, p2, p3, p4):
    p = get_line_intersection(p1, p2, p3, p4)
    #print("Intersection between {}, {} and {}, {} is {}".format(p1, p2, p3, p4, p))
    if p and ((p[0] < p3[0] and p[0] < p4[0]) or (p[0] > p3[0] and p[0] > p4[0]) 
            or (p[1] < p3[1] and p[1] < p4[1]) or (p[1] > p3[1] and p[1] > p4[1])):
        #print("...not really")
        return False
    return p


def get_distance_to_chain(p, points):
    bisector_angle = (get_angle(p, points[0]) + get_angle(p, points[-1])) / 2
    p2 = [p[0] + math.cos(bisector_angle), p[1] + math.sin(bisector_angle)]
    for i in range(1, len(points)):
        intersection = get_line_segment_intersection(p, p2, points[i-1], points[i])
        if intersection:
            return get_distance(p, intersection)
    raise RuntimeError()


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
        if ((angle1 + angle2) / 2 < math.pi/2 or (angle1 + angle2) / 2 > 3*math.pi/2):
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

        #next_p = min(points_list, key=lambda p: _down_get_angle(hull, p))
        next_p = min(points_list, key=lambda p: get_angle(hull[-1], p))
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
    elif len(points) <= 8: 
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
        #print("Min. angle p2:", min_angle_p2)
        max_angle_p2 = max(hull2, key=lambda p2: get_angle(p, p2))
        #print("Max. angle p2:", max_angle_p2)

        min_angle_i = hull2.index(min_angle_p2)
        max_angle_i = hull2.index(max_angle_p2)

        split_smaller_i = min(min_angle_i, max_angle_i)
        split_bigger_i = max(min_angle_i, max_angle_i)

        hull2_half1 = []
        hull2_half1_dist, hull2_half1_count = 0, 0
        for i in range(split_smaller_i, split_bigger_i + 1):
            hull2_half1.append(hull2[i])
            hull2_half1_dist += get_distance(p, hull2[i])
            hull2_half1_count += 1

        hull2_half2 = []
        hull2_half2_dist, hull2_half2_count = 0, 0
        for i in it.chain(range(split_bigger_i, len(hull2)), range(0, split_smaller_i + 1)):
            hull2_half2.append(hull2[i])
            hull2_half2_dist += get_distance(p, hull2[i])
            hull2_half2_count += 1

        hull2_outer = hull2_half1 if (get_distance_to_chain(p, hull2_half1) > get_distance_to_chain(p, hull2_half2)) else hull2_half2

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
