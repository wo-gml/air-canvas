"""모듈별 인터페이스 (Protocol).

각 팀원은 자기 모듈의 구현체가 여기 Protocol을 만족하도록 만듭니다.
파이프라인(app.py)과 테스트는 이 Protocol에만 의존하므로,
다른 팀원 구현이 끝나기 전에도 가짜 객체(fake)로 개발과 테스트를 할 수 있습니다.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from air_canvas.core.types import (
    Command,
    Gesture,
    HandLandmarks,
    Point,
    RecognitionResult,
    Stroke,
)

if TYPE_CHECKING:
    import numpy as np

    Frame = np.ndarray  # OpenCV BGR 이미지 (H, W, 3)


class HandTracker(Protocol):
    """[팀원 A] 카메라 프레임에서 손 랜드마크를 찾는다."""

    def detect(self, frame: Frame) -> HandLandmarks | None: ...

    def close(self) -> None: ...


class PointFilter(Protocol):
    """[팀원 A] 손가락 끝 좌표 떨림 보정."""

    def update(self, point: Point) -> Point: ...

    def reset(self) -> None: ...


class GestureClassifier(Protocol):
    """[팀원 C] 랜드마크 -> 이번 프레임의 손 모양."""

    def classify(self, hand: HandLandmarks) -> Gesture: ...


class CommandInterpreter(Protocol):
    """[팀원 C] 프레임별 제스처 흐름 -> 실행할 커맨드 목록.

    떨림 때문에 제스처가 한두 프레임 튀는 것을 걸러내는(debounce) 상태 머신입니다.
    """

    def update(self, gesture: Gesture, position: Point | None) -> list[Command]: ...


class Canvas(Protocol):
    """[팀원 A] 획(Stroke) 저장소. 커맨드를 받아 상태를 바꾼다."""

    @property
    def strokes(self) -> Sequence[Stroke]: ...

    def apply(self, command: Command) -> None: ...


class Renderer(Protocol):
    """[팀원 A] 카메라 프레임 위에 획과 인식 결과를 그린다."""

    def render(
        self,
        frame: Frame,
        strokes: Sequence[Stroke],
        results: Sequence[RecognitionResult],
    ) -> Frame: ...


class Recognizer(Protocol):
    """[팀원 B] 획 목록 -> 도형/텍스트 인식 결과."""

    def recognize(self, strokes: Sequence[Stroke]) -> list[RecognitionResult]: ...


class Exporter(Protocol):
    """[팀원 B] 인식 결과 -> 파일 (SVG 이미지, Mermaid 다이어그램 코드 등)."""

    def export(self, results: Sequence[RecognitionResult], path: Path) -> Path: ...
