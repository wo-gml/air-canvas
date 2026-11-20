"""파이프라인 통합 테스트 (모든 모듈을 가짜 객체로 대체).

실제 모듈이 완성되면 가짜 객체를 하나씩 실제 구현으로 바꿔 통합 테스트를 늘려가세요.
"""

from air_canvas.app import Pipeline
from air_canvas.core.types import Command, CommandType, Gesture, Point
from tests.fakes import (
    FakeCanvas,
    FakeClassifier,
    FakeExporter,
    FakeInterpreter,
    FakeRecognizer,
    FakeTracker,
    make_hand,
)


def make_pipeline(hands, gestures, **kwargs):
    canvas = FakeCanvas()
    recognizer = FakeRecognizer()
    pipeline = Pipeline(
        tracker=FakeTracker(hands),
        classifier=FakeClassifier(gestures),
        interpreter=FakeInterpreter(),
        canvas=canvas,
        recognizer=recognizer,
        **kwargs,
    )
    return pipeline, canvas, recognizer


def test_draw_gesture_creates_stroke_in_pixel_coords(frame):
    hands = [make_hand((0.1, 0.1)), make_hand((0.2, 0.1)), make_hand((0.2, 0.2))]
    pipeline, canvas, _ = make_pipeline(hands, [Gesture.DRAW] * 3)

    for _ in hands:
        pipeline.process(frame)

    assert len(canvas.strokes) == 1
    assert canvas.strokes[0].points == [Point(64, 48), Point(128, 48), Point(128, 96)]


def test_hand_lost_lifts_pen(frame):
    pipeline, canvas, _ = make_pipeline([make_hand(), None], [Gesture.DRAW])

    pipeline.process(frame)
    result = pipeline.process(frame)

    assert result.gesture is Gesture.NONE
    assert result.position is None
    assert canvas.applied[-1].type is CommandType.PEN_UP


def test_fist_triggers_recognition(frame):
    hands = [make_hand(), make_hand(), make_hand()]
    pipeline, _, recognizer = make_pipeline(hands, [Gesture.DRAW, Gesture.DRAW, Gesture.FIST])

    for _ in hands:
        pipeline.process(frame)

    assert recognizer.calls == 1
    assert len(pipeline.results) == 1


def test_clear_resets_results(frame):
    pipeline, _, _ = make_pipeline([make_hand(), make_hand()], [Gesture.DRAW, Gesture.FIST])
    pipeline.process(frame)
    pipeline.process(frame)
    assert pipeline.results

    pipeline.handle(Command(CommandType.CLEAR))

    assert pipeline.results == []


def test_save_calls_every_exporter(tmp_path):
    svg, mmd = FakeExporter(), FakeExporter()
    pipeline, _, _ = make_pipeline(
        [], [], exporters={".svg": svg, ".mmd": mmd}, output_dir=tmp_path
    )

    pipeline.handle(Command(CommandType.SAVE))

    assert svg.exported[0][1].suffix == ".svg"
    assert mmd.exported[0][1].suffix == ".mmd"
    assert all(p.parent == tmp_path for p in pipeline.saved_paths)
