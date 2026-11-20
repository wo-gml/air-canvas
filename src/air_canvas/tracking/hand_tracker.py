"""MediaPipe Hands 기반 손 추적기. `core.interfaces.HandTracker` 구현."""

from __future__ import annotations

from typing import TYPE_CHECKING

from air_canvas.config import TrackingConfig
from air_canvas.core.types import HandLandmarks

if TYPE_CHECKING:
    import numpy as np


class MediaPipeHandTracker:
    """TODO(팀원 A):
    - MediaPipe Tasks의 HandLandmarker 사용 (구버전 mp.solutions.hands는 deprecated)
      모델 파일: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
      -> config.model_path 에 저장 (models/ 는 .gitignore 처리됨)
    - BGR -> RGB 변환 후 VIDEO 모드로 detect_for_video 호출
    - 결과를 HandLandmarks(points=21개 Point, handedness, score)로 변환
    - mediapipe는 import가 무거우니 __init__ 안에서 import
    """

    def __init__(self, config: TrackingConfig) -> None:
        self.config = config

    def detect(self, frame: np.ndarray) -> HandLandmarks | None:
        raise NotImplementedError("TODO(팀원 A): MediaPipe로 손 랜드마크 검출")

    def close(self) -> None:
        pass
