"""튜닝 값을 한곳에 모아둔 설정.

임계값을 코드 곳곳에 숫자로 박아두지 말고 여기에 추가하세요.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from air_canvas.core.types import Color


@dataclass
class CameraConfig:
    index: int = 0
    width: int = 1280
    height: int = 720
    mirror: bool = True  # 셀카처럼 좌우 반전


@dataclass
class TrackingConfig:
    model_path: Path = Path("models/hand_landmarker.task")
    # HandLandmarkerOptions의 같은 이름 옵션으로 그대로 전달
    num_hands: int = 1
    min_hand_detection_confidence: float = 0.6
    min_hand_presence_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    smoothing_alpha: float = 0.5  # 지수 이동평균 계수 (작을수록 부드럽고 느림)


@dataclass
class GestureConfig:
    debounce_frames: int = 3  # 같은 제스처가 N 프레임 연속이어야 확정
    pinch_threshold: float = 0.05  # 엄지-검지 거리(정규화) 이하이면 PINCH


@dataclass
class CanvasConfig:
    palette: list[Color] = field(
        default_factory=lambda: [(0, 0, 255), (0, 200, 0), (255, 0, 0), (0, 0, 0)]
    )
    thickness: int = 4
    eraser_radius: int = 30


@dataclass
class RecognitionConfig:
    enable_ocr: bool = True
    ocr_model_id: str = "microsoft/trocr-small-handwritten"
    shape_min_confidence: float = 0.7


@dataclass
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    canvas: CanvasConfig = field(default_factory=CanvasConfig)
    recognition: RecognitionConfig = field(default_factory=RecognitionConfig)
    output_dir: Path = Path("outputs")
