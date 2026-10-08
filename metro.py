import sys
from collections import Counter


class WeightedUndirectedGraph[V, W]:
    def __init__(self, edges: (V, V, W)):
        self.graph: dict[V, list[(V, W)]] = {}
        for u, v, weight in edges:
            self[u, v] = weight

    def __getitem__(self, edge: (V, V)) -> W:
        u, v = edge
        if (weight := self.__weight(u, v)) is not None:
            return weight
        if (weight := self.__weight(u, v)) is not None:
            return weight
        raise IndexError(f"Graph doesn't have edge ({u}, {v})")

    def __setitem__(self, edge: (V, V), weight: W):
        u, v = edge
        self.__set(u, v, weight)
        self.__set(v, u, weight)

    def __contains__(self, edge: (V, V)) -> bool:
        """Check if the graph contains a edge. Also whether two vertices are adjacent."""
        u, v = edge
        return self.__in(u, v) or self.__in(v, u)

    def __weight(self, u: V, v: V) -> W | None:
        if u in self.graph:
            for vertex, weight in self.graph[u]:
                if vertex == v:
                    return weight
        return None

    def __set(self, u: V, v: V, weight: W):
        if u in self.graph:
            for i in range(len(self.graph[u])):
                if self.graph[u][i][0] == v:
                    del self.graph[u][i]
                    break
        else:
            self.graph[u] = []
        self.graph[u].append((v, weight))

    def __in(self, u: V, v: V) -> bool:
        if u in self.graph:
            for vertex, _ in self.graph[u]:
                if vertex == v:
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


class Metro:
    def __init__(self):
        self.cards: set[str] = (
            set()
        )  # set of card currently tapped in but not yet tapped out
        self.tap_outs: Counter[str] = Counter()  # card: number of tap outs
        self.fares: Counter[str] = Counter()  # card: sum of prices paid at tap out
        self.regulars: dict[
            str, Counter[str]
        ] = {}  # station: count of tap outs per station

    @staticmethod
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

    def tap_in(self, card: str, station: str) -> str:
        if card in self.cards:
            return "ERROR already in"
        if station not in STATIONS:
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
        if card not in self.cards:
            return "ERROR not in"
        if station not in STATIONS:
            return "ERROR unknown station"
        self.tap_outs[card] += 1
        price = Metro.price_of_card(self.tap_outs[card])
        self.fares[card] += price
        self.increment_tap(station, card)
        self.cards.remove(card)
        return price

    def pending(self) -> str:
        return " ".join(sorted(self.cards)) or "none"

    def fare(self, card: str) -> int:
        return self.fares[card]

    def tap_outs_at(self, station: str) -> str:
        if station not in STATIONS:
            return "ERROR unknown station"
        if station not in self.regulars:
            return "none"
        sorted_counts = sorted(
            self.regulars[station].items(), key=lambda t: (-t[1], t[0])
        )
        return " ".join(f"{k}:{v}" for k, v in sorted_counts)

    def run_command(self, command: list) -> str | int | None:
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
                if (a, b) not in network:
                    return "ERROR no track"
                if not network[a, b]:
                    return "ERROR already closed"
                network[a, b] = False
                return "OK"
            case ["OPEN", a, b]:
                if (a, b) not in network:
                    return "ERROR no track"
                if network[a, b]:
                    return "ERROR not closed"
                network[a, b] = True
                return "OK"
            case ["REACHABLE", a, b]:
                ...
            case ["ROUTE", a, b]:
                ...
            case _:
                return "ERROR invalid command"


def main():
    metro = Metro()
    for line in sys.stdin:
        if (result := metro.run_command(line)) or result == 0:
            print(result)


if __name__ == "__main__":
    main()
