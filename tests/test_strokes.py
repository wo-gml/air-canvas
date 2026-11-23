"""가짜 손그림 생성기(tests/strokes.py)가 의도대로 동작하는지 확인."""

import math
from dataclasses import replace

import pytest

from air_canvas.core.types import ShapeKind
from tests import strokes as fs


def _start_end_distance(stroke):
    (x0, y0), (x1, y1) = stroke.points[0], stroke.points[-1]
    return math.hypot(x1 - x0, y1 - y0)


def test_same_seed_gives_same_stroke():
    assert fs.rectangle(seed=3).points == fs.rectangle(seed=3).points
    assert fs.rectangle(seed=3).points != fs.rectangle(seed=4).points


def test_neat_rectangle_matches_requested_size():
    bbox = fs.rectangle(center=(300, 200), width=200, height=100, style=fs.NEAT).bbox()
    assert bbox.x == pytest.approx(200)
    assert bbox.y == pytest.approx(150)
    assert bbox.width == pytest.approx(200)
    assert bbox.height == pytest.approx(100)


def test_neat_shapes_are_closed():
    for stroke in (
        fs.rectangle(style=fs.NEAT),
        fs.triangle(style=fs.NEAT),
        fs.circle(style=fs.NEAT),
    ):
        assert _start_end_distance(stroke) == pytest.approx(0, abs=1e-6)


def test_gap_leaves_shape_open():
    closed = fs.circle(radius=100, style=replace(fs.NEAT, gap=0.0))
    opened = fs.circle(radius=100, style=replace(fs.NEAT, gap=0.1))
    assert _start_end_distance(closed) < 1
    # 둘레의 10% 호(약 63px)에 해당하는 현의 길이만큼 벌어진다.
    assert _start_end_distance(opened) == pytest.approx(2 * 100 * math.sin(math.pi * 0.1), rel=0.05)


def test_hand_style_stays_near_the_ideal_shape():
    neat = fs.circle(radius=100, style=fs.NEAT).bbox()
    hand = fs.circle(radius=100, style=fs.SHAKY, seed=7).bbox()
    assert abs(hand.width - neat.width) < 40
    assert abs(hand.height - neat.height) < 40


def test_num_points_is_respected():
    assert len(fs.triangle(style=replace(fs.HAND, num_points=37)).points) == 37


def test_sample_cases_cover_every_target_shape():
    cases = fs.sample_cases()
    kinds = {c.expected for c in cases}
    assert {ShapeKind.RECTANGLE, ShapeKind.TRIANGLE, ShapeKind.CIRCLE, ShapeKind.LINE} <= kinds
    assert len({c.name for c in cases}) == len(cases)  # 이름 중복 없음
