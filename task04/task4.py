import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sys


class Node:
    def __init__(self, x, y, split_horizontal = None, left_down = None, right_up = None):
        self.x = x
        self.y = y
        self.split_horizontal = split_horizontal
        self.left_down = left_down
        self.right_up = right_up

    def __str__(self):
        return self._str_recursive(0)

    def _str_recursive(self, level):
        res = '\t' * level
        res += "Horizontal" if self.split_horizontal else "Vertical"
        res += " split at ({}; {}):\n".format(self.x, self.y)

        if (self.left_down):
            res += '\t' * level
            res += "Left:\n" if self.split_horizontal else "Down:\n"
            res += self.left_down._str_recursive(level + 1)

        if (self.right_up):
            res += '\t' * level
            res += "Right:\n" if self.split_horizontal else "Up:\n"
            res += self.right_up._str_recursive(level + 1)
        return res


    @staticmethod
    def make_tree(points, split_horizontal=True):
        if (len(points) == 0):
            return None
        elif (len(points) == 1):
            return Node(points[0][0], points[0][1])

        # Lazy way to find median, could be done in O(n) time instead
        points.sort(key=lambda p : p[0] if split_horizontal else p[1])

        mid = int(len(points) / 2)
        node = Node(points[mid][0], points[mid][1], split_horizontal)

        node.left_down = Node.make_tree(points[:mid], not split_horizontal)
        node.right_up = Node.make_tree(points[mid + 1:], not split_horizontal)

        return node


    def _find_points_recursive(self, x, y, width, height, found):
        if (self.x >= x and self.x <= x + width
                and self.y >= y and self.y <= y + height):
            found.append([self.x, self.y])

        if (self.split_horizontal):
            if (self.left_down and self.y >= y):
                self.left_down._find_points_recursive(x, y, width, height, found)
            if (self.right_up and self.y <= y + height):
                self.right_up._find_points_recursive(x, y, width, height, found)
        else:
            if (self.left_down and self.x >= x):
                self.left_down._find_points_recursive(x, y, width, height, found)
            if (self.right_up and self.x <= x + width):
                self.right_up._find_points_recursive(x, y, width, height, found)


    def find_points(self, x, y, width, height):
        found = []
        self._find_points_recursive(x, y, width, height, found)
        return found



points = []

with open('points.txt') as points_file:
    for line in points_file:
        points.append([int(num) for num in line.split()])


tree = Node.make_tree(points)

# Search inside rectangle given by program args
x, y, width, height = [int(arg) for arg in sys.argv[-4:]]

print(str(tree))
print(tree.find_points(x, y, width, height))

points_x, points_y = zip(*points)

fig, ax = plt.subplots()
ax.plot(points_x, points_y, 'ro')
ax.grid()
ax.add_patch(Rectangle((x, y), width, height))
plt.show()
