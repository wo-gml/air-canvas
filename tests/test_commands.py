from air_canvas.config import GestureConfig
from air_canvas.core.types import CommandType, Gesture, Point
from air_canvas.gestures.commands import GestureCommandInterpreter


def command_types(commands):
    return [command.type for command in commands]


def test_draw_and_hover():
    interpreter = GestureCommandInterpreter(GestureConfig())
    pos = Point(100, 200)

    assert interpreter.update(Gesture.DRAW, pos) == []
    assert interpreter.update(Gesture.DRAW, pos) == []

    result = interpreter.update(Gesture.DRAW, pos)
    assert command_types(result) == [CommandType.PEN_DOWN]

    result = interpreter.update(Gesture.DRAW, Point(120, 200))
    assert command_types(result) == [CommandType.MOVE]

    interpreter.update(Gesture.HOVER, pos)
    interpreter.update(Gesture.HOVER, pos)

    result = interpreter.update(Gesture.HOVER, pos)
    assert command_types(result) == [CommandType.PEN_UP]


def test_fist_once():
    interpreter = GestureCommandInterpreter(GestureConfig())

    for _ in range(2):
        assert interpreter.update(Gesture.FIST, None) == []

    result = interpreter.update(Gesture.FIST, None)
    assert command_types(result) == [CommandType.RECOGNIZE]

    assert interpreter.update(Gesture.FIST, None) == []


def test_erase():
    interpreter = GestureCommandInterpreter(GestureConfig())
    pos = Point(100, 200)

    for _ in range(2):
        assert interpreter.update(Gesture.ERASE, pos) == []

    result = interpreter.update(Gesture.ERASE, pos)
    assert command_types(result) == [CommandType.ERASE]

    result = interpreter.update(Gesture.ERASE, pos)
    assert command_types(result) == [CommandType.ERASE]


def test_pinch_once():
    interpreter = GestureCommandInterpreter(GestureConfig())

    for _ in range(2):
        assert interpreter.update(Gesture.PINCH, None) == []

    result = interpreter.update(Gesture.PINCH, None)
    assert command_types(result) == [CommandType.CHANGE_COLOR]

    assert interpreter.update(Gesture.PINCH, None) == []


def test_hand_lost():
    interpreter = GestureCommandInterpreter(GestureConfig())
    pos = Point(100, 200)

    for _ in range(3):
        interpreter.update(Gesture.DRAW, pos)

    interpreter.update(Gesture.NONE, None)
    interpreter.update(Gesture.NONE, None)

    result = interpreter.update(Gesture.NONE, None)
    assert command_types(result) == [CommandType.PEN_UP]
