import sys
from collections import Counter

# Time horizon for the domain: today

STATIONS = ["garibaldi", "universita", "municipio", "toledo", "dante", "museo", "materdei", "vanvitelli", "augusteo", "fuga", "mergellina", "manzoni"]

cards: set[str] = set() # set of card currently tapped in but not yet tapped out
tap_outs: Counter[str, int] = Counter() # card: number of tap outs
fares: Counter[str, int] = Counter() # card: sum of prices paid at tap out
regulars: dict[str, Counter[str]] = {} # station: count of tap outs per station

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
        case _:
            print("ERROR invalid command")