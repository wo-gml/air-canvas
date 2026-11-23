"""ShapeRecognizer가 가짜 손그림(tests/strokes.py)을 정답대로 인식하고 보정하는지 확인."""

import math
from dataclasses import replace

import numpy as np
import pytest

from air_canvas.config import RecognitionConfig
from air_canvas.core.types import Point, ShapeKind, Stroke
from air_canvas.recognition import ShapeRecognizer
from tests import strokes as fs

SEEDS = range(20)
CASE_NAMES = [c.name for c in fs.sample_cases()]


@pytest.fixture
def recognizer() -> ShapeRecognizer:
    return ShapeRecognizer(RecognitionConfig())


def _accepted_kind(recognizer, stroke):
    fit = recognizer.classify(stroke)
    return fit.kind if fit.confidence >= recognizer.config.shape_min_confidence else None


def _outline_error(outline, ideal):
    """보정 결과와 정답 도형 사이의 평균 거리 (양쪽 방향 중 큰 값)."""
    a, b = np.array(outline), np.array(ideal)
    dist = np.linalg.norm(a[:, None] - b[None], axis=2)
    return max(dist.min(axis=1).mean(), dist.min(axis=0).mean())


def _diagonal(points):
    arr = np.array(points)
    return float(np.hypot(*np.ptp(arr, axis=0)))


# --- 판정 ---------------------------------------------------------------------


@pytest.mark.parametrize("name", CASE_NAMES)
def test_sample_case_is_classified_as_expected(recognizer, name):
    for seed in SEEDS:
        case = next(c for c in fs.sample_cases(seed) if c.name == name)
        fit = recognizer.classify(case.stroke)
        kind = _accepted_kind(recognizer, case.stroke) or ShapeKind.UNKNOWN
        assert kind is case.expected, f"seed={seed}: {fit.kind.name} {fit.confidence:.2f}"


def test_recognize_returns_one_result_per_shape_with_stroke_index(recognizer):
    strokes = [fs.rectangle(seed=1), fs.scribble(seed=1), fs.circle(seed=1), fs.triangle(seed=1)]

    results = recognizer.recognize(strokes)

    assert [(r.shape, r.stroke_indices) for r in results] == [
        (ShapeKind.RECTANGLE, (0,)),
        (ShapeKind.CIRCLE, (2,)),
        (ShapeKind.TRIANGLE, (3,)),
    ]
    assert all(r.confidence >= recognizer.config.shape_min_confidence for r in results)


def test_low_confidence_results_are_dropped():
    strict = ShapeRecognizer(RecognitionConfig(shape_min_confidence=0.999))
    assert strict.recognize([fs.rectangle(style=fs.SHAKY)]) == []
    assert len(strict.recognize([fs.rectangle(style=fs.NEAT)])) == 1


@pytest.mark.parametrize(
    "stroke",
    [
        Stroke(),
        Stroke(points=[Point(10, 10)]),
        Stroke(points=[Point(10, 10), Point(40, 40)]),
        Stroke(points=[Point(100, 100)] * 10),  # 손가락이 멈춰 있던 획
        fs.circle(radius=5),  # 너무 작음
    ],
    ids=["empty", "one_point", "two_points", "same_point", "tiny"],
)
def test_degenerate_strokes_are_ignored(recognizer, stroke):
    assert recognizer.classify(stroke).kind is ShapeKind.UNKNOWN
    assert recognizer.recognize([stroke]) == []


@pytest.mark.parametrize("num_points", [12, 80, 300])
def test_result_does_not_depend_on_point_density(recognizer, num_points):
    # 카메라 프레임 속도에 따라 같은 도형도 점 개수가 크게 달라진다.
    style = replace(fs.HAND, num_points=num_points)
    for seed in range(5):
        assert _accepted_kind(recognizer, fs.circle(style=style, seed=seed)) is ShapeKind.CIRCLE
        assert _accepted_kind(recognizer, fs.triangle(style=style, seed=seed)) is ShapeKind.TRIANGLE
        assert _accepted_kind(recognizer, fs.line(style=style, seed=seed)) is ShapeKind.LINE


# --- 보정 ---------------------------------------------------------------------


@pytest.mark.parametrize("name", [n for n in CASE_NAMES if n.endswith("_neat")])
def test_neat_shape_is_reproduced_exactly(recognizer, name):
    case = next(c for c in fs.sample_cases() if c.name == name)
    outline = recognizer.classify(case.stroke).outline
    assert _outline_error(outline, case.ideal) < 2.5  # 원은 64점 다각형이라 약간 오차


@pytest.mark.parametrize("name", [c.name for c in fs.sample_cases() if c.ideal])
def test_corrected_outline_is_close_to_ideal_shape(recognizer, name):
    for seed in SEEDS:
        case = next(c for c in fs.sample_cases(seed) if c.name == name)
        outline = recognizer.classify(case.stroke).outline
        error = _outline_error(outline, case.ideal)
        # 정답 도형 크기의 10% 이내 (손떨림이 심한 경우 포함)
        assert error < 0.1 * _diagonal(case.ideal), f"seed={seed}: {error:.1f}px"


def test_outline_has_right_number_of_points(recognizer):
    cfg = recognizer.config
    assert len(recognizer.classify(fs.rectangle()).outline) == 4
    assert len(recognizer.classify(fs.triangle()).outline) == 3
    assert len(recognizer.classify(fs.circle()).outline) == cfg.circle_outline_points
    assert len(recognizer.classify(fs.line()).outline) == 2


def test_rectangle_corners_are_clockwise_from_top_left(recognizer):
    outline = recognizer.classify(fs.rectangle(center=(300, 200), width=200, height=100)).outline
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = outline
    assert x0 < x1 and y0 == pytest.approx(y1, abs=0.5)  # 왼쪽 위 -> 오른쪽 위
    assert y1 < y2 and x1 == pytest.approx(x2, abs=0.5)  # 오른쪽 위 -> 오른쪽 아래
    assert x2 > x3 and y2 == pytest.approx(y3, abs=0.5)  # 오른쪽 아래 -> 왼쪽 아래


def _edge_angles(outline):
    pts = np.array(outline)
    edges = np.roll(pts, -1, axis=0) - pts
    return [math.degrees(math.atan2(dy, dx)) % 90 for dx, dy in edges]


def test_slightly_tilted_rectangle_is_straightened(recognizer):
    outline = recognizer.classify(fs.rectangle(angle=6, style=fs.NEAT)).outline
    for angle in _edge_angles(outline):
        assert min(angle, 90 - angle) < 0.5


def test_clearly_rotated_rectangle_keeps_its_angle(recognizer):
    outline = recognizer.classify(fs.rectangle(angle=25, style=fs.NEAT)).outline
    for angle in _edge_angles(outline):
        assert min(abs(angle - 25), abs(angle - 65)) < 0.5


def test_triangle_base_is_straightened(recognizer):
    outline = recognizer.classify(fs.triangle(angle=5, style=fs.NEAT)).outline
    ys = sorted(p.y for p in outline)
    assert ys[1] == pytest.approx(ys[2], abs=0.5)  # 아래쪽 두 꼭짓점이 같은 높이


def test_nearly_round_ellipse_becomes_circle(recognizer):
    outline = recognizer.classify(fs.ellipse(rx=100, ry=90, style=fs.NEAT)).outline
    pts = np.array(outline)
    radii = np.linalg.norm(pts - pts.mean(axis=0), axis=1)
    assert np.ptp(radii) < 0.5


def test_clearly_oval_ellipse_stays_oval(recognizer):
    outline = recognizer.classify(fs.ellipse(rx=130, ry=80, style=fs.NEAT)).outline
    pts = np.array(outline)
    width, height = np.ptp(pts, axis=0)
    assert width / height == pytest.approx(130 / 80, rel=0.05)


def test_line_keeps_drawing_direction_and_is_straightened(recognizer):
    start, end = recognizer.classify(fs.line((440, 236), (200, 244), style=fs.NEAT)).outline
    assert start.x > end.x  # 오른쪽에서 왼쪽으로 그은 방향 유지
    assert start.y == pytest.approx(end.y, abs=0.5)  # 수평으로 펴짐


def test_result_bbox_matches_corrected_outline(recognizer):
    [result] = recognizer.recognize([fs.rectangle(style=fs.SHAKY, seed=3)])
    xs = [p.x for p in result.outline]
    ys = [p.y for p in result.outline]
    assert result.bbox.x == pytest.approx(min(xs))
    assert result.bbox.y == pytest.approx(min(ys))
    assert result.bbox.width == pytest.approx(max(xs) - min(xs))
    assert result.bbox.height == pytest.approx(max(ys) - min(ys))
