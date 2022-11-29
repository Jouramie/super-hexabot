def choose_direction(position: float, available_distances: list[int]) -> float:
    """

    :param position: the position of the player from -1 to 1 where 0 is up
    :param available_distances: the distance before an obstacle, starting down and going clockwise
    :return: the direction where to turn to get to the ideal position to avoid the obstacles, from -1 to 1 where 1 would be a 180 degrees turn clockwise
    """

    max_available_distance = max(available_distances)
    obstacle_count = len(available_distances)
    normalized_obstacles = [round(d * 5 / max_available_distance) for d in available_distances]

    obstacles_rotation = [
        obst * (1 - abs(calculate_turn(position, to_circle_percent(index, obstacle_count)))) for index, obst in enumerate(normalized_obstacles)
    ]

    selected_index = max(enumerate(obstacles_rotation), key=lambda x: x[1])[0]

    turn = calculate_turn(position, to_circle_percent(selected_index, obstacle_count))

    return turn


def calculate_turn(position: float, target: float) -> float:
    direction = target - position

    if direction <= -1:
        direction += 2

    if direction >= 1:
        direction += -2

    return direction


def to_circle_percent(index: int, obstacle_count: int) -> float:
    return index / (obstacle_count / 2) - 1
