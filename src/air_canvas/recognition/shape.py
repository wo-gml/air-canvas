"""기하 연산 기반 도형 인식기. `core.interfaces.Recognizer` 구현."""

from __future__ import annotations

import math
from collections.abc import Sequence

import cv2
import numpy as np

from air_canvas.config import RecognitionConfig
from air_canvas.core.types import RecognitionResult, ShapeKind, Stroke

_EPS = 1e-6


class ShapeRecognizer:
    """손으로 그린 획 하나하나가 사각형/삼각형/원/직선인지 판정한다.

    딥러닝 모델 없이 OpenCV 기하 연산만 써서 실시간으로 돌아간다.

    판정 순서
    1. 너무 작은 획은 무시
    2. 획을 감싸는 볼록 껍질(convex hull)과 최소 외접 사각형을 구한다.
       손떨림으로 생긴 안쪽 들쭉날쭉함과 끝부분 덧그림은 볼록 껍질에서 사라진다.
    3. 가늘고 길이 비율(획 길이 / 껍질 둘레)이 작으면 LINE
    4. 길이 비율이 1 근처가 아니면 닫힌 도형이 아님 (열린 곡선, 낙서) -> 제외
       시작점-끝점 거리 대신 길이 비율을 쓰는 이유: 시작점을 지나쳐 더 그리면
       끝점이 멀어져도 도형은 닫혀 있기 때문
    5. 세 도형에 얼마나 잘 맞는지 점수를 매겨 가장 높은 것을 고른다 (점수 = confidence)
       - 사각형: 껍질 넓이 / 최소 외접 사각형 넓이            (사각형이면 1)
       - 삼각형: 껍질 넓이 / 최소 외접 삼각형 넓이            (삼각형이면 1)
       - 원:     외접 사각형에 내접하는 타원과 넓이가 얼마나 같은지, 원형도가
                 같은 크기 타원의 원형도와 얼마나 가까운지 중 낮은 값 (원/타원이면 1)
    6. confidence < config.shape_min_confidence 이면 결과에서 제외

    한 획 = 한 도형만 인식한다. 여러 획으로 나눠 그린 도형은 아직 지원하지 않는다.
    """

    def __init__(self, config: RecognitionConfig) -> None:
        self.config = config

    def recognize(self, strokes: Sequence[Stroke]) -> list[RecognitionResult]:
        results = []
        for i, stroke in enumerate(strokes):
            kind, confidence = self.classify(stroke)
            if kind is ShapeKind.UNKNOWN or confidence < self.config.shape_min_confidence:
                continue
            results.append(
                RecognitionResult(
                    bbox=stroke.bbox(),
                    confidence=confidence,
                    shape=kind,
                    stroke_indices=(i,),
                )
            )
        return results

    def classify(self, stroke: Stroke) -> tuple[ShapeKind, float]:
        """획 하나 -> (도형 종류, confidence). 도형이 아니면 (UNKNOWN, 0.0)."""
        cfg = self.config
        unknown = (ShapeKind.UNKNOWN, 0.0)

        bbox = stroke.bbox()
        if bbox is None or len(stroke.points) < 3:
            return unknown
        if math.hypot(bbox.width, bbox.height) < cfg.shape_min_size:
            return unknown

        pts = np.asarray(stroke.points, dtype=np.float32)
        hull = cv2.convexHull(pts)
        hull_area = cv2.contourArea(hull)
        hull_perimeter = cv2.arcLength(hull, closed=True)
        (_, (rw, rh), _) = cv2.minAreaRect(hull)

        path_length = float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())
        length_ratio = path_length / max(hull_perimeter, _EPS)
        thinness = min(rw, rh) / max(rw, rh, _EPS)

        if thinness < cfg.line_max_thinness and length_ratio <= cfg.line_max_length_ratio:
            return ShapeKind.LINE, 1.0 - thinness

        if not cfg.closed_min_length_ratio <= length_ratio <= cfg.closed_max_length_ratio:
            return unknown

        rect_fit = hull_area / max(rw * rh, _EPS)
        triangle_area, _ = cv2.minEnclosingTriangle(hull)
        triangle_fit = hull_area / max(triangle_area, _EPS)

        circularity = 4 * math.pi * hull_area / max(hull_perimeter, _EPS) ** 2
        ellipse_area_fit = 1 - abs(rect_fit / (math.pi / 4) - 1)
        ellipse_round_fit = circularity / _ellipse_circularity(rw / 2, rh / 2)
        circle_fit = min(ellipse_area_fit, ellipse_round_fit)

        scores = {
            ShapeKind.RECTANGLE: rect_fit,
            ShapeKind.TRIANGLE: triangle_fit,
            ShapeKind.CIRCLE: circle_fit,
        }
        kind = max(scores, key=scores.__getitem__)
        return kind, float(min(scores[kind], 1.0))


def _ellipse_circularity(a: float, b: float) -> float:
    """반지름 a, b인 타원의 원형도 4πA/P². 둘레는 라마누잔 근사식."""
    if min(a, b) <= _EPS:
        return 1.0
    perimeter = math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))
    return 4 * math.pi * (math.pi * a * b) / perimeter**2
