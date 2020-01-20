from argparse import ArgumentParser

from .travelplanner import Passenger, Route, Journey, read_passengers


def process():
    parser = ArgumentParser(
        description="Calculates the path the \
        passenger should take in a given bus route.")
    parser.add_argument("routefile", default="route.csv",
                        help="The input CSV file with a bus route")
    parser.add_argument("passfile", default="passengers.csv",
                        help="The input CSV file with passengers")
    parser.add_argument(
        "--speed", help="The speed of the bus in the route", type=int)
    parser.add_argument(
        "--saveplots", action="store_true",
        help="Displays and saves the map \
            of the route and load of the bus")

    arguments = parser.parse_args()
    passengers = [
        Passenger(start, end, speed)
        for start, end, speed
        in read_passengers(arguments.passfile)
    ]
    if arguments.speed:
        route = Route(arguments.routefile, arguments.speed)
    else:
        route = Route(arguments.routefile)

    journey = Journey(route, passengers)

    print("Stops: minutes from start\n", route.timetable())
    count = 0
    for passenger in passengers:
        print(f"Trip for passenger: {count}")
        print(f" {journey.travel_time(count)}")
        if journey.travel_time(count)["bus"] > 0:
            closerStart, closerEnd = \
                journey.passenger_trip(passenger)
            timeDict = journey.travel_time(count)
            print(
                f" Walk {closerStart[0]:3.2f} units \
                    to stop {closerStart[1]}, \n"
                f" get on the bus and alite at stop {closerEnd[1]} and \n"
                f" walk {closerEnd[0]:3.2f} units to your destination.")
            print(
                f" Total time of travel: \n"
                f"{timeDict['bus'] + timeDict['walk']:3.2f}")
        count += 1

    if arguments.saveplots:
        route.plot_map()
        journey.plot_bus_load()
