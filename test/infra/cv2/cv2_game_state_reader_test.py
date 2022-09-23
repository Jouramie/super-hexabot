import os

import bots.infra.cv2.cv2_game_state_reader as reader
import cv2
import pytest
from core import Card, Rank, Suit


def _load_lazy_image(path):
    return reader.LazyImage(cv2.imread(path))


@pytest.mark.parametrize("card", [card for card in os.listdir("resources/cards") if card[1] is not "0"])
def test_all_card_rank(card):
    card_image = _load_lazy_image("resources/cards/" + card)
    suit = Suit.value_of(card[0])

    rank = reader._read_card_rank(card_image, suit)

    assert rank == Rank.value_of(card[1])


def test_full_screen_play_mat_detection():
    screenshot = _load_lazy_image("resources/session-yellow-red/full-screen-first-turn.png")

    play_mat = reader._crop_play_mat(screenshot)

    assert (900, 1600, 3) < play_mat.original.shape < (1000, 1700, 3)


def test_smollur_play_mat_detection():
    screenshot = _load_lazy_image("resources/session-yellow-red/smollur-first-turn.png")

    play_mat = reader._crop_play_mat(screenshot)

    assert (450, 850, 3) < play_mat.original.shape < (500, 900, 3)


@pytest.mark.skip
def test_read_all_blue_cards_in_first_turn_my_turn():
    screenshot = _load_lazy_image("resources/session-yellow-red/first-turn-my-turn.png")
    screenshot = reader._crop_play_mat(screenshot)
    screenshot = reader._crop_hands_area(screenshot)
    screenshot.test_write()

    cards = reader._read_all_cards_for_suit(screenshot, Suit.BLUE)
    cards = [card.card for card in cards]

    assert Card(Suit.BLUE, Rank.ONE) in cards
    assert Card(Suit.BLUE, Rank.FOUR) in cards


@pytest.mark.skip
def test_read_all_cards_in_game_ended_3_players():
    screenshot = _load_lazy_image("resources/session-yellow-red/game-ended-3-players.png")
    screenshot = reader._crop_play_mat(screenshot)
    screenshot = reader._crop_hands_area(screenshot)
    screenshot.test_write()

    cards = reader._read_all_cards(screenshot)
    cards = [card.card for card in cards]

    assert len(cards) == 15
    assert Card(Suit.BLUE, Rank.TWO) in cards
    assert Card(Suit.GREEN, Rank.FOUR) in cards
    assert Card(Suit.BLUE, Rank.THREE) in cards
    assert Card(Suit.YELLOW, Rank.FIVE) in cards
    assert Card(Suit.GREEN, Rank.TWO) in cards
    assert Card(Suit.BLUE, Rank.FIVE) in cards
    assert Card(Suit.YELLOW, Rank.TWO) in cards
    assert Card(Suit.BLUE, Rank.ONE) in cards
    assert Card(Suit.RED, Rank.THREE) in cards
    assert Card(Suit.RED, Rank.TWO) in cards
    assert Card(Suit.GREEN, Rank.THREE) in cards
    assert Card(Suit.BLUE, Rank.FOUR) in cards
    assert Card(Suit.RED, Rank.FOUR) in cards
    assert Card(Suit.PURPLE, Rank.TWO) in cards
    assert Card(Suit.GREEN, Rank.ONE) in cards


def test_crop_hands_area():
    screenshot = _load_lazy_image("resources/session-yellow-red/cropped-play-mat.png")

    card_area = reader._crop_hands_area(screenshot)

    assert (483, 300, 3) < card_area.original.shape < (485, 350, 3)
