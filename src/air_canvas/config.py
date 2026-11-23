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
    # 도형 인식 (recognition/shape.py). 값은 tests/strokes.py 손그림 예제로 측정해서 정함.
    # 맞게 인식한 손그림은 confidence 0.84 이상,
    # 지원하지 않는 도형(반원 등)을 억지로 맞추면 0.81 이하
    shape_min_confidence: float = 0.82
    # 1등과 2등 도형 점수 차이가 이보다 작으면 애매하므로 보정하지 않음
    shape_min_margin: float = 0.03
    shape_min_size: float = 20.0  # bbox 대각선(px)이 이보다 작은 획은 점/실수로 보고 무시
    # 길이 비율 = 다듬은 획의 길이 / 볼록 껍질(convex hull) 둘레
    #   (손떨림으로 길이가 부풀지 않도록 획을 일정 간격으로 다시 찍고 이동 평균으로 다듬은 뒤 잰다)
    #   닫힌 도형 0.85~1.11 (덜 닫힘·덧그림 포함), 'ㄷ'자 ~0.73, 직선 ~0.5
    closed_min_length_ratio: float = 0.8
    closed_max_length_ratio: float = 1.25
    # 안쪽 거리 = 다듬은 획의 점이 껍질 테두리에서 평균 얼마나 안쪽에 있는지 / √껍질 넓이
    #   도형은 테두리를 따라 그리므로 0.06 이하, 낙서는 안쪽을 헤집어서 0.09 이상
    closed_max_inner_distance: float = 0.08
    # 납작함 = 최소 외접 사각형의 짧은 변 / 긴 변. 이보다 납작하면 직선 후보 (짧은 손 직선 ~0.16)
    line_max_thinness: float = 0.2
    # 진행도 = 점 순서와 직선 방향 위치의 상관계수. 한 방향으로 그은 직선 ~1, 왕복한 선 ~0.1
    line_min_progress: float = 0.9
    # 휨 = 직선에 2차 곡선을 맞췄을 때 가운데가 볼록한 높이 / 길이 (손 직선 ~0.07, 눈에 띄는 호 0.1)
    line_max_bend: float = 0.08
    # 둘레를 16등분한 구간에서 꺾이는 최대 각도(도). 원은 ~66 이하, 사각형 ~67 이상, 사다리꼴 ~100
    circle_max_corner_angle: float = 70.0
    # 외접 사각형 꼭짓점이 획에서 떨어진 최대 거리 / √껍질 넓이. 사각형 ~0.16 이하,
    # 사다리꼴·반원은 0.25 이상 (꼭짓점 하나가 비어 있음)
    rect_max_corner_gap: float = 0.2

    # 도형 보정
    snap_angle: float = 10.0  # 수평/수직에서 이 각도(도) 이내로 기울었으면 똑바로 편다
    circle_snap_ratio: float = 0.85  # 타원의 짧은 축 / 긴 축이 이 이상이면 정원으로 편다
    circle_outline_points: int = 64  # 보정한 원/타원을 몇 개의 점으로 표현할지


@dataclass
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    canvas: CanvasConfig = field(default_factory=CanvasConfig)
    recognition: RecognitionConfig = field(default_factory=RecognitionConfig)
    output_dir: Path = Path("outputs")
