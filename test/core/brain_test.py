from unittest import TestCase

from core import brain


class TestBrain(TestCase):
    def test_given_already_in_best_spot_when_choose_direction_then_dont_move(self):
        position = 0
        distances = [0, 0, 0, 0, 100, 0, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0, delta=0.05)

    def test_given_best_spot_is_just_right_when_choose_direction_then_turn_right(self):
        position = 0
        distances = [0, 0, 0, 0, 0, 100, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0.25, delta=0.05)

    def test_given_best_spot_is_far_left_when_choose_direction_then_turn_left(self):
        position = 0
        distances = [0, 100, 50, 50, 0, 0, 0, 0]

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

    def test_given_closest_best_spot_right_but_other_best_spot_left__when_choose_direction_then_turn_right(self):
        position = 0
        distances = [0, 100, 0, 0, 0, 100, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0.25, delta=0.05)

    def test_given_best_spot_right_but_nearly_as_best_left__when_choose_direction_then_turn_left(self):
        position = 0
        distances = [0, 0, 0, 99, 0, 0, 0, 100]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.25, delta=0.05)

    def test_given_best_spot_right_but_right_is_blocked__when_choose_direction_then_turn_left(self):
        position = 0
        distances = [0, 50, 20, 20, 0, 0, 100, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, -0.75, delta=0.05)

    def test_given_best_spot_left_but_left_is_blocked__when_choose_direction_then_turn_right(self):
        position = 0.75
        distances = [50, 100, 50, 50, 100, 0, 0, 0]

        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0.50, delta=0.05)
