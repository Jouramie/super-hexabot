from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Set, FrozenSet, Tuple

import cv2
import numpy as np
from frozendict import frozendict

from bots.domain.model.game_state import RelativeGameState
from bots.domain.model.hand import Hand
from bots.ui.game_state_reading import GameStateReader
from core import Card, Rank, Suit

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ColorBoundary:
    lower_bound: np.array
    upper_bound: np.array


_card_detection_boundaries_by_suit = frozendict(
    {
        Suit.RED: _ColorBoundary(np.array([0, 20, 100]), np.array([20, 255, 255])),
        Suit.BLUE: _ColorBoundary(np.array([105, 20, 100]), np.array([110, 255, 255])),
        Suit.GREEN: _ColorBoundary(np.array([50, 0, 0]), np.array([60, 255, 220])),
        Suit.YELLOW: _ColorBoundary(np.array([30, 120, 100]), np.array([50, 200, 200])),
        Suit.PURPLE: _ColorBoundary(np.array([120, 40, 100]), np.array([140, 255, 255])),
    }
)


_card_ranking_boundaries_by_suit = frozendict(
    {
        Suit.RED: _ColorBoundary(np.array([0, 200, 100]), np.array([20, 255, 255])),
        Suit.BLUE: _ColorBoundary(np.array([20, 200, 0]), np.array([200, 255, 255])),
        Suit.GREEN: _ColorBoundary(np.array([50, 200, 0]), np.array([60, 255, 220])),
        Suit.YELLOW: _ColorBoundary(np.array([0, 0, 0]), np.array([255, 150, 255])),
        Suit.PURPLE: _ColorBoundary(np.array([120, 200, 100]), np.array([140, 255, 255])),
    }
)


_play_mat_color_boundaries = _ColorBoundary(np.array([65, 100, 0]), np.array([70, 160, 255]))


@dataclass(frozen=True)
class DetectedCard:
    card: Card
    rect: Tuple[int, int, int, int]


class LazyImage:
    def __init__(self, screenshot: np.ndarray):
        self.original = screenshot
        self._hsv = None
        self._hsv_filtered = None

    def hsv(self) -> np.ndarray:
        if self._hsv is not None:
            return self._hsv

        self._hsv = cv2.cvtColor(self.original, cv2.COLOR_BGR2HSV)
        return self._hsv

    def hsv_filtered(self) -> np.ndarray:
        if self._hsv_filtered is not None:
            return self._hsv_filtered

        self._hsv_filtered = cv2.fastNlMeansDenoising(self.hsv(), h=10, templateWindowSize=7, searchWindowSize=21)
        return self._hsv_filtered

    def crop_with_4ratio(self, up_ratio: float = 0, down_ratio: float = 0, left_ratio: float = 0, right_ratio: float = 0) -> LazyImage:
        height = self.original.shape[0]
        width = self.original.shape[1]
        return LazyImage(self.original[int(height * up_ratio) : height - int(height * down_ratio), int(width * left_ratio) : width - int(width * right_ratio)])

    def crop_with_2ratio(self, height_ratio: float = 0, width_ratio: float = 0) -> LazyImage:
        return self.crop_with_4ratio(height_ratio, height_ratio, width_ratio, width_ratio)

    def crop_rect(self, rect: Tuple[int, int, int, int]) -> LazyImage:
        x, y, w, h = rect
        return LazyImage(self.original[y : y + h, x : x + w])

    def test_write(self, filename: str = "test.png"):
        return cv2.imwrite(f"../target/{filename}", self.original)

    def __getitem__(self, item) -> np.ndarray:
        return self.original[item]


class Screenshotter:
    def screenshot(self) -> LazyImage:
        raise NotImplementedError


class FromFileScreenshotter(Screenshotter):
    def __init__(self, filename: str):
        self._filename = filename

    def screenshot(self) -> LazyImage:
        return LazyImage(cv2.imread(self._filename))


class Cv2GameStateReader(GameStateReader):
    def __init__(self, screenshotter: Screenshotter):
        self.screenshotter = screenshotter
        self.first_turn = True

    def see_current_state(self) -> RelativeGameState | None:
        """
        algo:

        if previous state is None
          previous state = read state()
          return previous state

        if previous state is first turn:
          left arrow
          previous state = read state()
          if nothing changed
            return None

        right arrow
        previous state = read state()
        if nothing changed
          return None

        return previous state
        """

        # FIXME gamestate interpretion should be uncoupled from game item detection, ie do not add player hand

        screenshot = self.screenshotter.screenshot()

        play_mat = _crop_play_mat(screenshot)

        players = _read_player_hands(screenshot)

        return None


width_card_crop_ratio = 1 / 13
height_card_crop_ratio = 1 / 6


def _read_card_rank(card: LazyImage, suit: Suit) -> Rank:
    boundary = _card_ranking_boundaries_by_suit[suit]

    card = card.crop_with_2ratio(height_card_crop_ratio, width_card_crop_ratio)
    mask = cv2.inRange(card.hsv_filtered(), boundary.lower_bound, boundary.upper_bound)
    inv = cv2.bitwise_not(mask)

    contours = cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    min_area = 100
    max_area = 1000

    rank = len([contour for contour in contours if min_area < cv2.contourArea(contour) < max_area])
    return Rank.value_of(rank)


def _read_all_cards_for_suit(screenshot: LazyImage, suit: Suit) -> Set[DetectedCard]:
    logger.debug(f"Finding card of the {suit} suit.")

    color_boundary = _card_detection_boundaries_by_suit.get(suit)
    if color_boundary is None:
        return set()

    mask = cv2.inRange(screenshot.hsv_filtered(), color_boundary.lower_bound, color_boundary.upper_bound)

    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    contours = [contour for contour in contours if len(contour) >= 4]

    min_area = 10000
    cards = set()
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            rect = cv2.boundingRect(contour)
            card_image = screenshot.crop_rect(rect)
            card = DetectedCard(Card(suit, _read_card_rank(card_image, suit)), rect)
            logger.debug(f"Found {suit} {card.card.rank} card in {rect}.")
            cards.add(card)

    logger.debug(f"Found {len(cards)} {suit} cards.")
    return cards


def _read_all_cards(screenshot: LazyImage) -> FrozenSet[DetectedCard]:
    return frozenset(card for suit in Suit for card in _read_all_cards_for_suit(screenshot, suit))


def _read_player_hands(screenshot: LazyImage) -> List[Hand]:
    players = [Hand.create_unknown_hand("0")]

    cards = _read_all_cards(screenshot)

    return players


def _crop_play_mat(screenshot: LazyImage) -> LazyImage:
    mask = cv2.inRange(screenshot.hsv(), _play_mat_color_boundaries.lower_bound, _play_mat_color_boundaries.upper_bound)
    inv = cv2.bitwise_not(mask)
    contours = cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    contour = sorted([contour for contour in contours if cv2.contourArea(contour) > 100000], key=lambda x: cv2.contourArea(x), reverse=True)[1]
    x, y, w, h = cv2.boundingRect(contour)
    return LazyImage(screenshot.original[y : y + h, x : x + w])


def _crop_hands_area(play_mat: LazyImage) -> LazyImage:
    return play_mat.crop_with_4ratio(left_ratio=0.42, right_ratio=0.2)
