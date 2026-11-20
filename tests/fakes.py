"""테스트 공용 가짜 객체(fake)와 헬퍼. (pytest fixture는 conftest.py)

웹캠, MediaPipe, Hugging Face 모델 없이도 CI에서 돌아가도록
core.interfaces의 Protocol을 흉내 내는 가벼운 가짜 구현을 둡니다.
실제 손 데이터가 필요하면 tests/fixtures/ 에 랜드마크를 JSON으로 저장해 쓰세요.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np

from air_canvas.core.types import (
    NUM_LANDMARKS,
    BBox,
    Command,
    CommandType,
    Gesture,
    HandLandmarks,
    Point,
    RecognitionResult,
    ShapeKind,
    Stroke,
)


def make_hand(index_tip: tuple[float, float] = (0.5, 0.5)) -> HandLandmarks:
    """검지 끝 위치만 지정한 가짜 손 (나머지 점은 화면 중앙)."""
    points = [Point(0.5, 0.5)] * NUM_LANDMARKS
    points[8] = Point(*index_tip)
    return HandLandmarks(points=tuple(points))


class FakeTracker:
    """미리 정해둔 손 목록을 프레임마다 하나씩 돌려준다. None이면 손 없음."""

    def __init__(self, hands: Sequence[HandLandmarks | None]) -> None:
        self._hands = list(hands)
        self.closed = False

    def detect(self, frame: np.ndarray) -> HandLandmarks | None:
        return self._hands.pop(0) if self._hands else None

    def close(self) -> None:
        self.closed = True


class FakeClassifier:
    def __init__(self, gestures: Sequence[Gesture]) -> None:
        self._gestures = list(gestures)

    def classify(self, hand: HandLandmarks) -> Gesture:
        return self._gestures.pop(0)


class FakeInterpreter:
    """debounce 없는 단순 규칙.

    DRAW 시작 -> PEN_DOWN, 유지 -> MOVE, 끝 -> PEN_UP, FIST -> RECOGNIZE
    """

    def __init__(self) -> None:
        self.prev = Gesture.NONE

    def update(self, gesture: Gesture, position: Point | None) -> list[Command]:
        commands: list[Command] = []
        if gesture is Gesture.DRAW:
            kind = CommandType.MOVE if self.prev is Gesture.DRAW else CommandType.PEN_DOWN
            commands.append(Command(kind, position))
        elif self.prev is Gesture.DRAW:
            commands.append(Command(CommandType.PEN_UP))
        if gesture is Gesture.FIST and self.prev is not Gesture.FIST:
            commands.append(Command(CommandType.RECOGNIZE))
        self.prev = gesture
        return commands


class FakeCanvas:
    def __init__(self) -> None:
        self._strokes: list[Stroke] = []
        self.applied: list[Command] = []

    @property
    def strokes(self) -> Sequence[Stroke]:
        return self._strokes

    def apply(self, command: Command) -> None:
        self.applied.append(command)
        if command.type is CommandType.PEN_DOWN and command.position is not None:
            self._strokes.append(Stroke(points=[command.position]))
        elif command.type is CommandType.MOVE and command.position is not None:
            self._strokes[-1].points.append(command.position)
        elif command.type is CommandType.CLEAR:
            self._strokes.clear()


class FakeRecognizer:
    """획이 있으면 첫 획을 사각형으로 인식했다고 돌려준다."""

    def __init__(self, result: RecognitionResult | None = None) -> None:
        self.result = result or RecognitionResult(
            bbox=BBox(0, 0, 10, 10), confidence=0.9, shape=ShapeKind.RECTANGLE, stroke_indices=(0,)
        )
        self.calls = 0

    def recognize(self, strokes: Sequence[Stroke]) -> list[RecognitionResult]:
        self.calls += 1
        return [self.result] if strokes else []


class FakeExporter:
    def __init__(self) -> None:
        self.exported: list[tuple[list[RecognitionResult], Path]] = []

    def export(self, results: Sequence[RecognitionResult], path: Path) -> Path:
        self.exported.append((list(results), path))
        return path
