import pytest

from air_canvas.core.types import INDEX_TIP, BBox, HandLandmarks, Point, RecognitionResult, Stroke
from tests.fakes import make_hand


def test_stroke_bbox():
    stroke = Stroke(points=[Point(10, 20), Point(50, 5), Point(30, 40)])
    assert stroke.bbox() == BBox(10, 5, 40, 35)


def test_empty_stroke_has_no_bbox():
    assert Stroke().bbox() is None


def test_hand_requires_21_landmarks():
    with pytest.raises(ValueError):
        HandLandmarks(points=(Point(0, 0),) * 5)


def test_hand_to_pixel():
    hand = make_hand(index_tip=(0.25, 0.5))
    assert hand.index_tip == Point(0.25, 0.5)
    assert hand.to_pixel(INDEX_TIP, width=640, height=480) == Point(160, 240)


def test_recognition_result_is_text():
    box = BBox(0, 0, 1, 1)
    assert RecognitionResult(bbox=box, confidence=0.8, text="hello").is_text
    assert not RecognitionResult(bbox=box, confidence=0.8).is_text


def test_recognition_result_outline_defaults_to_empty():
    # outline을 모르는 인식기(OCR 등)도 그대로 결과를 만들 수 있어야 한다.
    assert RecognitionResult(bbox=BBox(0, 0, 1, 1), confidence=0.8).outline == ()
