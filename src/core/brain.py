import logging
from math import ceil, floor

import properties

logger = logging.getLogger(__name__)


def choose_direction(position: float, player_distance: int, available_distances: list[int]) -> (bool, float):
    """

    :param position: the position of the player from -1 to 1 where 0 is up
    :param player_distance: the distance of the player cursor from the center of the game
    :param available_distances: the distance before an obstacle, starting down and going clockwise
    :return: the direction where to turn to get to the ideal position to avoid the obstacles, from -1 to 1 where 1
    would be a 180 degrees turn clockwise
    """
    approximated_index = (position + 1) * properties.SENSOR_RAY_AMOUNT / 2
    round_index = round(approximated_index) % properties.SENSOR_RAY_AMOUNT

    if is_in_unsafe_position(player_distance, available_distances, round_index):
        safe = go_to_nearest_safe(position, round_index, player_distance, available_distances)
        if safe is not None:
            return True, safe

    reachable = calculate_reachable(round_index, player_distance, available_distances)
    reachable_distances = {i: available_distances[i] for i in reachable}
    logger.info(f"Reachable directions are {reachable_distances} from {approximated_index}")
    if len(reachable) > 1:
        reachable_available_distances = [j if i in reachable else 0 for i, j in enumerate(available_distances)]
    else:
        reachable_available_distances = available_distances
        logger.warning(f"Ohno! Found no reachable directions from {approximated_index}...")

    max_available_distance = max(available_distances)
    len(available_distances)

    normalized_obstacles = [
        round(d * properties.BRAIN_CATEGORIZING / max_available_distance) for d in reachable_available_distances
    ]

    max_value = max(normalized_obstacles)
    indexes_reaching_max = [i for i, j in enumerate(normalized_obstacles) if j == max_value]
    logger.info(f"Targeting directions {indexes_reaching_max} where player is around {approximated_index}")

    possible_turns = calculate_turns(indexes_reaching_max, position)
    selected_turn = select_best_possible_turn(possible_turns, approximated_index, reachable_available_distances)

    return False, selected_turn


def is_in_unsafe_position(player_distance, available_distances, round_index):
    return (
        sum(
            [
                available_distances[i % properties.SENSOR_RAY_AMOUNT]
                >= player_distance + properties.BRAIN_UNSAFE_SPACE_OFFSET
                for i in range(
                    round_index - properties.BRAIN_REQUIRED_SAFE_SPACE + 1,
                    round_index + properties.BRAIN_REQUIRED_SAFE_SPACE,
                )
            ]
        )
        < properties.BRAIN_REQUIRED_SAFE_SPACE
    )


def go_to_nearest_safe(position, approximated_index, player_distance, available_distances) -> None | float:
    wall_left = False
    wall_right = False
    for i in range(0, properties.SENSOR_RAY_AMOUNT):
        if (
            available_distances[(approximated_index + i) % properties.SENSOR_RAY_AMOUNT]
            == properties.SENSOR_IMPOSSIBLE_WALL
        ):
            wall_right = True
        if (
            available_distances[(approximated_index - i) % properties.SENSOR_RAY_AMOUNT]
            == properties.SENSOR_IMPOSSIBLE_WALL
        ):
            wall_left = True

        if not wall_right and all(
            available_distances[(approximated_index + i + j) % properties.SENSOR_RAY_AMOUNT]
            > player_distance + properties.BRAIN_UNSAFE_SPACE_OFFSET + properties.BRAIN_SAFE_MARGIN
            for j in range(0, properties.BRAIN_REQUIRED_SAFE_SPACE)
        ):
            return calculate_right_turn(position, to_circle_percent(approximated_index + i))

        if not wall_left and all(
            available_distances[(approximated_index - i - j) % properties.SENSOR_RAY_AMOUNT]
            > player_distance + properties.BRAIN_UNSAFE_SPACE_OFFSET + properties.BRAIN_SAFE_MARGIN
            for j in range(0, properties.BRAIN_REQUIRED_SAFE_SPACE)
        ):
            return calculate_left_turn(position, to_circle_percent(approximated_index - i))

    logger.warning(f"Ohno, found no safe space! Prepare to die...")
    return None


def select_best_possible_turn(possible_turns, position, reachable_available_distances):
    safe_turns = []
    for t in possible_turns:
        moved_pos = t / 2 * properties.SENSOR_RAY_AMOUNT
        if moved_pos > 0:
            passing = [p % properties.SENSOR_RAY_AMOUNT for p in range(ceil(position), floor(position + moved_pos))]
        else:
            passing = [
                p % properties.SENSOR_RAY_AMOUNT
                for p in range(
                    floor(position) + properties.SENSOR_RAY_AMOUNT,
                    ceil(position + moved_pos) + properties.SENSOR_RAY_AMOUNT,
                    -1,
                )
            ]

        if all(reachable_available_distances[p] > 0 for p in passing):
            safe_turns.append(t)

    if not safe_turns:
        logger.warning(f"No safe turn are available. Will pick shortest in all possible turns.")
        safe_turns = possible_turns

    selected_turn = min(safe_turns, key=lambda x: abs(x))
    logger.info(f"Selected {selected_turn} from {possible_turns}")

    return selected_turn


def calculate_turns(possible_destinations, position):
    turns = []
    for i in possible_destinations:
        turns.append(calculate_left_turn(position, to_circle_percent(i)))
        turns.append(calculate_right_turn(position, to_circle_percent(i)))

    return turns


def calculate_left_and_right_turns(position: float, target: float) -> (float, float):
    return calculate_left_turn(position, target), calculate_right_turn(position, target)


def calculate_left_turn(position: float, target: float) -> float:
    direction = target - position

    if direction > 0:
        return direction - 2
    return direction


def calculate_right_turn(position: float, target: float) -> float:
    direction = target - position

    if direction < 0:
        return direction + 2
    return direction


def calculate_reachable(approximated_index: int, player_distance, available_distances: list[int]) -> set[int]:
    reachable = {approximated_index % len(available_distances)}
    for obstacle_index in range(approximated_index + 1, len(available_distances) + approximated_index):
        i = obstacle_index if obstacle_index < len(available_distances) else obstacle_index - len(available_distances)
        dist = available_distances[i]
        if dist <= player_distance + properties.BRAIN_MINIMAL_SPACE_OFFSET:
            break

        reachable.add(i)

    for obstacle_index in range(len(available_distances) + approximated_index - 1, approximated_index, -1):
        i = obstacle_index if obstacle_index < len(available_distances) else obstacle_index - len(available_distances)
        dist = available_distances[i]
        if dist <= player_distance + properties.BRAIN_MINIMAL_SPACE_OFFSET:
            break

        reachable.add(i)

    return reachable


def to_circle_percent(index: int) -> float:
    return index / (properties.SENSOR_RAY_AMOUNT / 2) - 1
