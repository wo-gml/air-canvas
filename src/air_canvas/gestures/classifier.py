"""랜드마크 -> 손 모양. `core.interfaces.GestureClassifier` 구현."""

from __future__ import annotations

from air_canvas.config import GestureConfig
from air_canvas.core.types import Gesture, HandLandmarks


class RuleBasedGestureClassifier:
    """규칙 기반 손 모양 판정.

    TODO(팀원 C):
    - 손가락별로 '펴짐' 판정: 손끝(TIP)이 PIP 관절보다 위(y가 작음)인지
      (엄지는 x축 기준이라 따로 처리, handedness 고려)
    - 펴진 손가락 조합 -> Gesture
        검지만: DRAW / 검지+중지: HOVER / 다섯 손가락: ERASE / 모두 접음: FIST
    - 엄지 끝과 검지 끝의 거리 < config.pinch_threshold -> PINCH
    - 손 크기와 상관없게 거리는 손목~중지 MCP 길이로 정규화
    """

    def __init__(self, config: GestureConfig) -> None:
        self.config = config

    def classify(self, hand: HandLandmarks) -> Gesture:
        points = hand.points

        def distance(a, b):
            dx = points[a].x - points[b].x
            dy = points[a].y - points[b].y
            return (dx**2 + dy**2) ** 0.5

        index_up = points[8].y < points[6].y
        middle_up = points[12].y < points[10].y
        ring_up = points[16].y < points[14].y
        pinky_up = points[20].y < points[18].y

        palm_width = distance(5, 17)
        thumb_up = distance(4, 17) > distance(3, 17) + 0.15 * palm_width

        if distance(4, 8) < self.config.pinch_threshold:
            return Gesture.PINCH

        if thumb_up and index_up and middle_up and ring_up and pinky_up:
            return Gesture.ERASE

        if not (thumb_up or index_up or middle_up or ring_up or pinky_up):
            return Gesture.FIST

        if index_up and middle_up and not ring_up and not pinky_up:
            return Gesture.HOVER

        if index_up and not middle_up and not ring_up and not pinky_up:
            return Gesture.DRAW

        return Gesture.NONE
