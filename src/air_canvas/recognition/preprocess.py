"""획 -> 모델 입력용 이미지 변환."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from air_canvas.core.types import Stroke

if TYPE_CHECKING:
    import numpy as np


def strokes_to_image(strokes: Sequence[Stroke], padding: int = 20) -> np.ndarray:
    """흰 배경에 검은 선으로 획을 그린 이미지를 만든다 (bbox 기준으로 잘라냄).

    TODO(팀원 B):
    - 모든 획의 bbox를 합쳐 padding만큼 여유를 둔 흰 캔버스 생성
    - 좌표를 bbox 기준으로 옮겨 cv2.polylines로 그리기
    - 카메라 배경 없이 획만 그리면 OCR 정확도가 훨씬 좋아짐
    """
    raise NotImplementedError("TODO(팀원 B): 획을 이미지로 변환")
