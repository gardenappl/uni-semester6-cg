import sys
import pprint
from enum import Enum

import matplotlib.pyplot as plt


def is_left_turn(p1: tuple, p2: tuple, p3: tuple) -> bool:
    return ((p2[0] - p1[0])*(p3[1] - p1[1])) - ((p2[1] - p1[1])*(p3[0] - p1[0])) >= 0


def get_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


#
# only works for upper half of hull
#

class CurveNode:
    def __init__(self, p, own_curve, join_index = -1, parent = None, left = None, right = None):
        self.p = p
        self.own_curve = own_curve
        self.join_index = join_index
        self.parent = parent
        self.left = left
        self.right = right

    def __str__(self):
        return self._str_recursive(0)

    def _str_recursive(self, level):
        res = '\t' * level
        res += "{}, own curve: {}, join index: {}\n".format(self.p, self.own_curve, self.join_index)

        if (self.left):
            res += '\t' * level
            res += "Left:\n"
            res += self.left._str_recursive(level + 1)

        if (self.right):
            res += '\t' * level
            res += "Right:\n"
            res += self.right._str_recursive(level + 1)
        return res

    def is_leaf(self):
        return self.join_index == -1


def get_join_indices(i1, i2, chain1, chain2):
    #print("join", i1, i2, chain1, chain2)
    CONCAVE = 0
    CONVEX = 1
    TANGENT = 2

    p1 = chain1[i1]
    p2 = chain2[i2]
    if i1 == 0 or is_left_turn(p2, p1, chain1[i1 - 1]):
        if i1 == len(chain1) - 1 or is_left_turn(p2, p1, chain1[i1 + 1]):
            status1 = TANGENT
        else:
            status1 = CONCAVE
    else:
        status1 = CONVEX

    if i2 == len(chain2) - 1 or not is_left_turn(p1, p2, chain2[i2 + 1]):
        if i2 == 0 or not is_left_turn(p1, p2, chain2[i2 - 1]):
            status2 = TANGENT
        else:
            status2 = CONCAVE
    else:
        status2 = CONVEX
    #print("status", status1, status2)

    if status1 == TANGENT and status2 == TANGENT:
        return (i1, i2)

    if status1 != CONCAVE:
        i1 = i1 // 2
    elif status2 == TANGENT:
        i1 += (len(chain1) - i1) // 2

    if status2 != CONCAVE:
        i2 += (len(chain2) - i2) // 2
    elif status1 == TANGENT:
        i2 = i2 // 2

    if status1 == CONCAVE and status2 == CONCAVE:
        p = get_intersection((p1, chain1[i1 + 1]), (p2, chain2[i2 - 1]))

        if p[0] > chain1[-1].p[0]:
            i2 = i2 // 2
        else:
            i1 += (len(chain2) - i2) // 2

    return get_join_indices(i1, i2, chain1, chain2)


def insert(root_node: CurveNode, p):
    node_curves = { root_node: root_node.own_curve }
    def print_node_curves():
        for node, curve in node_curves.items():
            print(" -- {} (left: {}, right: {}): {}".format(node.p, None if node.left is None else node.left.p,
                None if node.right is None else node.right.p, curve))

    def go_down(node, p):
        if node.is_leaf():
            return node

        curve = node_curves[node]
        chain1 = curve[:node.join_index + 1]
        chain2 = curve[node.join_index + 1:]

        node_curves[node.left] = chain1 + node.left.own_curve
        node_curves[node.right] = node.right.own_curve.copy() + chain2
        if (p[0] <= node.p[0]):
            return go_down(node.left, p)
        else:
            return go_down(node.right, p)

    print("going down")
    print_node_curves()
    print(root_node)

    found_leaf_node = go_down(root_node, p)

    if (p[0] <= found_leaf_node.p[0]):
        leaf_value = found_leaf_node.p
        found_leaf_node.p = p
        found_leaf_node.left = CurveNode(p, [], parent=found_leaf_node)
        found_leaf_node.right = CurveNode(leaf_value, [], parent=found_leaf_node)
    else:
        found_leaf_node.left = CurveNode(found_leaf_node.p, [], parent=found_leaf_node)
        found_leaf_node.right = CurveNode(p, [], parent=found_leaf_node)

    node_curves[found_leaf_node.left] = [ found_leaf_node.left.p ]
    node_curves[found_leaf_node.right] = [ found_leaf_node.right.p ]
    
    print("went down")
    print_node_curves()
    print(root_node)

    def go_up(node):
        if node == root_node:
            root_node.own_curve = node_curves[root_node]
            return

        node1 = node.parent.left
        node2 = node.parent.right
        join_i1, join_i2 = get_join_indices(0, 0, node_curves[node1], node_curves[node2])
        node1.own_curve = node_curves[node1][join_i1 + 1:]
        node2.own_curve = node_curves[node2][:join_i2]

        node_curves[node.parent] = node_curves[node1][:join_i1 + 1] + node_curves[node2][join_i2:]
        node.parent.join_index = join_i1

        go_up(node.parent)

    go_up(found_leaf_node.left if found_leaf_node.left.p == p else found_leaf_node.right)

    print("went up")
    print_node_curves()
    print(root_node)

    return node_curves[root_node]
        

points = []

with open('points.txt') as points_file:
    for line in points_file:
        points.append([int(num) for num in line.split()])

root = CurveNode(points[0], [])

for i in range(1, len(points)):
    points_x, points_y = zip(*points[:i + 1])

    plt.plot(points_x, points_y, 'ro')
    plt.grid()

    hull_points = insert(root, points[i])

    print("Hull points:", hull_points)

    prev_point = None
    for hull_point in hull_points:
        if prev_point:
            plt.plot([prev_point[0], hull_point[0]], [prev_point[1], hull_point[1]])
        prev_point = hull_point

    plt.show()
