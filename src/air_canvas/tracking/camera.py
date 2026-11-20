"""웹캠 래퍼."""

from __future__ import annotations

from typing import TYPE_CHECKING

from air_canvas.config import CameraConfig

if TYPE_CHECKING:
    import numpy as np


class Camera:
    """OpenCV VideoCapture 래퍼. `with Camera(cfg) as cam:` 형태로 사용.

    TODO(팀원 A):
    - cv2.VideoCapture(cfg.index) 열기, 해상도 설정
    - read(): 프레임 읽기, cfg.mirror면 cv2.flip(frame, 1)
    - 카메라를 못 열면 이해하기 쉬운 에러 메시지
    """

    def __init__(self, config: CameraConfig) -> None:
        self.config = config

    def read(self) -> np.ndarray | None:
        raise NotImplementedError("TODO(팀원 A): 웹캠 프레임 읽기")

    def release(self) -> None:
        # TODO(팀원 A): 웹캠 해제 (cap.release()).
        # 정리 함수는 예외를 던지면 원래 에러를 가리므로 NotImplementedError를 쓰지 않는다.
        pass

    def __enter__(self) -> Camera:
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()
