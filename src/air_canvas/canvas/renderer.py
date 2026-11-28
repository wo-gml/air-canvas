"""OpenCV를 이용한 Air Canvas 획 렌더링."""

from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np

from air_canvas.core.types import RecognitionResult, Stroke


class OpenCVRenderer:
    """저장된 Stroke를 카메라 프레임 위에 표시한다."""

    def render(
        self,
        frame: np.ndarray,
        strokes: Sequence[Stroke],
        results: Sequence[RecognitionResult],
    ) -> np.ndarray:
        """프레임 위에 손그림 획을 그린 이미지를 반환한다."""

        output = frame.copy()

        for stroke in strokes:
            if not stroke.points:
                continue

            points = np.array(
                [(int(point.x), int(point.y)) for point in stroke.points],
                dtype=np.int32,
            )

            color = tuple(int(c) for c in stroke.color)
            thickness = max(1, int(stroke.thickness))

            if len(points) == 1:
                cv2.circle(
                    output,
                    tuple(points[0]),
                    max(1, thickness // 2),
                    color,
                    -1,
                    cv2.LINE_AA,
                )
            else:
                cv2.polylines(
                    output,
                    [points],
                    isClosed=False,
                    color=color,
                    thickness=thickness,
                    lineType=cv2.LINE_AA,
                )

        # 인식 결과 출력은 화면·통합 담당자가 구현할 예정
        _ = results

        return output
