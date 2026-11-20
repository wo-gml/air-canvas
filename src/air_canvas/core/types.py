"""모듈 사이에서 주고받는 공통 데이터 타입.

이 파일은 팀 전체의 '계약'입니다. 필드를 바꾸면 다른 모듈이 깨질 수 있으니
변경할 때는 PR에 모든 팀원을 리뷰어로 지정하세요.

좌표 규칙
- HandLandmarks.points: MediaPipe 그대로 정규화 좌표 (0.0 ~ 1.0)
- 그 외 Point (Stroke, Command, BBox): 화면 픽셀 좌표 (x: 오른쪽, y: 아래쪽)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, NamedTuple

Color = tuple[int, int, int]  # OpenCV 기준 BGR


class Point(NamedTuple):
    x: float
    y: float


class BBox(NamedTuple):
    x: float
    y: float
    width: float
    height: float


# --- 손 추적 (tracking) -------------------------------------------------------

# MediaPipe Hands 랜드마크 인덱스 중 자주 쓰는 것
WRIST = 0
THUMB_TIP = 4
INDEX_PIP = 6
INDEX_TIP = 8
MIDDLE_PIP = 10
MIDDLE_TIP = 12
RING_PIP = 14
RING_TIP = 16
PINKY_PIP = 18
PINKY_TIP = 20
NUM_LANDMARKS = 21


@dataclass(frozen=True)
class HandLandmarks:
    """한 손의 21개 랜드마크 (정규화 좌표)."""

    points: tuple[Point, ...]
    handedness: str = "Right"  # "Left" | "Right"
    score: float = 1.0

    def __post_init__(self) -> None:
        if len(self.points) != NUM_LANDMARKS:
            raise ValueError(
                f"랜드마크는 {NUM_LANDMARKS}개여야 합니다 (받은 개수: {len(self.points)})"
            )

    @property
    def index_tip(self) -> Point:
        return self.points[INDEX_TIP]

    def to_pixel(self, index: int, width: int, height: int) -> Point:
        """정규화 좌표를 화면 픽셀 좌표로 변환."""
        p = self.points[index]
        return Point(p.x * width, p.y * height)


# --- 제스처 / 커맨드 (gestures) -----------------------------------------------


class Gesture(Enum):
    """한 프레임에서 판정한 손 모양."""

    NONE = auto()  # 손 없음 / 판정 불가
    DRAW = auto()  # 검지만 폄 -> 그리기
    HOVER = auto()  # 검지 + 중지 폄 -> 펜 들고 이동
    ERASE = auto()  # 손바닥 폄 -> 지우개
    PINCH = auto()  # 엄지 + 검지 맞닿음 -> 선택 / 색 변경
    FIST = auto()  # 주먹 -> 인식 실행


class CommandType(Enum):
    PEN_DOWN = auto()
    MOVE = auto()
    PEN_UP = auto()
    ERASE = auto()
    UNDO = auto()
    CLEAR = auto()
    CHANGE_COLOR = auto()
    RECOGNIZE = auto()
    SAVE = auto()


@dataclass(frozen=True)
class Command:
    """캔버스와 앱이 실행할 명령. 제스처 파서가 만들어냅니다."""

    type: CommandType
    position: Point | None = None
    payload: dict[str, Any] = field(default_factory=dict)  # 예: {"color": (0, 0, 255)}


# --- 캔버스 (canvas) ---------------------------------------------------------


@dataclass
class Stroke:
    """펜을 내렸다가 들 때까지 그린 한 획."""

    points: list[Point] = field(default_factory=list)
    color: Color = (0, 0, 255)
    thickness: int = 4

    def bbox(self) -> BBox | None:
        if not self.points:
            return None
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


# --- 인식 (recognition) ------------------------------------------------------


class ShapeKind(Enum):
    RECTANGLE = auto()
    CIRCLE = auto()
    TRIANGLE = auto()
    LINE = auto()
    ARROW = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class RecognitionResult:
    """인식 결과 하나. 도형이면 shape, 글자면 text를 채웁니다."""

    bbox: BBox
    confidence: float
    shape: ShapeKind | None = None
    text: str | None = None
    stroke_indices: tuple[int, ...] = ()  # 이 결과를 만든 Stroke들의 인덱스

    @property
    def is_text(self) -> bool:
        return self.text is not None
