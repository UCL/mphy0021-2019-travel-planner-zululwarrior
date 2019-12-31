import math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

route = [(2, 1, 'A'), (3, 1, ''), (4, 1, ''), (5, 1, ''),
         (6, 1, ''), (7, 1, 'B'), (7, 2, ''), (8, 2, ''),
         (9, 2, ''), (10, 2, ''), (11, 2, 'C'), (11, 1, ''),
         (12, 1, ''), (13, 1, ''), (14, 1, ''), (14, 2, 'D'),
         (14, 3, ''), (14, 4, ''), (13, 4, ''), (12, 4, ''),
         (11, 4, ''), (10, 4, ''), (9, 4, ''), (9, 5, 'E'),
         (9, 6, ''), (10, 6, ''), (11, 6, 'F'), (12, 6, ''),
         (13, 6, ''), (14, 6, ''), (15, 6, ''), (16, 6, 'G')]

passengers = {1: [(0, 2), (8, 1), 15],
              2: [(0, 0), (6, 2), 12],
              3: [(5, 2), (15, 4), 16],
              4: [(4, 5), (9, 7), 20],
              }


class Passenger:
    def __init__(self, start, end, speed):
        self.start = start
        self.end = end
        self.speed = speed

    def walk_time(self):
        walking_time = math.sqrt(
            (self.end[0] - self.start[0])**2 + (self.end[1] - self.start[1]**2)) * self.speed
        return walking_time


class Route:
    def __init__(self, file_name):
        self.file_name = file_name

        DIR = Path(__file__).parent
        route_csv = np.genfromtxt(
            DIR / file_name, delimiter=(','), dtype=(int, int, 'U10'), encoding=None)

        route = [(int(x), int(y), stop.replace("'", ""))
                 for x, y, stop in route_csv]
        self.route = route

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
            time += 10
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
            cc.append(str(freeman_coord2cc[(x_step, y_step)]))
        return start, ''.join(cc)


class Journey:
    def __init__(self, route, passengers):
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
        if((distance * passenger.speed) <= (bus_travel + walk_travel)):
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
        print("Average time on bus: ", total_bus/(id), " min")
        print("Average walking time: ", total_walk/(id), " min")


def timetable(route):
    '''
    Generates a timetable for a route as minutes from its first stop.
    '''
    time = 0
    stops = {}
    for step in route:
        if step[2]:
            stops[step[2]] = time
        time += 10
    return stops


def passenger_trip(passenger, route):
    start, end, pace = passenger
    stops = [value for value in route if value[2]]
    # calculate closer stops
    # to start
    distances = [(math.sqrt((x - start[0])**2 +
                            (y - start[1])**2), stop) for x, y, stop in stops]
    closer_start = min(distances)
    # to end
    distances = [(math.sqrt((x - end[0])**2 +
                            (y - end[1])**2), stop) for x, y, stop in stops]
    closer_end = min(distances)
    return (closer_start, closer_end)


def passenger_trip_time(passenger, route):
    walk_distance_stops = passenger_trip(passenger, route)
    bus_times = timetable(route)
    bus_travel = bus_times[walk_distance_stops[1][1]] - \
        bus_times[walk_distance_stops[0][1]]
    walk_travel = walk_distance_stops[0][0] * passenger[2] + \
        walk_distance_stops[1][0] * passenger[2]
    return bus_travel + walk_travel


def plot_map(route):
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


def plot_bus_load(route, passengers):
    stops = {step[2]: 0 for step in route if step[2]}
    for passenger in passengers.values():
        trip = passenger_trip(passenger, route)
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


'''
print(" Stops: minutes from start\n", timetable(route))
for passenger_id, passenger in passengers.items():
    print(f"Trip for passenger: {passenger_id}")
    start, end = passenger_trip(passenger, route)
    total_time = passenger_trip_time(passenger, route)
    print((f" Walk {start[0]:3.2f} units to stop {start[1]}, \n"
           f" get on the bus and alite at stop {end[1]} and \n"
           f" walk {end[0]:3.2f} units to your destination."))
    print(f" Total time of travel: {total_time:03.2f} minutes")
'''
# Plots the route of the bus
# plot_map(route)
# Plots the number of passenger on the bus
# plot_bus_load(route, passengers)


def route_cc(route):
    '''
    Converts a set of route into a Freeman chain code
        3 2 1
        \ | /
    4 - C - 0
        / | \
        5 6 7
    '''
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
        cc.append(str(freeman_coord2cc[(x_step, y_step)]))
    return start, ''.join(cc)


def read_passengers(file):
    DIR = Path(__file__).parent
    passengers_list = []
    passengers = np.genfromtxt(DIR / file, delimiter=(','), dtype=int)
    for x, y, x1, y1, pace in passengers:
        passengers_list.append(((x, y), (x1, y1), pace))
    return passengers_list


start_point, cc = route_cc(route)
print((f"The bus route starts at {start_point} and\n"
       f"it's described by this chain code:\n{cc}"))
