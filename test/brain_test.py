from unittest import TestCase

import properties
from core import brain

properties.BRAIN_MINIMAL_SPACE = 10
properties.BRAIN_UNSAFE_SPACE = 20
properties.SENSOR_RAY_AMOUNT = 8


class TestBrain(TestCase):
    def test_given_already_in_best_spot_when_choose_direction_then_dont_move(self):
        position = 0
        distances = [0, 0, 0, 0, 100, 0, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0, delta=0.05)

    def test_given_best_spot_is_just_right_when_choose_direction_then_turn_right(self):
        position = 0
        distances = [0, 0, 0, 0, 10, 100, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0.25, delta=0.05)

    def test_given_best_spot_is_far_left_when_choose_direction_then_turn_left(self):
        position = 0
        distances = [0, 100, 50, 50, 10, 0, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.75, delta=0.05)

    def test_given_best_spot_is_opposite_when_choose_direction_then_turn_left(self):
        position = 0
        distances = [100, 50, 50, 50, 50, 0, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -1, delta=0.05)

    def test_given_player_is_right_and_best_spot_is_up_when_choose_direction_then_turn_left(self):
        position = 0.5
        distances = [0, 0, 50, 50, 100, 50, 50, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.5, delta=0.05)

    def test_given_player_is_far_left_and_best_spot_is_far_right_when_choose_direction_then_turn_left(self):
        position = -0.75
        distances = [50, 50, 50, 0, 0, 0, 0, 100]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.5, delta=0.05)

    def test_given_closest_best_spot_right_but_other_best_spot_left_when_choose_direction_then_turn_right(self):
        position = 0
        distances = [0, 100, 0, 0, 10, 100, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0.25, delta=0.05)

    def test_given_best_spot_right_but_nearly_as_best_left_when_choose_direction_then_turn_left(self):
        position = 0
        distances = [0, 0, 0, 99, 10, 0, 0, 100]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.25, delta=0.05)

    def test_given_best_spot_right_but_right_is_blocked_when_choose_direction_then_turn_left(self):
        position = 0
        distances = [0, 50, 20, 20, 10, 0, 100, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.75, delta=0.05)

    def test_given_best_spot_left_but_left_is_blocked_when_choose_direction_then_turn_right(self):
        position = 0.50
        distances = [50, 50, 50, 50, 100, 0, 10, 50]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 1.5, delta=0.05)

    def test_given_player_unsafe_when_choose_direction_then_to_nearest_safe_location(self):
        position = -0.5
        distances = [12, 6, 12, 12, 12, 12, 100, 50]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.75, delta=0.05)
