from ..travelplanner import Passenger, Route, Journey
import numpy as np
import math
import pytest
from pathlib import Path

DIR = Path(__file__).parent


@pytest.fixture
def write_file():
    f = open(DIR / "route.csv", "w")
    f.write("10,8,A\n10,9,\n10,10,\n10,11,\n9,11,\n8,11,\n7,11,\n7,10,\n7,9,\n6,9,\n5,9,\n4,9,\n3,9,\n2,9,\n2,8,\n2,7,\n2,6,B\n2,5,\n2,4,\n2,3,\n2,2,\n2,1,\n1,1,\n0,1,\n0,2,\n0,3,C\n")
    f.close()


@pytest.fixture
def passengers():
    john = Passenger(start=(0, 2), end=(8, 1), speed=15)
    mary = Passenger(start=(9, 8), end=(2, 4), speed=23)
    connor = Passenger(start=(10, 8), end=(1, 2), speed=28)
    return [john, mary, connor]


def test_constructor_input():
    with pytest.raises(TypeError) as e:
        p = Passenger((1, 1), (2, 1), 1.1)

    with pytest.raises(ValueError) as e:
        p = Passenger((1, 1), (2, 1), -1)

    with pytest.raises(TypeError) as e:
        p = Passenger(1, (2, 1), 5)

    with pytest.raises(TypeError) as e:
        p = Passenger((1, 1), 1, 5)

    with pytest.raises(TypeError) as e:
        r = Route(123)

    with pytest.raises(TypeError) as e:
        r = Route("route.csv", "12")

    with pytest.raises(ValueError) as e:
        r = Route("route.csv", -10)

    with pytest.raises(TypeError) as e:
        p = Passenger((1, 1), (1, 2), 5)
        j = Journey("route", [p])

    with pytest.raises(TypeError) as e:
        p = Passenger((1, 1), (1, 2), 5)
        r = Route("route.csv")
        j = Journey(r, p)


def test_walk_time():
    p = Passenger((1, 1), (5, 8), 10)
    expected = math.sqrt((1-5)**2 + (1-8)**2) * 10
    walk_time = p.walk_time()
    assert walk_time == pytest.approx(expected, 0.01)


def test_timetable(write_file):

    # test without speed
    r = Route(DIR / "route.csv")
    result = r.timetable()
    expected = {'A': 0, 'B': 160, 'C': 250}
    assert result == expected

    # test with speed
    r = Route(DIR / "route.csv", 20)
    result = r.timetable()
    expected = {'A': 0, 'B': 320, 'C': 500}
    assert result == expected


def test_travel_time(write_file, passengers):

    route = Route(DIR / "route.csv")
    journey = Journey(route, passengers)

    # test without speed
    id = 0
    results = []
    for passenger in journey.passengers:
        results.append(journey.travel_time(id))
        id += 1

    expected = [{'bus': 0, 'walk': 120.93386622447824}, {
        'bus': 0, 'walk': 185.43192821086663}, {'bus': 250, 'walk': 39.59797974644666}]

    assert expected == results

    route = Route(DIR / "route.csv", 5)
    journey = Journey(route, passengers)

    # test with speed
    id = 0
    results = []
    for passenger in journey.passengers:
        results.append(journey.travel_time(id))
        id += 1

    expected = [{'bus': 0, 'walk': 120.93386622447824}, {
        'bus': 80, 'walk': 69.0}, {'bus': 125, 'walk': 39.59797974644666}]

    assert expected == results


def test_print_time_stats(capsys, write_file, passengers):

    route = Route(DIR / "route.csv")
    journey = Journey(route, passengers)

    # test without speed
    journey.print_time_stats()
    result = capsys.readouterr()
    expected = (
        "Average time on bus: 83.33333333333333 min\nAverage walking time: 115.32125806059717 min\n")
    assert result.out == expected

    route = Route(DIR / "route.csv", 5)
    journey = Journey(route, passengers)

    # test with speed
    journey.print_time_stats()
    result = capsys.readouterr()

    expected = (
        "Average time on bus: 68.33333333333333 min\nAverage walking time: 76.51061532364163 min\n")
    assert result.out == expected


def test_generate_cc(capsys, write_file):

    # test without speed
    route = Route(DIR / "route.csv")

    result = route.generate_cc()
    expected = ((10, 8), '6664442244444222222224466')
    assert result == expected

    # test with speed
    route = Route(DIR / "route.csv", 5)

    result = route.generate_cc()
    expected = ((10, 8), '6664442244444222222224466')
    assert result == expected

    # test invalid route without speed
    f = open(DIR / "route.csv", "w")
    f.write("10,8,A\n11,9,\n10,10,\n10,11,\n9,11,\n8,11,\n7,11,\n7,10,\n7,9,\n6,9,\n5,9,\n4,9,\n3,9,\n2,9,\n2,8,\n2,7,\n2,6,B\n2,5,\n2,4,\n2,3,\n2,2,\n2,1,\n1,1,\n0,1,\n0,2,\n0,3,C\n")
    f.close()
    with pytest.raises(ValueError) as e:
        route = Route(DIR / "route.csv")
        route.generate_cc()

    # test invalid route with speed
    with pytest.raises(ValueError) as e:
        route = Route(DIR / "route.csv", 5)
        route.generate_cc()
