import pytest

from metro import Metro

# These are white-box, unit tests. `check.sh` does the black box testing.


@pytest.fixture
def metro() -> Metro:
    return Metro()


def test_brand_new_network_contains_only_known_stations_connected_by_open_tracks(
    metro: Metro,
):
    for u, v in metro.network.adj.items():
        assert u in Metro.STATIONS
        for w, open in v:
            assert w in Metro.STATIONS
            assert open


def test_run_command_returns_none_when_command_is_the_empty_string(metro: Metro):
    assert metro.run_command("") is None


def test_run_command_returns_none_when_command_is_only_spaces(metro: Metro):
    assert metro.run_command("     ") is None


def test_run_command_works_with_all_valid_commands(metro: Metro):
    assert type(metro.run_command("FARE luciano")) is int
    for cmd in (
        "TAPIN ciao hello",
        "TAPOUT hello ciao",
        "PENDING",
        "REGULARS spoleto",
        "CLOSED como pisa",  # strada più pesante d'Italia
        "OPEN lecco crema",  # strada più dolce d'Italia
        "REACHABLE lugro palermo",
        "ROUTE milano genova",
    ):
        assert type(metro.run_command(cmd)) is str


def test_run_command_checks_number_of_parameters(metro: Metro):
    for cmd in (
        "TAPIN",
        "TAPIN a",
        "TAPIN a b c",
        "TAPOUT",
        "TAPOUT z",
        "TAPOUT z y x",
        "PENDING marciapiede",
        "FARE",
        "FARE bongo bong",
        "REGULARS",
        "REGULARS helicopter helicopter",
        "CLOSED p q r s",
        "CLOSED zanzara",
        "OPEN g h i",
        "OPEN g",
        "OPEN",
        "REACHABLE",
        "REACHABLE 1",
        "REACHABLE 1 2 3",
        "ROUTE",
        "ROUTE 1",
        "ROUTE 1 2 3",
    ):
        assert metro.run_command(cmd) == "ERROR invalid command"


def test_tapin_enters_the_card_in_the_station(metro: Metro):
    assert "fuga" not in metro.regulars
    assert "luigi" not in metro.cards

    assert metro.tap_in("luigi", "fuga") == "OK"

    assert "luigi" in metro.cards
    assert metro.regulars["fuga"]["luigi"] == 1


def test_tapin_detects_unknown_stations(metro: Metro):
    assert metro.tap_in("luigi", "catania") == "ERROR unknown station"


def test_tapin_detects_if_a_card_is_already_in(metro: Metro):
    metro.tap_in("luigi", "fuga")

    assert metro.tap_in("luigi", "fuga") == "ERROR already in"
    assert metro.tap_in("luigi", "universita") == "ERROR already in"


def test_tapout_returns_the_price_of_the_trip(metro: Metro):
    for i in range(1, 144):
        metro.tap_in("gennaro", "fuga")
        if 1 <= i <= 3:
            assert metro.tap_out("gennaro", "universita") == 2
        elif 4 <= i <= 5:
            assert metro.tap_out("gennaro", "dante") == 1
        else:
            assert metro.tap_out("gennaro", "museo") == 0
        assert metro.tap_outs["gennaro"] == i


def test_tapout_detects_if_the_card_is_not_in(metro: Metro):
    assert metro.tap_out("totonno", "fuga") == "ERROR not in"


def test_tapout_detecs_unknown_stations(metro: Metro):
    metro.tap_in("gianni", "fuga")
    assert metro.tap_out("gianni", "forlimpopoli") == "ERROR unknown station"


def test_pending_returns_the_currently_tapped_in_cards(metro: Metro):
    metro.tap_in("giovanni", "fuga")
    assert metro.pending() == "giovanni"


def test_pending_returns_none_if_there_are_no_tapped_in_cards(metro: Metro):
    assert metro.pending() == "none"


def test_pending_returns_the_cards_in_sorted_alphabetically(metro: Metro):
    metro.tap_in("romeo", "fuga")
    metro.tap_in("oscar", "fuga")
    metro.tap_in("julliet", "fuga")
    metro.tap_in("charlie", "fuga")
    metro.tap_in("mike", "fuga")
    cards = metro.pending().split()
    for i in range(len(cards) - 1):
        assert cards[i] <= cards[i + 1]


def test_fare_returns_zero_for_a_card_never_seen(metro: Metro):
    assert metro.fare("zulu") == 0


def test_fare_returns_the_cumulative_tap_out_price_for_each_card(metro: Metro):
    for _ in range(8):
        metro.tap_in("november", "fuga")
        metro.tap_out("november", "fuga")
    assert metro.fare("november") == 8
    for _ in range(3):
        metro.tap_in("lima", "fuga")
        metro.tap_out("lima", "fuga")
    assert metro.fare("lima") == 6
    metro.tap_in("yankee", "fuga")
    metro.tap_out("yankee", "fuga")
    assert metro.fare("yankee") == 2


def test_tap_otus_at_detects_unknown_stations(metro: Metro):
    assert metro.tap_outs_at("nicosia") == "ERROR unknown station"


def test_tap_outs_at_returns_none_if_a_station_was_never_used(metro: Metro):
    assert metro.tap_outs_at("fuga") == "none"


def test_tap_outs_at_returns_the_sorted_list_of_most_used_cards_by_station(
    metro: Metro,
):
    for card, n in (("ciro", 5), ("gennaro", 19), ("carmine", 8)):
        for _ in range(n):
            metro.tap_in(card, "fuga")
            metro.tap_out(card, "fuga")
    assert metro.tap_outs_at("fuga") == "gennaro:38 carmine:16 ciro:10"


def test_closed_closes_a_track(metro: Metro):
    assert metro.network["dante", "toledo"] == True
    assert metro.closed("dante", "toledo") == "OK"
    assert metro.network["dante", "toledo"] == False


def test_closed_detects_if_the_to_stations_are_not_adjacent(metro: Metro):
    assert metro.closed("manzoni", "fuga") == "ERROR no track"
    assert metro.closed("garibaldi", "municipio") == "ERROR no track"
    assert metro.closed("dante", "fuga") == "ERROR no track"


def test_closed_detects_if_a_track_is_already_closed(metro: Metro):
    metro.closed("museo", "dante")
    assert metro.closed("museo", "dante") == "ERROR already closed"


def test_open_opens_a_track(metro: Metro):
    metro.closed("dante", "toledo")
    assert metro.network["dante", "toledo"] == False
    metro.open("dante", "toledo")
    assert metro.network["dante", "toledo"] == True


def test_open_detects_if_the_to_stations_are_not_adjacent(metro: Metro):
    assert metro.open("manzoni", "fuga") == "ERROR no track"
    assert metro.open("garibaldi", "municipio") == "ERROR no track"
    assert metro.open("dante", "fuga") == "ERROR no track"


def test_open_detects_if_a_track_is_not_closed(metro: Metro):
    assert metro.open("museo", "dante") == "ERROR not closed"


def test_reachable_returns_yes_given_the_same_station_twice(metro: Metro):
    for station in Metro.STATIONS:
        assert metro.reachable(station, station) == "YES"


def test_reachable_returns_yes_when_the_path_exists(metro: Metro):
    assert metro.reachable("dante", "museo") == "YES"
    assert metro.reachable("dante", "fuga") == "YES"
    assert metro.reachable("dante", "fuga") == "YES"
    assert metro.reachable("garibaldi", "materdei") == "YES"
    assert metro.reachable("materdei", "garibaldi") == "YES"
    assert metro.reachable("fuga", "augusteo") == "YES"
    assert metro.reachable("mergellina", "manzoni") == "YES"
    assert metro.reachable("materdei", "municipio") == "YES"
    assert metro.reachable("vanvitelli", "toledo") == "YES"


def test_reachable_returns_no_when_the_path_does_not_exist(metro: Metro):
    assert metro.reachable("manzoni", "toledo") == "NO"
    assert metro.reachable("mergellina", "garibaldi") == "NO"
    assert metro.reachable("dante", "manzoni") == "NO"


def test_reachable_returns_no_when_the_path_exists_but_contains_closed_tracks(
    metro: Metro,
):
    metro.closed("municipio", "universita")
    assert metro.reachable("garibaldi", "fuga") == "NO"
    assert metro.reachable("universita", "materdei") == "NO"
    assert metro.reachable("dante", "universita") == "NO"
    assert metro.reachable("municipio", "garibaldi") == "NO"
    metro.closed("mergellina", "manzoni")
    assert metro.reachable("mergellina", "manzoni") == "NO"


def test_route_returns_ureachable_if_there_is_no_route(metro: Metro):
    assert metro.route("mergellina", "toledo") == "UNREACHABLE"
    assert metro.route("toledo", "mergellina") == "UNREACHABLE"
    assert metro.route("manzoni", "dante") == "UNREACHABLE"
    assert metro.route("manzoni", "dante") == "UNREACHABLE"
    assert metro.route("manzoni", "fuga") == "UNREACHABLE"
    assert metro.route("mergellina", "garibaldi") == "UNREACHABLE"
    assert metro.route("mergellina", "municipio") == "UNREACHABLE"


def test_route_returns_unreachable_if_the_route_contains_closed_tracks(metro: Metro):
    metro.closed("municipio", "toledo")
    assert metro.route("garibaldi", "augusteo") == "UNREACHABLE"
    assert metro.route("augusteo", "garibaldi") == "UNREACHABLE"
    assert metro.route("universita", "vanvitelli") == "UNREACHABLE"
    assert metro.route("materdei", "municipio") == "UNREACHABLE"
    metro.closed("manzoni", "mergellina")
    assert metro.route("manzoni", "mergellina") == "UNREACHABLE"
    assert metro.route("mergellina", "manzoni") == "UNREACHABLE"


def test_route_returns_the_shortest_path_between_two_station(metro: Metro):
    assert metro.route("fuga", "fuga") == "fuga"
    assert metro.route("manzoni", "mergellina") == "manzoni mergellina"
    assert metro.route("mergellina", "manzoni") == "mergellina manzoni"
    assert metro.route("toledo", "fuga") == "toledo augusteo fuga"
    assert metro.route("fuga", "materdei") == "fuga vanvitelli materdei"

    assert (
        metro.route("garibaldi", "dante")
        == "garibaldi universita municipio toledo dante"
    )
    metro.closed("toledo", "dante")
    assert (
        metro.route("garibaldi", "dante")
        == "garibaldi universita municipio toledo augusteo fuga vanvitelli materdei museo dante"
    )

