"""OpenCV를 이용한 웹캠 프레임 처리."""

from __future__ import annotations

import cv2
import numpy as np

from air_canvas.config import CameraConfig


class Camera:
    """웹캠 연결, 프레임 읽기 및 리소스 해제를 담당한다."""

    def __init__(self, config: CameraConfig) -> None:
        self.config = config

        # 지정된 번호의 웹캠 연결
        self.cap = cv2.VideoCapture(config.index)

        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(f"웹캠을 열 수 없습니다. 카메라 번호: {config.index}")

        # 카메라 해상도 설정
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)

    def read(self) -> np.ndarray | None:
        """웹캠에서 프레임을 읽어 반환한다."""

        success, frame = self.cap.read()

        if not success:
            return None

        # 거울 모드가 활성화되어 있으면 좌우 반전
        if self.config.mirror:
            frame = cv2.flip(frame, 1)

        return frame

    def release(self) -> None:
        """웹캠 리소스를 해제한다."""
        self.cap.release()

    def __enter__(self) -> Camera:
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()
