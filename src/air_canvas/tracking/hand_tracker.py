"""MediaPipe Tasks를 이용한 손 랜드마크 추적."""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from air_canvas.config import TrackingConfig
from air_canvas.core.types import HandLandmarks, Point


class MediaPipeHandTracker:
    """카메라 프레임에서 손의 21개 랜드마크를 인식한다."""

    def __init__(self, config: TrackingConfig) -> None:
        self.config = config

        model_path = Path(config.model_path)

        if not model_path.is_file():
            raise FileNotFoundError(
                f"MediaPipe 모델 파일을 찾을 수 없습니다: {model_path}"
            )

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=config.num_hands,
            min_hand_detection_confidence=config.min_hand_detection_confidence,
            min_hand_presence_confidence=config.min_hand_presence_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )

        self._tracker = (
            mp.tasks.vision.HandLandmarker.create_from_options(options)
        )

        self._start_time = time.monotonic()
        self._last_timestamp = -1

    def detect(self, frame: np.ndarray) -> HandLandmarks | None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp = int(
            (time.monotonic() - self._start_time) * 1000
        )
        timestamp = max(timestamp, self._last_timestamp + 1)
        self._last_timestamp = timestamp

        result = self._tracker.detect_for_video(
            mp_image, timestamp
        )

        if not result.hand_landmarks:
            return None

        hand = result.hand_landmarks[0]

        points = tuple(
            Point(float(landmark.x), float(landmark.y))
            for landmark in hand
        )

        handedness = "Right"
        score = 1.0

        if result.handedness and result.handedness[0]:
            category = result.handedness[0][0]
            handedness = category.category_name
            score = float(category.score)

        return HandLandmarks(
            points=points,
            handedness=handedness,
            score=score
        )

    def close(self) -> None:
        self._tracker.close()