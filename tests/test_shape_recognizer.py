"""ShapeRecognizer가 가짜 손그림(tests/strokes.py)을 정답대로 인식하는지 확인."""

from dataclasses import replace

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


@pytest.mark.parametrize("name", CASE_NAMES)
def test_sample_case_is_classified_as_expected(recognizer, name):
    for seed in SEEDS:
        case = next(c for c in fs.sample_cases(seed) if c.name == name)
        kind, confidence = recognizer.classify(case.stroke)
        assert kind is case.expected, f"seed={seed}: {kind.name} (confidence={confidence:.2f})"


def test_recognize_returns_one_result_per_shape_with_stroke_index(recognizer):
    strokes = [fs.rectangle(seed=1), fs.scribble(seed=1), fs.circle(seed=1), fs.triangle(seed=1)]

    results = recognizer.recognize(strokes)

    assert [(r.shape, r.stroke_indices) for r in results] == [
        (ShapeKind.RECTANGLE, (0,)),
        (ShapeKind.CIRCLE, (2,)),
        (ShapeKind.TRIANGLE, (3,)),
    ]
    assert results[0].bbox == strokes[0].bbox()
    assert all(0.7 <= r.confidence <= 1.0 for r in results)


def test_low_confidence_results_are_dropped():
    strict = ShapeRecognizer(RecognitionConfig(shape_min_confidence=0.999))
    assert strict.recognize([fs.rectangle(style=fs.SHAKY)]) == []
    assert len(strict.recognize([fs.rectangle(style=fs.NEAT)])) == 1


def test_open_curve_is_not_a_shape(recognizer):
    # 사각형의 세 변만 그린 'ㄷ'자: 닫히지도, 곧지도 않다.
    u_shape = Stroke(points=[Point(100, 100), Point(300, 100), Point(300, 300), Point(100, 300)])
    open_circle = fs.circle(style=replace(fs.HAND, gap=0.5))
    assert recognizer.classify(u_shape)[0] is ShapeKind.UNKNOWN
    assert recognizer.classify(open_circle)[0] is ShapeKind.UNKNOWN


@pytest.mark.parametrize(
    "stroke",
    [
        Stroke(),
        Stroke(points=[Point(10, 10)]),
        Stroke(points=[Point(10, 10), Point(40, 40)]),
        fs.circle(radius=5),  # 너무 작음
    ],
    ids=["empty", "one_point", "two_points", "tiny"],
)
def test_degenerate_strokes_are_ignored(recognizer, stroke):
    assert recognizer.classify(stroke) == (ShapeKind.UNKNOWN, 0.0)
    assert recognizer.recognize([stroke]) == []
