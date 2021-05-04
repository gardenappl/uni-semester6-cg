import bisect
import sys
import math
import pprint
from enum import Enum

import matplotlib.pyplot as plt


def is_left_turn(p1: tuple, p2: tuple, p3: tuple) -> bool:
    return ((p2[0] - p1[0])*(p3[1] - p1[1])) - ((p2[1] - p1[1])*(p3[0] - p1[0])) >= 0


def get_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


class Edge:
    def __init__(self, in_p, out_p, weight=1):
        self.in_p = in_p
        self.out_p = out_p
        self.weight = weight


class RegularGraph:
    def __init__(self, points: list[tuple]):
        self.out_edges = {} # vertices going out of point
        self.in_edges = {}
        self.points = sorted(points, key=lambda p: (p[1], p[0]))


    def add_edge(self, p1, p2):
        e = Edge(p1, p2)
        if p1 not in self.out_edges:
            self.out_edges[p1] = []
        self.out_edges[p1].append(e)

        if p2 not in self.in_edges:
            self.in_edges[p2] = []
        self.in_edges[p2].append(e)


    def sort_edges(self):
        for p in self.out_edges:
            self.out_edges[p].sort(key=lambda edge: get_angle(p, edge.out_p), reverse=True)

        for p in self.in_edges:
            self.in_edges[p].sort(key=lambda edge: get_angle(p, edge.in_p))


def stripes_method_balancing(graph: RegularGraph):
    print("Moving up...", file=sys.stderr)

    for i in range(1, len(graph.points) - 1):
        p = graph.points[i]
        weight_in = 0
        for edge in graph.in_edges[p]:
            weight_in += edge.weight

        weight_out = 0
        for edge in graph.out_edges[p]:
            weight_out += edge.weight

        if weight_in > weight_out:
            graph.out_edges[p][0].weight += weight_in - weight_out
            print("Add {} to [{}, {}]".format(weight_in - weight_out, p, graph.out_edges[p][0].out_p),
                    file=sys.stderr)

    print("Moving down...", file=sys.stderr)

    # move down
    for i in range(len(graph.points) - 2, 0, -1):
        p = graph.points[i]
        weight_out = 0
        for edge in graph.out_edges[p]:
            weight_out += edge.weight

        weight_in = 0
        for edge in graph.in_edges[p]:
            weight_in += edge.weight

        if weight_out > weight_in:
            graph.in_edges[p][0].weight += weight_out - weight_in
            print("Add {} to [{}, {}]".format(weight_out - weight_in, p, graph.in_edges[p][0].in_p),
                    file=sys.stderr)
    return


def make_chains(graph: RegularGraph):
    chains = []

    p0 = graph.points[0]
    for start_edge in graph.out_edges[p0]:
        while start_edge.weight > 0:
            # Make one chain
            chain = [p0]
            p = p0
            # While p is not the top point
            while p in graph.out_edges:
                for edge in graph.out_edges[p]:
                    if edge.weight > 0:
                        edge.weight -= 1
                        chain.append(edge.out_p)
                        p = edge.out_p
                        break
            chains.append(chain)

    return chains


def locate_point(p: tuple[float, float], chains: list[list[tuple]]):

    def is_chain_to_the_left(p: tuple[float, float], chain: list[tuple]):
        start = 0
        end = len(chain) - 1
        while True:
            i = (end + start) // 2
            p_low = chain[i]
            p_high = chain[i + 1]

            if p_low[1] <= p[1] and p[1] <= p_high[1]:
                return is_left_turn(p_low, p, p_high)
            elif p[1] < p_low[1]:
                if i == 0:
                    print("Point is below", file=sys.stderr)
                    return None
                end = i
            else:
                if i + 1 == len(chain) - 1:
                    print("Point is above", file=sys.stderr)
                    return None
                start = i


    start = 0
    end = len(chains) - 1
    while True:
        i = (end + start) // 2
        #print("Start: {}, end: {}, i: {}".format(start, end, i))
        c_left = chains[i]
        c_right = chains[i + 1]

        c_left_is_to_the_left = is_chain_to_the_left(p, c_left)
        #print("Left is to the left?:", c_left_is_to_the_left)
        if c_left_is_to_the_left is None:
            return None

        if c_left_is_to_the_left and not is_chain_to_the_left(p, c_right):
            return (c_left, c_right)
        elif c_left_is_to_the_left:
            if i + 1 == len(chains) - 1:
                print("Point is to the right", file=sys.stderr)
                return None
            start = i
        else:
            if i == 0:
                print("Point is to the left", file=sys.stderr)
                return None
            end = i


edges = []
points = []
x, y = [float(arg) for arg in sys.argv[-2:]]

with open('points.txt') as points_file:
    for line in points_file:
        points.append(tuple([int(num) for num in line.split()]))

with open('edges.txt') as edges_file:
    for line in edges_file:
        edges.append([int(num) for num in line.split()])


graph = RegularGraph(points)
for e in edges:
    graph.add_edge(points[e[0]], points[e[1]])

graph.sort_edges()
stripes_method_balancing(graph)


def draw(graph, draw_weight):
    points_x, points_y = zip(*graph.points)

    plt.plot(points_x, points_y, 'ro')
    plt.grid()

    for p in graph.out_edges:
        for edge in graph.out_edges[p]:
            plt.plot([p[0], edge.out_p[0]], [p[1], edge.out_p[1]])
            if draw_weight:
                plt.text((p[0] + edge.out_p[0]) / 2, (p[1] + edge.out_p[1]) / 2, str(edge.weight))

    plt.show()


draw(graph, True)

chains = make_chains(graph)
for chain in chains:
    print(chain)


location = locate_point((x, y), chains)
if location is not None:
    print("Left:", location[0])
    print("Right:", location[1])

draw(graph, False)
