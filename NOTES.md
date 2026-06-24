## Problem understanding
My Observation: 
- I understood that this problem is mainly about "Route optimization" since the coverage path inside each survey area is already planned. 
- My task is to decide the order in which the drone should visit the areas.
- This problem remainds me of the traveling salesman problem. Since the baseline task does not require returning to the starting point, I treated it as an open TS Problem
What needs to be optimised?
Given:
- each area has an entry point and exit point
- the cost is based on the travel distance between areas
- route_cost() helper provides the cost to evaluate and compare routes.
Therefore, the main abjective would be
- to find a good visiting order for survey areas
- Minimize the travel distance from the exit point of the current area to the entry point of the next area.
Assumptions:
- I assumed that the polygon geometry is only for contextual understanding and I didn't use it for route optimization. Route decision were purely based on the provided entry and exit points.

## Implementation:
## 1. First Approach: Nearest Neighbour Algorithm
I started with a simple nearest neighbor approach because it is easy to implement and produce a valid route quikly.

Steps:
- pick a starting area
- mark it visited
- look at all remaining area
- Find the one whose entry point is closest to the current exit point
- visit it
- repeat until we cover all area

Output:
- python -m pytest
    2 passed in 0.01s
- python -m flight_sequence.cli data/sample_small.json
    Start: C
    "problem": "sample_small",
    "cost": 12.0,
    Route: C, D, E, B, A
- python -m flight_sequence.cli data/mission_14.json
    Start: Ridge
    "problem": "mission_14",
    "cost": 108.83970376937303,

Observation: 
- The route was valid, but I noticed that the result depeneded on the starting area
- For example, in sample_small.json, starting from area A would produce a route cost of 4, but starting from C produce a cost of 12
- I guess, choosing a better starting area could improve the solution.

## 2. Second Approach: Best-start Nearest Neighbor
To improve the route quality, I modified the implementation so that it check every area as a possible starting point.

steps:
- Adding extra helper function build_nearest_neighbor_route() 
- Its a resuable function which gets the starting area from solve_basic() and return the NN route
- Solve_basic() function 
    1. tries every area as a stating point
    2. generates a route using nearest neighbor
    3. compute the route cost
    4. keeps the best route found

Output:
- python -m pytest 
    2 passed in 0.01s
- python -m flight_sequence.cli data/sample_small.json
Start: A
  "problem": "sample_small",
  "cost": 4.0,
- python -m flight_sequence.cli data/mission_14.json
start: Gully
    "problem": "mission_14",
    "cost": 96.91916947148442,

Observation: 
sample_small.json: from cost 12 to cost 4
mission_14.json: from cost 108.84 to 96.92
- This approach actually improved the route quality while keeping the implementation simple and efficient.

## 3. Third Approach: Best-start Nearest Neighbor + 2-opt
After improving the starting point selection, I wanted to further improve the route. NN makes greedy decisions and can sometimes create route sections that can be traversed in better order.
to address this, I implemented a simple 2-opt local search improvement.

- Added another helper function improve_route_2opt()
- steps,
    1. try every starting point
    2. Build NN route
    3. apply 2-opt optimization
    4. Select the best route

Output:
- python -m pytest 
    2 passed in 0.01s
- python -m flight_sequence.cli data/sample_small.json
    Start: A
    "problem": "sample_small",
    "cost": 4.0,
- python -m flight_sequence.cli data/mission_14.json
    start: Gully
    "problem": "mission_14",
    "cost": 89.16068719747653,

Observations:
from cost = 96.91
order: Gully, Creek, Vineyard, Orchard, Switchback, Plateau, Terrace, Quarry, Basin, Harbor, Field, Ridge, Pines, Meadow
to cost = 89.16
order: Gully, Creek, Vineyard, Harbor, Switchback, Orchard, Basin, Quarry, Terrace, Plateau, Field, Ridge, Pines, Meadow
- Thes 2-opt step reduced the total route cost further by improving some route segments without changing the overall algorithm.

## Additional Test cases
I added a few additional chceks.

Test 1: Every area must be visited exactly once
This test verifies that the generated route has the same number of visits as the number of areas in the mission and that no area appears more than once.

Test 2: No missing areas
This test verifies that every area defined in the mission appears in the final route.

Test 3: Cost matches the provided cost model
This test checks that the cost stored in the returned Route object matches the value computed by the provided route_cost() helper function.

Test 4: Single-area mission
This test verifies that the solver correctly handles the edge case where the mission contains only one area.

Test 5: Route improves over input order
This test verifies that the optimized route performs better than simply following the original area order from the input fixture.

## Optional Extension
1. solve_with_flips
For this extension, I allowed an area to be visited either its original direction of the reversed direction. 
Checks both orientations and chooses whichever gives the shorter distance from the current area.
Result: cost = 61.64
this method gave the best cost result.

2. solve_closed_loop
This fixture has home location and requires a closed loop route. So the route start from home, visit all area and return to the home location.
Result: cost = 98.026
It is because, it introduce extra travel requirement that is to return to home location thats why it has higher cost.

3. solve_large
The provided large mission fixture contains 26 areas.

For this size, the same approach used in the baseline solution remained computationally practical. So I reused:
- Best-start Nearest Neighbor
- 2-opt local search


## Algorithm reasoning
- I first chose the Nearest Neighbor algorithm because it is simple, easy to implement and quickly produce a valid route.
- I noticed that the route quality depended on the starting area, so I improved it by trying all possible starting points and selecting the best result.
- Then added a 2-opt improvement step because some route segments could be reordered to reduce unnecessary travel distance.
- I also considered exact TSP approaches like brute-force search, dynamic programming but they would add more complexity than needed for this task and do not scale well as the number of areas increases.
- Overall, Best-start Nearest Neighbor + 2-opt gave a good balance between route quality, simplicity, and runtime.