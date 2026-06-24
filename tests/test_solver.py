from pathlib import Path

from flight_sequence.models import (
    Visit,
    load_problem,
    route_cost,
    Problem,
    Area,
)
from flight_sequence.solver import solve_basic


ROOT = Path(__file__).resolve().parents[1]


def test_every_area_visited_once() -> None:
    """
    Every area should appear exactly once in the final route.
    """
    problem = load_problem(ROOT / "data" / "mission_14.json")

    route = solve_basic(problem)

    visited_ids = [visit.area_id for visit in route.visits]

    assert len(visited_ids) == len(problem.areas)
    assert len(set(visited_ids)) == len(problem.areas)


def test_no_missing_areas() -> None:
    """
    Ensure every area from the problem is included.
    """
    problem = load_problem(ROOT / "data" / "mission_14.json")

    route = solve_basic(problem)

    expected_ids = {area.id for area in problem.areas}
    actual_ids = {visit.area_id for visit in route.visits}

    assert actual_ids == expected_ids


def test_cost_matches_route_cost_model() -> None:
    """
    Route.cost should match the official package cost model.
    """
    problem = load_problem(ROOT / "data" / "mission_14.json")

    route = solve_basic(problem)

    expected_cost = route_cost(
        problem,
        route.visits,
        closed_loop=False,
    )

    assert route.cost == expected_cost


def test_single_area_mission() -> None:
    """
    Solver should handle a mission containing only one area.
    """
    problem = Problem(
        name="single_area",
        areas=(
            Area(
                id="A",
                polygon=(),
                entry=(0.0, 0.0),
                exit=(1.0, 0.0),
            ),
        ),
    )

    route = solve_basic(problem)

    assert len(route.visits) == 1
    assert route.visits[0].area_id == "A"
    assert route.cost == 0.0


def test_route_improves_over_input_order_on_sample_small() -> None:
    """
    Optimized route should be better than the raw input order.
    """
    problem = load_problem(ROOT / "data" / "sample_small.json")

    input_order = tuple(
        Visit(area.id)
        for area in problem.areas
    )

    input_cost = route_cost(
        problem,
        input_order,
        closed_loop=False,
    )

    optimized_route = solve_basic(problem)

    assert optimized_route.cost < input_cost