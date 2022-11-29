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
    max_available_distance = max(available_distances)
    obstacle_count = len(available_distances)

    # obstacles_rotation = [
    #    obst * (1 - abs(calculate_turn(position, to_circle_percent(index, obstacle_count)))) for index, obst in enumerate(available_distances)
    # ]

    normalized_obstacles = [round(d * properties.BRAIN_CATEGORIZING / max_available_distance) for d in available_distances]

    max_value = max(normalized_obstacles)
    index_reaching_max = [i for i, j in enumerate(normalized_obstacles) if j == max_value]
    logger.info(f"Targeting directions {index_reaching_max} where player is around {approximated_index}")

    possible_turns = [calculate_turn(position, to_circle_percent(i, obstacle_count)) for i in index_reaching_max]
    selected_turn = min(possible_turns, key=lambda x: abs(x))
    logger.info(f"Available turns are {possible_turns}, selected {selected_turn}")

    return selected_turn


def calculate_turn(position: float, target: float) -> float:
    direction = target - position

    if direction <= -1:
        direction += 2

    if direction >= 1:
        direction += -2

    return direction


def to_circle_percent(index: int, obstacle_count: int) -> float:
    return index / (obstacle_count / 2) - 1
