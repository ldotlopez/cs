import collections
import csv
import sys
import matplotlib.pyplot as plt


Station = collections.namedtuple('Station', ['id', 'name', 'states'])
State = collections.namedtuple('State', [
    'station', 'timestamp', 'ocupation', 'capacity'])


def plot(station, timespan):
    states = list(sorted(station.states, key=lambda x: x.timestamp))
    plt.plot(
        [state.timestamp for state in states],
        [state.ocupation for state in states])
    import ipdb; ipdb.set_trace(); pass
    plt.axis([states[0].timestamp, states[-1].timestamp, 0, max([state.ocupation for state in states])])
    plt.show()


stations = {}
span = [sys.maxsize, -sys.maxsize]

with open('data.csv') as fh:
    reader = csv.reader(fh, delimiter=',', quotechar="'")
    for row in reader:
        try:
            (ts, station_id, name, lat, lng, ocupation, capacity) = row
        except ValueError:
            print(row)
            continue

        ts = int(ts)
        if ts < span[0]:
            span[0] = ts

        if ts > span[1]:
            span[1] = ts

        ocupation = int(ocupation)
        capacity = int(capacity)

        if station_id not in stations:
            stations[station_id] = Station(id=station_id, name=name, states=[])

        stations[station_id].states.append(State(
            station=stations[station_id], timestamp=ts, ocupation=ocupation,
            capacity=capacity))

    plot(stations['34'], span)
