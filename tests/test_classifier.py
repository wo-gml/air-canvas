from air_canvas.config import GestureConfig
from air_canvas.core.types import Gesture, HandLandmarks, Point
from air_canvas.gestures.classifier import RuleBasedGestureClassifier


def make_hand(index_up, middle_up):
    points = [Point(0.5, 0.6) for _ in range(21)]

    points[6] = Point(0.4, 0.5)
    points[8] = Point(0.4, 0.3 if index_up else 0.7)

    points[10] = Point(0.5, 0.5)
    points[12] = Point(0.5, 0.3 if middle_up else 0.7)

    points[14] = Point(0.6, 0.5)
    points[16] = Point(0.6, 0.7)

    points[18] = Point(0.7, 0.5)
    points[20] = Point(0.7, 0.7)

    return HandLandmarks(points=tuple(points))


def test_draw():
    classifier = RuleBasedGestureClassifier(GestureConfig())
    hand = make_hand(True, False)
    assert classifier.classify(hand) == Gesture.DRAW


def test_hover():
    classifier = RuleBasedGestureClassifier(GestureConfig())
    hand = make_hand(True, True)
    assert classifier.classify(hand) == Gesture.HOVER


def test_fist():
    classifier = RuleBasedGestureClassifier(GestureConfig())
    hand = make_hand(False, False)

    assert classifier.classify(hand) == Gesture.FIST


def test_erase():
    classifier = RuleBasedGestureClassifier(GestureConfig())

    points = list(make_hand(True, True).points)
    points[16] = Point(0.6, 0.3)
    points[20] = Point(0.7, 0.3)
    points[3] = Point(0.3, 0.5)
    points[4] = Point(0.1, 0.3)
    points[5] = Point(0.4, 0.6)
    points[17] = Point(0.7, 0.6)

    hand = HandLandmarks(points=tuple(points))
    assert classifier.classify(hand) == Gesture.ERASE


def test_pinch():
    classifier = RuleBasedGestureClassifier(GestureConfig())

    points = list(make_hand(False, False).points)
    points[4] = Point(0.41, 0.69)

    hand = HandLandmarks(points=tuple(points))
    assert classifier.classify(hand) == Gesture.PINCH


def test_none():
    classifier = RuleBasedGestureClassifier(GestureConfig())
    hand = make_hand(False, True)

    assert classifier.classify(hand) == Gesture.NONE
