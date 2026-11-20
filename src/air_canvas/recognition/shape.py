"""기하 연산 기반 도형 인식기. `core.interfaces.Recognizer` 구현."""

from __future__ import annotations

from collections.abc import Sequence

from air_canvas.config import RecognitionConfig
from air_canvas.core.types import RecognitionResult, Stroke


class ShapeRecognizer:
    """손으로 그린 획이 사각형/원/삼각형/선인지 판정.

    딥러닝 모델 없이도 데모 GIF(사각형 -> 깨끗한 사각형)를 실시간으로 만들 수 있게
    가벼운 방법을 먼저 씁니다.

    TODO(팀원 B):
    - 획이 닫혀 있는지 확인 (시작점과 끝점 거리 / bbox 대각선)
    - cv2.approxPolyDP로 꼭짓점 수 계산: 3 -> TRIANGLE, 4 -> RECTANGLE
    - 원형도 4*pi*area / perimeter^2 가 1에 가까우면 CIRCLE
    - 닫히지 않고 거의 직선이면 LINE
    - 판정이 애매하면(confidence < config.shape_min_confidence) 결과에서 제외
    """

    def __init__(self, config: RecognitionConfig) -> None:
        self.config = config

    def recognize(self, strokes: Sequence[Stroke]) -> list[RecognitionResult]:
        raise NotImplementedError("TODO(팀원 B): 획 -> 도형 인식")
