"""기하 연산 기반 도형 인식 + 자동 보정. `core.interfaces.Recognizer` 구현."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import cv2
import numpy as np

from air_canvas.config import RecognitionConfig
from air_canvas.core.types import BBox, Point, RecognitionResult, ShapeKind, Stroke

_EPS = 1e-6
# 모서리 측정: 볼록 껍질 둘레를 64개 점으로 나누고, 연속한 4구간(둘레의 1/16)에서 꺾인 각도를 본다.
_CORNER_SAMPLES = 64
_CORNER_WINDOW = 4
# 길이 측정 전 다듬기: 획을 128개 점으로 다시 찍고 5개씩 이동 평균
_SMOOTH_SAMPLES = 128
_SMOOTH_WINDOW = 5


@dataclass(frozen=True)
class ShapeFit:
    """획 하나를 판정한 결과. outline은 보정된 도형의 점들 (RecognitionResult.outline 참고)."""

    kind: ShapeKind
    confidence: float
    outline: tuple[Point, ...] = ()


_UNKNOWN = ShapeFit(ShapeKind.UNKNOWN, 0.0)
_CLOSED = frozenset({ShapeKind.RECTANGLE, ShapeKind.TRIANGLE, ShapeKind.CIRCLE})


class ShapeRecognizer:
    """손으로 그린 획 하나하나가 사각형/삼각형/원/직선인지 판정하고 깨끗한 도형으로 보정한다.

    딥러닝 모델 없이 OpenCV 기하 연산만 써서 실시간으로 돌아간다.

    판정 순서
    1. 너무 작은 획은 무시
    2. 획을 감싸는 볼록 껍질(convex hull)과 최소 외접 사각형을 구한다.
       손떨림으로 생긴 안쪽 들쭉날쭉함과 끝부분 덧그림은 볼록 껍질에서 사라진다.
    3. 납작한 획: 한 방향으로 그었고 휘지 않았으면 LINE, 아니면 제외
       (같은 선을 왕복해서 그은 획, 둥근 호)
    4. 닫힌 도형인지 확인. 아니면 제외
       - 길이 비율(다듬은 획 길이 / 껍질 둘레)이 1 근처여야 한다 ('ㄷ'자, 열린 곡선 제외)
         시작점-끝점 거리 대신 길이 비율을 쓰는 이유: 시작점을 지나쳐 더 그리면
         끝점이 멀어져도 도형은 닫혀 있기 때문
       - 획이 껍질 테두리를 따라가야 한다 (안쪽을 헤집는 낙서 제외)
       - 껍질 둘레 대부분을 획이 지나가야 한다 (엉뚱한 획까지 이어 붙여 껍질만 커진 묶음 제외)
    5. 세 도형에 얼마나 잘 맞는지 점수를 매긴다 (점수 = confidence)
       - 사각형: 껍질 넓이 / 최소 외접 사각형 넓이            (사각형이면 1)
                 외접 사각형 꼭짓점 근처가 비어 있으면 0 (사다리꼴, 반원)
       - 삼각형: 껍질 넓이 / 최소 외접 삼각형 넓이            (삼각형이면 1)
       - 원:     외접 사각형에 내접하는 타원과 넓이가 얼마나 같은지, 원형도가
                 같은 크기 타원의 원형도와 얼마나 가까운지 중 낮은 값 (원/타원이면 1)
                 뾰족한 모서리가 있으면 0 (사다리꼴, 반원이 원으로 잡히는 것을 막음)
    6. 1등과 2등 점수가 비슷하면 애매하므로 제외 (틀리게 보정하느니 손그림 그대로 둔다)
    7. confidence < config.shape_min_confidence 이면 결과에서 제외

    보정
    - 사각형/삼각형/원: 최소 외접 도형을 껍질 넓이와 같아지도록 중심 기준으로 줄인다.
      외접 도형은 손떨림으로 바깥쪽에 튄 점까지 감싸서 실제 의도보다 크기 때문
    - 직선: 점들에 맞춘 직선 위로 양 끝점을 투영 (그린 방향 유지)
    - 수평/수직에서 config.snap_angle 이내로 기울었으면 똑바로 편다
    - 거의 둥근 타원은 정원으로 편다

    여러 획으로 나눠 그린 도형 (recognize)
    - 연달아 그린 획 2 ~ config.shape_max_group_strokes개를 끝점이 가까운 순서로 이어
      한 획으로 만든 뒤 위와 같은 방법으로 판정한다. 획 방향과 그린 순서는 상관없다.
      (변을 하나씩 그은 사각형, 반씩 그린 원, 손 추적이 끊겨 둘로 나뉜 획)
    - 이어지는 끝점 사이가 config.shape_join_max_gap보다 벌어지면 묶지 않는다.
    - 혼자서 닫힌 도형으로 인식된 획은 이미 완성된 도형이므로 묶지 않는다.
    - 묶음 후보가 겹치면 획을 더 많이 묶은 것, 그다음 confidence가 높은 것을 고른다.
      묶이지 않은 획은 하나씩 판정한다.
    """

    def __init__(self, config: RecognitionConfig) -> None:
        self.config = config

    def recognize(self, strokes: Sequence[Stroke]) -> list[RecognitionResult]:
        """획 목록 -> 인식된 도형 목록 (첫 획 순서대로). 도형이 아닌 획은 결과에 없다."""
        fits = [self.classify(stroke) for stroke in strokes]
        found: list[tuple[tuple[int, ...], ShapeFit]] = []
        used: set[int] = set()
        for indices, fit in self._group_candidates(strokes, fits):
            if used.isdisjoint(indices):
                found.append((indices, fit))
                used.update(indices)
        found += [((i,), fit) for i, fit in enumerate(fits) if i not in used and self._accepts(fit)]
        found.sort(key=lambda item: item[0][0])
        return [
            RecognitionResult(
                bbox=_bbox(fit.outline),
                confidence=fit.confidence,
                shape=fit.kind,
                stroke_indices=indices,
                outline=fit.outline,
            )
            for indices, fit in found
        ]

    def _accepts(self, fit: ShapeFit) -> bool:
        return (
            fit.kind is not ShapeKind.UNKNOWN and fit.confidence >= self.config.shape_min_confidence
        )

    def _group_candidates(
        self, strokes: Sequence[Stroke], fits: Sequence[ShapeFit]
    ) -> list[tuple[tuple[int, ...], ShapeFit]]:
        """연달아 그린 획을 이어 붙여 도형이 되는 묶음들. 고를 순서대로 정렬."""
        cfg = self.config
        # 혼자서도 닫힌 도형인 획은 이미 완성된 도형이므로 묶지 않는다 (붙여 그린 원 두 개 등)
        complete = {i for i, fit in enumerate(fits) if self._accepts(fit) and fit.kind in _CLOSED}
        candidates = []
        for size in range(2, cfg.shape_max_group_strokes + 1):
            for start in range(len(strokes) - size + 1):
                indices = tuple(range(start, start + size))
                if not complete.isdisjoint(indices):
                    continue
                joined = _join_strokes([strokes[i] for i in indices], cfg.shape_join_max_gap)
                if joined is None:
                    continue
                fit = self.classify(joined)
                if not self._accepts(fit):
                    continue
                candidates.append((indices, fit))
        candidates.sort(key=lambda c: (len(c[0]), c[1].confidence), reverse=True)
        return candidates

    def classify(self, stroke: Stroke) -> ShapeFit:
        """획 하나 -> 도형 종류, confidence, 보정된 외곽선. 도형이 아니면 kind가 UNKNOWN."""
        cfg = self.config

        bbox = stroke.bbox()
        if bbox is None or len(stroke.points) < 3:
            return _UNKNOWN
        if math.hypot(bbox.width, bbox.height) < cfg.shape_min_size:
            return _UNKNOWN

        pts = np.asarray(stroke.points, dtype=np.float32)
        hull = cv2.convexHull(pts)
        min_rect = cv2.minAreaRect(hull)
        (_, (rw, rh), _) = min_rect
        thinness = min(rw, rh) / max(rw, rh, _EPS)

        if thinness < cfg.line_max_thinness:
            outline, progress, bend = _fit_line(pts, cfg.snap_angle)
            if progress < cfg.line_min_progress or bend > cfg.line_max_bend:
                return _UNKNOWN  # 같은 선을 왕복한 획, 둥근 호
            return ShapeFit(ShapeKind.LINE, 1.0 - thinness, outline)

        hull_area = cv2.contourArea(hull)
        hull_perimeter = cv2.arcLength(hull, closed=True)
        smooth = _resample_and_smooth(pts)
        length_ratio = _path_length(smooth) / max(hull_perimeter, _EPS)
        if not cfg.closed_min_length_ratio <= length_ratio <= cfg.closed_max_length_ratio:
            return _UNKNOWN  # 열린 곡선, 여러 바퀴 돌린 획
        if _inner_distance(smooth, hull, hull_area) > cfg.closed_max_inner_distance:
            return _UNKNOWN  # 낙서
        if (
            _uncovered(hull, smooth, hull_area, cfg.closed_cover_tolerance)
            > cfg.closed_max_uncovered
        ):
            return _UNKNOWN  # 획이 지나가지 않은 껍질 변이 있음 (엉뚱한 획까지 이어 붙인 묶음)

        box = cv2.boxPoints(min_rect).astype(float)
        rect_fit = hull_area / max(rw * rh, _EPS)
        if _corner_gap(box, hull, hull_area) > cfg.rect_max_corner_gap:
            rect_fit = 0.0  # 외접 사각형 꼭짓점 근처가 비어 있음 (사다리꼴, 반원)
        triangle_area, triangle = cv2.minEnclosingTriangle(hull)
        triangle_fit = hull_area / max(triangle_area, _EPS)

        circle_fit = 0.0
        if _max_corner_angle(hull) <= cfg.circle_max_corner_angle:
            circularity = 4 * math.pi * hull_area / max(hull_perimeter, _EPS) ** 2
            ellipse_area_fit = 1 - abs(hull_area / max(rw * rh, _EPS) / (math.pi / 4) - 1)
            ellipse_round_fit = circularity / _ellipse_circularity(rw / 2, rh / 2)
            circle_fit = min(ellipse_area_fit, ellipse_round_fit)

        scores = {
            ShapeKind.RECTANGLE: rect_fit,
            ShapeKind.TRIANGLE: triangle_fit,
            ShapeKind.CIRCLE: circle_fit,
        }
        ranked = sorted(scores, key=scores.__getitem__, reverse=True)
        kind, runner_up = ranked[0], ranked[1]
        if scores[kind] - scores[runner_up] < cfg.shape_min_margin:
            return _UNKNOWN

        if kind is ShapeKind.RECTANGLE:
            outline = _correct_polygon(box, rw * rh, hull_area, cfg.snap_angle)
        elif kind is ShapeKind.TRIANGLE:
            corners = triangle.reshape(-1, 2).astype(float)
            outline = _correct_polygon(corners, triangle_area, hull_area, cfg.snap_angle)
        else:
            outline = _correct_ellipse(min_rect, hull_area, cfg)
        return ShapeFit(kind, float(min(scores[kind], 1.0)), outline)


# --- 보정 ---------------------------------------------------------------------


def _correct_polygon(
    corners: np.ndarray, enclosing_area: float, hull_area: float, snap_angle: float
) -> tuple[Point, ...]:
    """외접 다각형을 넓이가 hull_area가 되도록 줄이고, 거의 수평/수직인 변은 똑바로 편다."""
    center = corners.mean(axis=0)
    k = math.sqrt(hull_area / max(enclosing_area, _EPS))
    corners = center + (corners - center) * k

    edges = np.roll(corners, -1, axis=0) - corners
    tilts = [_tilt(math.degrees(math.atan2(dy, dx))) for dx, dy in edges]
    tilt = min(tilts, key=abs)
    if abs(tilt) <= snap_angle:
        corners = _rotate(corners, center, -tilt)
    return _to_points(_clockwise_from_top_left(corners))


def _correct_ellipse(min_rect, hull_area: float, cfg: RecognitionConfig) -> tuple[Point, ...]:
    """외접 사각형에 내접하는 타원을 넓이가 hull_area가 되도록 줄여 둘레를 점으로 찍는다."""
    (cx, cy), (w, h), angle = min_rect
    k = math.sqrt(hull_area / max(math.pi / 4 * w * h, _EPS))
    a, b = w / 2 * k, h / 2 * k
    if min(a, b) / max(a, b, _EPS) >= cfg.circle_snap_ratio:
        a = b = math.sqrt(a * b)  # 넓이를 유지한 정원
    tilt = _tilt(angle)
    if abs(tilt) <= cfg.snap_angle:
        angle -= tilt

    # minAreaRect의 width 축 방향은 (cos θ, sin θ), height 축 방향은 (-sin θ, cos θ)
    th = math.radians(angle)
    t = np.linspace(0, 2 * math.pi, cfg.circle_outline_points, endpoint=False)
    xs = cx + a * np.cos(t) * math.cos(th) - b * np.sin(t) * math.sin(th)
    ys = cy + a * np.cos(t) * math.sin(th) + b * np.sin(t) * math.cos(th)
    return _to_points(np.column_stack([xs, ys]))


def _fit_line(pts: np.ndarray, snap_angle: float) -> tuple[tuple[Point, ...], float, float]:
    """점들에 직선을 맞춰 ((시작점, 끝점), 진행도, 휨)을 돌려준다. 시작/끝은 그린 순서를 따른다.

    - 진행도: 점 순서와 직선 방향 위치의 상관계수 (한 방향으로 그었으면 1에 가깝다)
    - 휨: 2차 곡선을 맞췄을 때 가운데가 볼록한 높이 / 길이
    """
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01).ravel()
    direction = np.array([vx, vy], dtype=float)
    normal = np.array([-vy, vx], dtype=float)
    rel = pts.astype(float) - (x0, y0)
    u, v = rel @ direction, rel @ normal

    progress = abs(float(np.corrcoef(np.arange(len(u)), u)[0, 1]))
    length = max(float(np.ptp(u)), _EPS)
    curvature = np.polyfit(u, v, 2)[0]
    bend = abs(curvature) * (length / 2) ** 2 / length

    start = np.array([x0, y0]) + direction * u.min()
    end = np.array([x0, y0]) + direction * u.max()
    if u[0] > u[-1]:
        start, end = end, start
    ends = np.array([start, end])

    tilt = _tilt(math.degrees(math.atan2(vy, vx)))
    if abs(tilt) <= snap_angle:
        ends = _rotate(ends, ends.mean(axis=0), -tilt)
    return _to_points(ends), progress, bend


# --- 여러 획 잇기 -------------------------------------------------------------


def _join_strokes(strokes: Sequence[Stroke], max_gap: float) -> Stroke | None:
    """획들을 끝점이 가까운 순서로 이어 한 획으로 만든다. 빈틈이 너무 크면 None.

    첫 획에서 시작해, 지금까지 이은 사슬의 앞끝이나 뒤끝에 가장 가까운 끝점을 가진 획을
    방향을 맞춰 붙이기를 반복한다. 그래서 획을 그린 방향과 순서는 결과에 영향이 없다.
    빈틈 기준은 묶음 전체 bbox 대각선 * max_gap.
    """
    pieces = [np.asarray(s.points, dtype=float).reshape(-1, 2) for s in strokes]
    if any(len(p) == 0 for p in pieces):
        return None
    limit = max_gap * float(np.hypot(*np.ptp(np.vstack(pieces), axis=0)))

    chain, rest = [pieces[0]], pieces[1:]
    while rest:
        head, tail = chain[0][0], chain[-1][-1]
        options = []  # (빈틈, 획 번호, 앞에 붙임?, 뒤집음?)
        for j, p in enumerate(rest):
            options += [
                (np.linalg.norm(p[0] - tail), j, False, False),
                (np.linalg.norm(p[-1] - tail), j, False, True),
                (np.linalg.norm(p[-1] - head), j, True, False),
                (np.linalg.norm(p[0] - head), j, True, True),
            ]
        gap, j, front, flip = min(options, key=lambda o: o[0])
        if gap > limit:
            return None
        piece = rest.pop(j)
        piece = piece[::-1] if flip else piece
        if front:
            chain.insert(0, piece)
        else:
            chain.append(piece)
    return Stroke(points=list(_to_points(np.vstack(chain))))


# --- 측정 도우미 --------------------------------------------------------------


def _resample_and_smooth(pts: np.ndarray) -> np.ndarray:
    """획을 길이 기준으로 일정 간격의 점으로 다시 찍고 이동 평균으로 다듬는다.

    카메라 프레임 속도에 따라 점 개수가 달라져도, 손떨림 때문에 길이가 부풀지 않게 하려는 것.
    """
    pts = pts.astype(float)
    cum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    s = np.linspace(0, cum[-1], _SMOOTH_SAMPLES)
    resampled = np.column_stack([np.interp(s, cum, pts[:, 0]), np.interp(s, cum, pts[:, 1])])
    kernel = np.ones(_SMOOTH_WINDOW) / _SMOOTH_WINDOW
    return np.column_stack([np.convolve(resampled[:, i], kernel, mode="valid") for i in range(2)])


def _path_length(pts: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def _corner_gap(corners: np.ndarray, hull: np.ndarray, hull_area: float) -> float:
    """외접 도형의 꼭짓점 중 껍질에서 가장 멀리 떨어진 거리 / √껍질 넓이."""
    gaps = [abs(cv2.pointPolygonTest(hull, (float(x), float(y)), True)) for x, y in corners]
    return max(gaps) / math.sqrt(max(hull_area, _EPS))


def _inner_distance(pts: np.ndarray, hull: np.ndarray, hull_area: float) -> float:
    """점들이 볼록 껍질 테두리에서 평균 얼마나 떨어져 있는지 / √껍질 넓이."""
    dist = [abs(cv2.pointPolygonTest(hull, (float(x), float(y)), True)) for x, y in pts]
    return float(np.mean(dist)) / math.sqrt(max(hull_area, _EPS))


def _uncovered(hull: np.ndarray, pts: np.ndarray, hull_area: float, tolerance: float) -> float:
    """껍질 둘레를 고르게 나눈 점 중 획에서 tolerance * √껍질 넓이보다 먼 점의 비율."""
    samples = _sample_ring(hull)
    dist = np.linalg.norm(samples[:, None] - pts[None], axis=2).min(axis=1)
    return float((dist > tolerance * math.sqrt(max(hull_area, _EPS))).mean())


def _sample_ring(hull: np.ndarray) -> np.ndarray:
    """닫힌 껍질 둘레를 같은 간격의 _CORNER_SAMPLES개 점으로 다시 찍는다."""
    ring = hull.reshape(-1, 2).astype(float)
    ring = np.vstack([ring, ring[:1]])
    cum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ring, axis=0), axis=1))])
    s = np.linspace(0, cum[-1], _CORNER_SAMPLES, endpoint=False)
    return np.column_stack([np.interp(s, cum, ring[:, 0]), np.interp(s, cum, ring[:, 1])])


def _max_corner_angle(hull: np.ndarray) -> float:
    """볼록 껍질 둘레를 고르게 나눠 짧은 구간 안에서 가장 크게 꺾인 각도(도).

    원은 고르게 조금씩 꺾이고, 다각형은 꼭짓점에서 한꺼번에 크게 꺾인다.
    """
    samples = _sample_ring(hull)
    step = np.roll(samples, -1, axis=0) - samples
    heading = np.arctan2(step[:, 1], step[:, 0])
    turn = (np.roll(heading, -1) - heading + math.pi) % (2 * math.pi) - math.pi
    window = sum(np.roll(turn, -k) for k in range(_CORNER_WINDOW))
    return math.degrees(float(np.abs(window).max()))


def _ellipse_circularity(a: float, b: float) -> float:
    """반지름 a, b인 타원의 원형도 4πA/P². 둘레는 라마누잔 근사식."""
    if min(a, b) <= _EPS:
        return 1.0
    perimeter = math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))
    return 4 * math.pi * (math.pi * a * b) / perimeter**2


def _tilt(angle: float) -> float:
    """각도(도)가 가장 가까운 수평/수직 방향에서 얼마나 기울었는지. 범위 [-45, 45)."""
    return (angle + 45) % 90 - 45


def _rotate(points: np.ndarray, center: np.ndarray, angle: float) -> np.ndarray:
    """화면 좌표에서 center를 기준으로 angle(도)만큼 회전 (양수 = 시계 방향으로 보임)."""
    th = math.radians(angle)
    c, s = math.cos(th), math.sin(th)
    return (points - center) @ np.array([[c, s], [-s, c]]) + center


def _clockwise_from_top_left(corners: np.ndarray) -> np.ndarray:
    """꼭짓점을 화면에서 시계 방향으로, 왼쪽 위(x + y가 가장 작은) 점부터 정렬."""
    center = corners.mean(axis=0)
    order = np.argsort(np.arctan2(corners[:, 1] - center[1], corners[:, 0] - center[0]))
    corners = corners[order]
    return np.roll(corners, -int(np.argmin(corners.sum(axis=1))), axis=0)


def _to_points(arr: np.ndarray) -> tuple[Point, ...]:
    return tuple(Point(float(x), float(y)) for x, y in arr)


def _bbox(points: Sequence[Point]) -> BBox:
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    return BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
