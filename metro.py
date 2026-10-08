import sys
from collections import Counter

# Time horizon for the domain: today

"""From: <https://prepinsta.com/data-structures-and-algorithms-in-python/weighted-and-directed-graphs/>"""

STATIONS = [
    "garibaldi",
    "universita",
    "municipio",
    "toledo",
    "dante",
    "museo",
    "materdei",
    "vanvitelli",
    "augusteo",
    "fuga",
    "mergellina",
    "manzoni",
]


class WeightedUndirectedGraph[V, W]:
    def __init__(self, edges: (V, V, W)):
        self.graph: dict[V, list[(V, W)]] = {}
        for u, v, weight in edges:
            self[u, v] = weight

    def __getitem__(self, edge: (V, V)) -> W:
        u, v = edge
        if u in self.graph:
            for vertex, weight in self.graph[u]:
                if vertex == v:
                    return weight
        if v in self.graph:
            for vertex, weight in self.graph[v]:
                if vertex == u:
                    return weight
        raise IndexError(f"Graph doesn't have edge ({u}, {v})")

    def __setitem__(self, edge: (V, V), weight: W):
        u, v = edge
        if u in self.graph:
            for i in range(len(self.graph[u])):
                if self.graph[u][i][0] == v:
                    del self.graph[u][i]
                    break
        else:
            self.graph[u] = []
        self.graph[u].append((v, weight))
        if v in self.graph:
            for i in range(len(self.graph[v])):
                if self.graph[v][i][0] == u:
                    del self.graph[v][i]
                    break
        else:
            self.graph[v] = []
        self.graph[v].append((u, weight))

    def __contains__(self, edge: (V, V)) -> bool:
        """Check if the graph contains a node. Also whether two vertices are adjacent."""
        u, v = edge
        if u in self.graph:
            for vertex, _ in self.graph[u]:
                if vertex == v:
                    return True
        if v in self.graph:
            for vertex, _ in self.graph[v]:
                if vertex == u:
                    return True
        return False


network = WeightedUndirectedGraph(
    [
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
        ("universita", "garibaldi", True),
    ]
)

# network.display()
# print(("toledo", "dante") in network)
# print(("dante", "toledo") in network)


# Check if I did not mistype
# for a, b, is_open in NETWORK:
#     assert a in STATIONS
#     assert b in STATIONS
#     assert is_open


def price_of_card(number_of_taps: int) -> int:
    match number_of_taps:
        case 0:
            raise ValueError("Number of taps can't be 0")
        case 1 | 2 | 3:
            return 2
        case 4 | 5:
            return 1
        case _:
            return 0


def increment_tap(regulars: dict[str, Counter[str]], station: str, card: str):
    """To count the regulars we count any tap IN and OUT at `station`"""
    if station not in regulars:
        regulars[station] = Counter()
    regulars[station][card] += 1


def main():
    cards: set[str] = set()  # set of card currently tapped in but not yet tapped out
    tap_outs: Counter[str] = Counter()  # card: number of tap outs
    fares: Counter[str] = Counter()  # card: sum of prices paid at tap out
    regulars: dict[str, Counter[str]] = {}  # station: count of tap outs per station

    for line in sys.stdin:
        match line.split():
            case []:
                ...  # on empty line, do nothing
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
                    sorted_counts = sorted(
                        regulars[station].items(), key=lambda t: (-t[1], t[0])
                    )
                    print(" ".join(f"{k}:{v}" for k, v in sorted_counts))
            case ["CLOSED", a, b]:
                if (a, b) not in network:
                    print("ERROR no track")
                elif not network[a, b]:
                    print("ERROR already closed")
                else:
                    network[a, b] = False
                    print("OK")
            case ["OPEN", a, b]:
                if (a, b) not in network:
                    print("ERROR no track")
                elif network[a, b]:
                    print("ERROR not closed")
                else:
                    network[a, b] = True
                    print("OK")
            case ["REACHABLE", a, b]:
                ...
            case ["ROUTE", a, b]:
                ...
            case _:
                print("ERROR invalid command")


if __name__ == "__main__":
    main()
