import logging

import properties

logger = logging.getLogger(__name__)


def choose_direction(position: float, available_distances: list[int]) -> float:
    """

    :param position: the position of the player from -1 to 1 where 0 is up
    :param available_distances: the distance before an obstacle, starting down and going clockwise
    :return: the direction where to turn to get to the ideal position to avoid the obstacles, from -1 to 1 where 1 would be a 180 degrees turn clockwise
    """
    approximated_index = (position + 1) * len(available_distances) / 2

    reachable = calculate_reachable(round(approximated_index), available_distances)
    reachable_distances = {i: available_distances[i] for i in reachable}
    logger.info(f"Reachable directions are {reachable_distances} from {approximated_index}")
    if len(reachable) > 1:
        reachable_available_distances = [j if i in reachable else 0 for i, j in enumerate(available_distances)]
    else:
        reachable_available_distances = available_distances
        logger.warning(f"Ohno! Found no reachable directions from {approximated_index}...")

    max_available_distance = max(available_distances)
    obstacle_count = len(available_distances)

    # obstacles_rotation = [
    #    obst * (1 - abs(calculate_turn(position, to_circle_percent(index, obstacle_count)))) for index, obst in enumerate(available_distances)
    # ]

    normalized_obstacles = [round(d * properties.BRAIN_CATEGORIZING / max_available_distance) for d in reachable_available_distances]

    max_value = max(normalized_obstacles)
    index_reaching_max = [i for i, j in enumerate(normalized_obstacles) if j == max_value]
    logger.info(f"Targeting directions {index_reaching_max} where player is around {approximated_index}")

    possible_turns = [calculate_turn(position, to_circle_percent(i, obstacle_count)) for i in index_reaching_max]
    selected_turn = min(possible_turns, key=lambda x: abs(x))
    logger.info(f"Selected {selected_turn} from {possible_turns}")

    return selected_turn


def calculate_turn(position: float, target: float) -> float:
    direction = target - position

    if direction <= -1:
        direction += 2

    if direction >= 1:
        direction += -2

    return direction


def calculate_reachable(approximated_index: int, normalized_obstacles: list[int]) -> set[int]:
    reachable = {approximated_index % len(normalized_obstacles)}
    for obstacle_index in range(approximated_index + 1, len(normalized_obstacles) + approximated_index):
        i = obstacle_index if obstacle_index < len(normalized_obstacles) else obstacle_index - len(normalized_obstacles)
        dist = normalized_obstacles[i]
        if dist <= properties.BRAIN_MINIMAL_SPACE:
            break

        reachable.add(i)

    for obstacle_index in range(len(normalized_obstacles) + approximated_index - 1, approximated_index, -1):
        i = obstacle_index if obstacle_index < len(normalized_obstacles) else obstacle_index - len(normalized_obstacles)
        dist = normalized_obstacles[i]
        if dist <= properties.BRAIN_MINIMAL_SPACE:
            break

        reachable.add(i)

    return reachable


def to_circle_percent(index: int, obstacle_count: int) -> float:
    return index / (obstacle_count / 2) - 1
