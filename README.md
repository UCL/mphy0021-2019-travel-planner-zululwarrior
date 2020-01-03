# travel planner

This is a library that takes a route csv and a passengers csv file and calculates the travel distances/time for the passengers in the route

## Installation

Browse to the directory of this file and run:

```bash
pip install .
```

## Usage

An example of a usage would be:

```python
from travelplanner import Passenger, Route, Journey

john = Passenger(start=(0,2), end=(8,1), speed=15)
mary = Passenger(start=(0,0), end=(6,2), speed=12)
route = Route("route.csv")
journey = Journey(route, [mary, john])
```

```bash
$ bussimula route.csv passenger.csv --speed 10 --saveplots
```
