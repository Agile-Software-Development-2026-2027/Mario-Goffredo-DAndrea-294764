"""
Metro solution.

Note: `WeightedUndirectedGraph` doesn't know anything about stations, fares,
tap ins, etc. It's just a graph, used by `Metro`, just like `Metro` uses
`dict`, `Counter`, and `set`.
"""

import sys
from collections import Counter, deque
from collections.abc import Callable
from typing import ClassVar


class WeightedUndirectedGraph[V, W]:
    """
    Fully generic (because why not?) undirected graph that can carry arbitrary
    data on its edges

    Ok, the implementation is a bit ugly with all the linear searches on
    `__setitem__` and `__getitem__`, that's because I used an adjacency list,
    but still I can do

    ```python
    graph[v, w] = "potato" # and then
    print(graph[v, w]) # will print "potato"
    ```

    Performance should be fine with sparse graphs, because the adj list for
    each vertex would be quite short. With dense graphs this would be terrible.

    It doesn't support removing edges and vertices because I didn't need to.
    """

    def __init__(self, edges: list[tuple[V, V, W]]):
        # All hail the adjacency list
        self.adj: dict[V, list[tuple[V, W]]] = {}
        self.vertices: set[V] = set()
        for u, v, weight in edges:
            self[u, v] = weight
            self.vertices.add(u)
            self.vertices.add(v)

    def __getitem__(self, edge: tuple[V, V]) -> W:
        for vertex, weight in self.adj.get(edge[0], []):
            if vertex == edge[1]:
                return weight
        raise IndexError(f"Graph doesn't have edge {edge}")

    def __setitem__(self, edge: tuple[V, V], weight: W):
        """Adds or replaces the edge"""
        self.__set(edge[0], edge[1], weight)
        self.__set(edge[1], edge[0], weight)  # pylint: disable=arguments-out-of-order

    def __contains__(self, edge: tuple[V, V]) -> bool:
        """
        Wether the graph contains `edge`, or wether two vertices are adjacent.
        """
        return any(v == edge[1] for v, _ in self.adj.get(edge[0], []))

    def __set(self, u: V, v: V, weight: W):
        if u not in self.adj:
            self.adj[u] = [(v, weight)]
            return
        for i in range(len(self.adj[u])):
            if self.adj[u][i][0] == v:
                self.adj[u][i] = (v, weight)
                return
        self.adj[u].append((v, weight))

    def breadth_first_search(
        self, u: V, v: V, check_weight: Callable[[W], bool]
    ) -> list[V] | None:
        """
        I started reading Cormen, Liserson, Rivest and Stein, "Introduction to
        Algorithms", Chapter 20: "Elementary Graph Algorithms". But after a
        couple of hours I wanted to cry so I _adapted_ this guys code:
        <https://stackoverflow.com/a/8922151>
        At least I know BFS is also able to find the shortest path.
        """
        seen = {v: False for v in self.vertices}
        seen[u] = True
        q = deque([[u]])
        while q:
            path = q.popleft()
            if path[-1] == v:
                return path
            for adj, weight in self.adj.get(path[-1], []):
                if not seen[adj] and check_weight(weight) is True:
                    seen[adj] = True
                    q.append(list(path) + [adj])
        return None


class Metro:
    """Metro made of stations, tracks and cards"""

    STATIONS: ClassVar[list[str]] = [
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

    def __init__(self):
        # set of card currently tapped in but not yet tapped out
        self.cards: set[str] = set()

        self.tap_outs: Counter[str] = Counter()  # card: number of tap outs
        self.fares: Counter[str] = Counter()  # card: sum of prices paid at tap out

        # station: count of tap outs per station
        self.regulars: dict[str, Counter[str]] = {}

        # composition over inheritance
        self.network = WeightedUndirectedGraph(
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

    @staticmethod
    def price_of_card(number_of_taps: int) -> int:
        """Is responsible for deciding the price of a card based on today's taps"""
        match number_of_taps:
            case 0:
                raise ValueError("Number of taps can't be 0")
            case 1 | 2 | 3:
                return 2
            case 4 | 5:
                return 1
            case _:
                return 0

    def tap_in(self, card: str, station: str) -> str:
        """Taps in `card` at `station`"""
        if card in self.cards:
            return "ERROR already in"
        if station not in Metro.STATIONS:
            return "ERROR unknown station"
        self.increment_tap(station, card)
        self.cards.add(card)
        return "OK"

    def increment_tap(self, station: str, card: str):
        """To count the regulars we count any tap IN and OUT at `station`"""
        if station not in self.regulars:
            self.regulars[station] = Counter()
        self.regulars[station][card] += 1

    def tap_out(self, card: str, station: str) -> str | int:
        """Taps out `card` at `sation`. Returns the price to pay"""
        if card not in self.cards:
            return "ERROR not in"
        if station not in Metro.STATIONS:
            return "ERROR unknown station"
        self.tap_outs[card] += 1
        price = Metro.price_of_card(self.tap_outs[card])
        self.fares[card] += price
        self.increment_tap(station, card)
        self.cards.remove(card)
        return price

    def pending(self) -> str:
        """Lists cards that are currenctly tapped in"""
        return " ".join(sorted(self.cards)) or "none"

    def fare(self, card: str) -> int:
        """Returns the cumulative price paid for `card`"""
        return self.fares[card]

    def tap_outs_at(self, station: str) -> str:
        """Returns a record of cards and their tap out conts at `station`"""
        if station not in Metro.STATIONS:
            return "ERROR unknown station"
        if station not in self.regulars:
            return "none"
        sorted_counts = sorted(
            self.regulars[station].items(), key=lambda t: (-t[1], t[0])
        )
        return " ".join(f"{k}:{v}" for k, v in sorted_counts)

    def closed(self, a: str, b: str) -> str:
        """Closes the track from `a` to `b`"""
        if (a, b) not in self.network:
            return "ERROR no track"
        if not self.network[a, b]:
            return "ERROR already closed"
        self.network[a, b] = False
        return "OK"

    def open(self, a: str, b: str) -> str:
        """Reopens the track from `a` to `b`"""
        if (a, b) not in self.network:
            return "ERROR no track"
        if self.network[a, b]:
            return "ERROR not closed"
        self.network[a, b] = True
        return "OK"

    def reachable(self, a: str, b: str) -> str:
        """Checks wether `a` and `b` are connected only by open tracks"""
        if a not in Metro.STATIONS or b not in Metro.STATIONS:
            return "ERROR unknown station"
        if self.network.breadth_first_search(a, b, lambda open: open) is None:
            return "NO"
        return "YES"

    def route(self, a: str, b: str) -> str:
        """Returns the route between `a` and `b`, or `"UNREACHABLE"`"""
        if a not in Metro.STATIONS or b not in Metro.STATIONS:
            return "ERROR unknown station"
        if (
            route := self.network.breadth_first_search(a, b, lambda open: open)
        ) is None:
            return "UNREACHABLE"
        return " ".join(route)

    # pylint: disable=too-many-return-statements
    def run_command(self, command: str) -> str | int | None:
        """Prases `command` and executes it accordingly"""
        match command.split():
            case []:
                ...  # on empty line, do nothing
            case ["TAPIN", card, station]:
                return self.tap_in(card, station)
            case ["TAPOUT", card, station]:
                return self.tap_out(card, station)
            case ["PENDING"]:
                return self.pending()
            case ["FARE", card]:
                return self.fare(card)
            case ["REGULARS", station]:
                return self.tap_outs_at(station)
            case ["CLOSED", a, b]:
                return self.closed(a, b)
            case ["OPEN", a, b]:
                return self.open(a, b)
            case ["REACHABLE", a, b]:
                return self.reachable(a, b)
            case ["ROUTE", a, b]:
                return self.route(a, b)
            case _:
                return "ERROR invalid command"


def main():
    """Entry point. Handles stdin and stdout."""
    metro = Metro()
    for line in sys.stdin:
        if (result := metro.run_command(line)) is not None:
            print(result)


if __name__ == "__main__":
    main()
