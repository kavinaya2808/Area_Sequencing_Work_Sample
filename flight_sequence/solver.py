from __future__ import annotations

from .models import Problem, Route, Visit, route_cost, distance, endpoints


def solve_basic(problem: Problem) -> Route:
    """Return a route for the baseline planning case.

    This starter implementation is deliberately naive and follows the input
    order. Replace it with your implementation.
    """
    if not problem.areas:
        return Route(visits=(), cost=0.0)
    best_visits = None
    best_cost = float("inf")
    for start_index in range(len(problem.areas)):
        visits = build_nearest_neighbor_route(
            problem,
            start_index,
        )
        visits = improve_route_2opt(
            problem,
            visits,
        )
        cost = route_cost(
            problem,
            visits,
            closed_loop=False,
        )
        if cost < best_cost:
            best_cost = cost
            best_visits = visits
    return Route(
        visits=best_visits,
        cost=best_cost,
    )


def solve_with_flips(problem: Problem) -> Route:
    """Optional extension: allow area direction choices."""
    best_visits = None
    best_cost = float("inf")
    for start_index in range(len(problem.areas)):
        visits = build_route_with_flips(
            problem,
            start_index,
        )
        visits = improve_route_2opt(
            problem,
            visits,
        )
        cost = route_cost(
            problem,
            visits,
            closed_loop=False,
        )
        if cost < best_cost:
            best_cost = cost
            best_visits = visits
    return Route(
        visits=best_visits,
        cost=best_cost,
    )


def solve_closed_loop(problem: Problem) -> Route:
    """Optional extension: use problem.home when present."""
    if not problem.areas:
        return Route(visits=(), cost=0.0)
    best_visits = None
    best_cost = float("inf")
    for start_index in range(len(problem.areas)):
        visits = build_nearest_neighbor_route(
            problem,
            start_index,
        )
        visits = improve_route_2opt(
            problem,
            visits,
        )
        cost = route_cost(
            problem,
            visits,
            closed_loop=True,
        )
        if cost < best_cost:
            best_cost = cost
            best_visits = visits
    return Route(
        visits=best_visits,
        cost=best_cost,
    )

def solve_large(problem: Problem) -> Route:
    """Optional extension: handle larger missions."""
    return solve_basic(problem)

def build_nearest_neighbor_route(problem: Problem, start_index: int) -> tuple[Visit, ...]:
    """
    Build a nearest-neighbor route starting from a specific area.
    """
    remaining = list(problem.areas)
    current = remaining.pop(start_index)
    visits = [Visit(current.id)]
    while remaining:
        next_area = min(
            remaining,
            key=lambda area: distance(
                current.exit,
                area.entry,
            ),
        )
        visits.append(
            Visit(next_area.id)
        )
        remaining.remove(next_area)
        current = next_area
    return tuple(visits)

def improve_route_2opt(
    problem: Problem,
    visits: tuple[Visit, ...],
) -> tuple[Visit, ...]:
    """
    Improve a route using 2-opt local search.
    """
    best_visits = list(visits)
    best_cost = route_cost(
        problem,
        best_visits,
        closed_loop=False,
    )
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best_visits) - 1):
            for j in range(i + 1, len(best_visits)):
                candidate = (
                    best_visits[:i]
                    + list(reversed(best_visits[i:j]))
                    + best_visits[j:]
                )
                candidate_cost = route_cost(
                    problem,
                    candidate,
                    closed_loop=False,
                )
                if candidate_cost < best_cost:
                    best_visits = candidate
                    best_cost = candidate_cost
                    improved = True
                    break
            if improved:
                break
    return tuple(best_visits)

def build_route_with_flips(
    problem: Problem,
    start_index: int,
) -> tuple[Visit, ...]:
    remaining = list(problem.areas)
    current = remaining.pop(start_index)
    visits = [Visit(current.id, flipped=False)]
    current_exit = current.exit
    while remaining:
        best_area = None
        best_flipped = False
        best_distance = float("inf")
        for area in remaining:
            normal_distance = distance(
                current_exit,
                area.entry,
            )
            if normal_distance < best_distance:
                best_distance = normal_distance
                best_area = area
                best_flipped = False
            flipped_distance = distance(
                current_exit,
                area.exit,
            )
            if flipped_distance < best_distance:
                best_distance = flipped_distance
                best_area = area
                best_flipped = True
        visits.append(
            Visit(
                best_area.id,
                flipped=best_flipped,
            )
        )
        entry, exit_ = endpoints(
            best_area,
            best_flipped,
        )
        current_exit = exit_
        remaining.remove(best_area)
    return tuple(visits)