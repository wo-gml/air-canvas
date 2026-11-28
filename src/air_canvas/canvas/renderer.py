"""카메라 프레임 위에 획과 인식 결과를 그린다. `core.interfaces.Renderer` 구현."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from air_canvas.core.types import RecognitionResult, Stroke

if TYPE_CHECKING:
    import numpy as np


class OpenCVRenderer:
    """TODO(팀원 A):
    - 각 Stroke를 cv2.polylines로 그리기 (color, thickness 반영)
    - 인식된 도형은 손그림 대신 깨끗한 도형으로 그리기 (RECTANGLE -> cv2.rectangle 등)
    - 인식된 텍스트는 bbox 위치에 cv2.putText
      (한글은 cv2.putText로 안 나오므로 필요하면 Pillow ImageDraw 사용)
    - 현재 제스처, 펜 색상 같은 상태 표시 UI
    """

    def render(
        self,
        frame: np.ndarray,
        strokes: Sequence[Stroke],
        results: Sequence[RecognitionResult],
    ) -> np.ndarray:
        raise NotImplementedError("TODO(팀원 A): 프레임 위에 캔버스 그리기")
