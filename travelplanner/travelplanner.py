import math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


class Passenger:
    def __init__(self, start, end, speed):
        if not isinstance(speed, int):
            raise TypeError("Speed must be an int")
        if speed <= 0:
            raise ValueError("Speed cannot be equal or less than 0")
        if not isinstance(start, tuple):
            raise TypeError("Start must be a tuple of 2 ints e.g. (1,1)")
        if not isinstance(end, tuple):
            raise TypeError("End must be a tuple of 2 ints e.g. (1,1)")
        if list(map(type, start)) != [int, int]:
            raise TypeError("Start must be a tuple of 2 ints e.g. (1,1)")
        if list(map(type, end)) != [int, int]:
            raise TypeError("End must be a tuple of 2 ints e.g. (1,1)")
        self.start = start
        self.end = end
        self.speed = speed

    def walk_time(self):
        '''Returns walking time of passenger
        >>> p = Passenger((1, 1), (5, 8), 10)
        >>> print(p.walk_time())
        80.62257748298549
        '''
        walking_time = math.sqrt(
            (self.end[0] - self.start[0])**2 + (self.end[1] - self.start[1])**2) * self.speed
        return walking_time


class Route:
    def __init__(self, file_name, speed=None):
        if not isinstance(file_name, type(Path(__file__))) and not isinstance(file_name, str):
            raise TypeError("File name must be a string or a path")

        self.file_name = file_name
        DIR = Path(__file__).parent
        route_csv = np.genfromtxt(
            DIR / file_name, delimiter=(','), dtype=(int, int, 'U10'), encoding=None)

        route = [(int(x), int(y), stop.replace("'", ""))
                 for x, y, stop in route_csv]
        self.route = route
        self.speed = speed if speed is not None else 10

        if not isinstance(self.speed, int):
            raise TypeError("Speed must be an int")
        if self.speed <= 0:
            raise ValueError("Speed cannot be equal or less than 0")
        self.generate_cc()

    def plot_map(self):
        route = self.route
        max_x = max([n[0] for n in route]) + 5  # adds padding
        max_y = max([n[1] for n in route]) + 5
        grid = np.zeros((max_y, max_x))
        for x, y, stop in route:
            grid[y, x] = 1
            if stop:
                grid[y, x] += 1
        fig, ax = plt.subplots(1, 1)
        ax.pcolor(grid)
        ax.invert_yaxis()
        ax.set_aspect('equal', 'datalim')
        plt.show()

    def timetable(self):
        route = self.route
        time = 0
        stops = {}
        for step in route:
            if step[2]:
                stops[step[2]] = time
            time += self.speed
        return stops

    def generate_cc(self):
        route = self.route
        start = route[0][:2]
        cc = []
        freeman_cc2coord = {0: (1, 0),
                            1: (1, -1),
                            2: (0, -1),
                            3: (-1, -1),
                            4: (-1, 0),
                            5: (-1, 1),
                            6: (0, 1),
                            7: (1, 1)}
        freeman_coord2cc = {val: key for key, val in freeman_cc2coord.items()}
        for b, a in zip(route[1:], route):
            x_step = b[0] - a[0]
            y_step = b[1] - a[1]
            if freeman_coord2cc[(x_step, y_step)] not in (0, 2, 4, 6):
                raise ValueError(
                    "Invalid route, bus can only move horizontally or vertically")
            cc.append(str(freeman_coord2cc[(x_step, y_step)]))
        return start, ''.join(cc)


class Journey:
    def __init__(self, route, passengers):
        if not isinstance(route, Route):
            raise TypeError("1st argument must be of type route")
        if not isinstance(passengers, list):
            raise TypeError("2nd argument must be a list of type passenger")
        if not all(isinstance(passenger, Passenger) for passenger in passengers):
            raise TypeError("2nd argument must of a list of type passenger")
        self.route = route
        self.passengers = passengers

    def passenger_trip(self, passenger):
        stops = [value for value in self.route.route if value[2]]
        # calculate closer stop
        # to start
        closer_start = ((stops[0][0], stops[0][1]), stops[0][2])
        min_distance = math.sqrt((stops[0][0] - passenger.start[0])**2 +
                                 (stops[0][1] - passenger.start[1])**2)
        for x, y, stop in stops:
            distance = (math.sqrt((x - passenger.start[0])**2 +
                                  (y - passenger.start[1])**2))
            if (distance < min_distance):
                closer_start = ((x, y), stop)
                min_distance = distance
            elif (distance == min_distance):
                prev_dist = math.sqrt((passenger.end[0] - closer_start[0][0])
                                      ** 2 + (passenger.end[1] - closer_start[0][1])**2)
                next_dist = math.sqrt((passenger.end[0] - x) **
                                      2 + (passenger.end[1] - y)**2)
                if(prev_dist > next_dist):
                    closer_start = ((x, y), stop)
                    min_distance = distance
                else:
                    closer_start = closer_start
        closer_start = (math.sqrt((passenger.start[0] - closer_start[0][0])
                                  ** 2 + (passenger.start[1] - closer_start[0][1])**2), closer_start[1])
        # to end
        closer_end = ((stops[0][0], stops[0][1]), stops[0][2])
        min_distance = math.sqrt((stops[0][0] - passenger.end[0])**2 +
                                 (stops[0][1] - passenger.end[1])**2)
        for x, y, stop in stops:
            distance = (math.sqrt((x - passenger.end[0])**2 +
                                  (y - passenger.end[1])**2))
            if (distance < min_distance):
                closer_end = ((x, y), stop)
                min_distance = distance
            elif (distance == min_distance):
                prev_dist = math.sqrt((passenger.start[0] - closer_end[0][0])
                                      ** 2 + (passenger.start[1] - closer_end[0][1])**2)
                next_dist = math.sqrt((passenger.start[0] - x) **
                                      2 + (passenger.start[1] - y)**2)
                if(prev_dist > next_dist):
                    closer_end = ((x, y), stop)
                    min_distance = distance
                else:
                    closer_end = closer_end
        closer_end = (math.sqrt((passenger.end[0] - closer_end[0][0])
                                ** 2 + (passenger.end[1] - closer_end[0][1])**2), closer_end[1])
        return (closer_start, closer_end)

    def plot_bus_load(self):
        stops = {step[2]: 0 for step in self.route.route if step[2]}
        for passenger in self.passengers:
            trip = self.passenger_trip(passenger)
            stops[trip[0][1]] += 1
            stops[trip[1][1]] -= 1
        for i, stop in enumerate(stops):
            if i > 0:
                stops[stop] += stops[prev]
            prev = stop
        fig, ax = plt.subplots()
        ax.step(range(len(stops)), list(stops.values()), where='post')
        ax.set_xticks(range(len(stops)))
        ax.set_xticklabels(list(stops.keys()))
        plt.show()

    def travel_time(self, id):
        passenger = self.passengers[id]
        walk_distance_stops = self.passenger_trip(passenger)
        bus_times = self.route.timetable()
        bus_travel = bus_times[walk_distance_stops[1][1]] - \
            bus_times[walk_distance_stops[0][1]]
        walk_travel = walk_distance_stops[0][0] * passenger.speed + \
            walk_distance_stops[1][0] * passenger.speed
        distance = math.sqrt((passenger.end[0] - passenger.start[0])**2 +
                             (passenger.end[1] - passenger.start[1])**2)
        if((distance * passenger.speed) <= (bus_travel + walk_travel) or bus_travel < 0):
            bus_travel = 0
            walk_travel = distance * passenger.speed
        travel_dict = {"bus": bus_travel,
                       "walk": walk_travel}
        return travel_dict

    def print_time_stats(self):
        id = 0
        total_bus = 0
        total_walk = 0
        for passenger in self.passengers:
            travel_dict = self.travel_time(id)
            total_bus = travel_dict["bus"] + total_bus
            total_walk = travel_dict["walk"] + total_walk
            id += 1
        print("Average time on bus:", total_bus/(id),
              "min\nAverage walking time:", total_walk/(id), "min")


def read_passengers(file):
    DIR = Path(__file__).parent
    passengers_list = []
    passengers = np.genfromtxt(DIR / file, delimiter=(','), dtype=int)
    for x, y, x1, y1, pace in passengers:
        passengers_list.append(((x, y), (x1, y1), pace))
    return passengers_list


if __name__ == "__main__":
    import doctest
    doctest.testmod()
