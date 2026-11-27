from air_canvas.core.types import BBox, Point, RecognitionResult, ShapeKind, Stroke
from air_canvas.recognition.composite import CompositeRecognizer
from tests.fakes import FakeRecognizer


class RecordingTextRecognizer:
    """받은 획 개수를 기록하고, 받은 획 중 첫 번째를 텍스트로 인식한다."""

    def __init__(self):
        self.received = None

    def recognize(self, strokes):
        self.received = list(strokes)
        return [
            RecognitionResult(bbox=BBox(0, 0, 1, 1), confidence=0.7, text="A", stroke_indices=(0,))
        ]


def strokes(n):
    return [Stroke(points=[Point(i, i)]) for i in range(n)]


def test_only_unrecognized_strokes_go_to_ocr():
    shape = FakeRecognizer()  # 0번 획을 사각형으로 인식
    text = RecordingTextRecognizer()

    results = CompositeRecognizer(shape, text).recognize(strokes(3))

    assert len(text.received) == 2
    assert results[0].shape is ShapeKind.RECTANGLE
    # OCR이 받은 리스트의 0번 = 원래 strokes의 1번
    assert results[1].text == "A"
    assert results[1].stroke_indices == (1,)


def test_without_text_recognizer_returns_shapes_only():
    results = CompositeRecognizer(FakeRecognizer()).recognize(strokes(2))
    assert [r.shape for r in results] == [ShapeKind.RECTANGLE]


def test_ocr_result_fields_are_kept_when_indices_are_remapped():
    class OutlineRecognizer:
        def recognize(self, strokes):
            outline = (Point(0, 0), Point(5, 5))
            return [
                RecognitionResult(
                    bbox=BBox(0, 0, 5, 5),
                    confidence=0.9,
                    shape=ShapeKind.LINE,
                    stroke_indices=(0,),
                    outline=outline,
                )
            ]

    results = CompositeRecognizer(FakeRecognizer(), OutlineRecognizer()).recognize(strokes(2))

    assert results[1].stroke_indices == (1,)
    assert results[1].outline == (Point(0, 0), Point(5, 5))
