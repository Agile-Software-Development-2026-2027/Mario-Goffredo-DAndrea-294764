"""
WeightedUndirectedGraph unit tests.
"""

# pylint: disable=missing-function-docstring,redefined-outer-name

import pytest

from metro import WeightedUndirectedGraph


def test_creating_the_graph_initializes_the_adj_list():
    graph = WeightedUndirectedGraph([("a", "b", "c"), ("v", "w", "x")])

    assert {"a", "b", "v", "w"} == graph.vertices

    assert "a" in graph.adj
    assert "b" in graph.adj
    assert ("b", "c") in graph.adj["a"]
    assert ("a", "c") in graph.adj["b"]

    assert "v" in graph.adj
    assert "w" in graph.adj
    assert ("w", "x") in graph.adj["v"]
    assert ("v", "x") in graph.adj["w"]


def test_in_operator_checks_if_an_edge_exsists():
    graph = WeightedUndirectedGraph([(1, 2, None), (3, 4, None), (1, 4, None)])
    assert (1, 2) in graph
    assert (2, 1) in graph
    assert (3, 4) in graph
    assert (4, 3) in graph
    assert (1, 4) in graph
    assert (4, 1) in graph
    assert (1, 3) not in graph
    assert (3, 1) not in graph
    assert (2, 3) not in graph
    assert (3, 2) not in graph
    assert (2, 4) not in graph
    assert (4, 2) not in graph


def test_weights_can_be_set_and_retrieved_via_indexing_operation():
    graph = WeightedUndirectedGraph([(1, 2, ["my weight"])])
    assert graph[1, 2] == ["my weight"]
    assert graph[2, 1] == ["my weight"]

    graph[1, 2].append("another one")
    assert graph[1, 2] == ["my weight", "another one"]
    assert graph[2, 1] == ["my weight", "another one"]

    graph[2, 1] = 3.14
    assert graph[1, 2] == 3.14
    assert graph[2, 1] == 3.14


def test_edges_can_be_added_via_setitem():
    graph = WeightedUndirectedGraph([])
    graph[1, 2] = 3
    assert graph[1, 2] == 3
    assert graph[2, 1] == 3


def test_weights_accessing_an_edge_that_does_not_exist_raises_index_error():
    graph = WeightedUndirectedGraph([])
    with pytest.raises(IndexError) as error:
        _ = graph[15, 16]
    assert str(error.value) == "Graph doesn't have edge (15, 16)"
    with pytest.raises(IndexError) as error:
        _ = graph[16, 15]
    assert str(error.value) == "Graph doesn't have edge (16, 15)"


def test_breadth_first_search_returns_none_if_the_path_does_not_exist():
    graph = WeightedUndirectedGraph([(1, 2, None), (3, 4, None)])
    assert graph.breadth_first_search(1, 4, lambda _: True) is None
    assert graph.breadth_first_search(4, 1, lambda _: True) is None
    assert graph.breadth_first_search(2, 3, lambda _: True) is None
    assert graph.breadth_first_search(3, 2, lambda _: True) is None


def test_breadth_first_search_returns_the_path_when_it_exists():
    graph = WeightedUndirectedGraph([(1, 2, 5), (3, 4, 1), (2, 4, 2)])
    assert graph.breadth_first_search(1, 2, lambda _: True) == [1, 2]
    assert graph.breadth_first_search(2, 1, lambda _: True) == [2, 1]
    assert graph.breadth_first_search(2, 4, lambda _: True) == [2, 4]
    assert graph.breadth_first_search(4, 2, lambda _: True) == [4, 2]
    assert graph.breadth_first_search(1, 4, lambda _: True) == [1, 2, 4]
    assert graph.breadth_first_search(4, 1, lambda _: True) == [4, 2, 1]
    assert graph.breadth_first_search(1, 3, lambda _: True) == [1, 2, 4, 3]
    assert graph.breadth_first_search(3, 1, lambda _: True) == [3, 4, 2, 1]


def test_bfs_returns_the_path_when_it_exists_and_the_condition_on_the_weights_is_satisfied():
    graph = WeightedUndirectedGraph([(1, 2, 5), (3, 4, 1), (2, 4, 2)])
    assert graph.breadth_first_search(1, 2, lambda cost: cost < 6) == [1, 2]
    assert graph.breadth_first_search(1, 2, lambda cost: cost < 3) is None

    assert graph.breadth_first_search(1, 3, lambda cost: cost <= 5) == [1, 2, 4, 3]
    assert graph.breadth_first_search(1, 3, lambda cost: cost < 5) is None

    assert graph.breadth_first_search(4, 3, lambda cost: cost < 2) == [4, 3]
