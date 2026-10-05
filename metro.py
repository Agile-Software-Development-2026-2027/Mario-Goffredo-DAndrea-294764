import sys
from collections import Counter

# Time horizon for the domain: today

STATIONS = ["garibaldi", "universita", "municipio", "toledo", "dante", "museo", "materdei", "vanvitelli", "augusteo", "fuga", "mergellina", "manzoni"]

cards: set[str] = set() # set of card currently tapped in but not yet tapped out
tap_outs: Counter[str, int] = Counter() # card: number of tap outs
fares: Counter[str, int] = Counter() # card: sum of prices paid at tap out
regulars: dict[str, Counter[str]] = {} # station: count of tap outs per station

# Represent the graph as a set of edges, each can be opened or closed
NETWORK = [
    ("manzoni", "mergellina", True),
    ("materdei", "museo", True),
    ("museo", "dante", True),
    ("dante", "toledo", True),
    ("vanvitelli", "materdei", True),
    ("vanvitelli", "fuga", True),
    ("fuga", "augusteo", True),
    ("augusteo", "toledo", True),
    ("toledo", "municipio", True),
    ("municipio", "universita", True),
    ("universita", "garibaldi", True)
]

def edge_in_network(a, b) -> bool:
    return (a, b, True) in NETWORK or (a, b, False) in NETWORK or (b, a, False) in NETWORK or (b, a, True) in NETWORK

def edge_is_open(a, b) -> bool:
    return (a, b, True) in NETWORK or (b, a, True) in NETWORK

# Check if I did not mistype
for a, b, is_open in NETWORK:
    assert a in STATIONS
    assert b in STATIONS
    assert is_open

def price_of_card(number_of_taps: int):
    match number_of_taps:
        case 0:
            raise ValueError("Number of taps can't be 0")
        case 1 | 2 | 3:
            return 2
        case 4 | 5:
            return 1
        case _:
            return 0


"""To count the regulars we count any tap IN and OUT at `station`"""
def increment_tap(regulars: dict[str, Counter[str]], station: str, card: str):
    if station not in regulars:
        regulars[station] = Counter()
    regulars[station][card] += 1


for line in sys.stdin:
    match line.split():
        case []:
            ... # on empty line, do nothing
        case ["TAPIN", card, station]:
            if card in cards:
                print("ERROR already in")
            elif station not in STATIONS:
                print("ERROR unknown station") 
            else:
                increment_tap(regulars, station, card)
                cards.add(card)
                print("OK")
        case ["TAPOUT", card, station]:
            if card not in cards:
                print("ERROR not in")
            elif station not in STATIONS:
                print("ERROR unknown station") 
            else:
                tap_outs[card] += 1
                price = price_of_card(tap_outs[card])
                fares[card] += price
                increment_tap(regulars, station, card)
                print(price)
                cards.remove(card)
        case ["PENDING"]:
            print(" ".join(sorted(cards)) or "none")
        case ["FARE", card]:
            print(fares[card])
        case ["REGULARS", station]:
            if station not in STATIONS:
                print("ERROR unknown station") 
            elif station not in regulars:
                print("none")
            else:
                sorted_counts = sorted(regulars[station].items(), key=lambda t: (-t[1], t[0]))
                print(" ".join(f"{k}:{v}" for k, v in sorted_counts))
        case ["CLOSED", a, b]:
            if not edge_in_network(a, b):
                print("ERROR no track")
            elif not edge_is_open(a, b):
                print("ERROR already closed")
            else:
                ...
        case ["OPEN", a, b]:
            ...
        case ["REACHABLE", a, b]:
            ...
        case ["ROUTE", a, b]:
            ...
        case _:
            print("ERROR invalid command")