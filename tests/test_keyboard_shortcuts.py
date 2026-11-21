from air_canvas.app import KEY_COMMANDS
from air_canvas.core.types import CommandType


def test_clear_and_save():
    assert KEY_COMMANDS["c"] == CommandType.CLEAR
    assert KEY_COMMANDS["s"] == CommandType.SAVE


def test_other_shortcuts():
    assert KEY_COMMANDS["r"] == CommandType.RECOGNIZE
    assert KEY_COMMANDS["z"] == CommandType.UNDO
    assert KEY_COMMANDS["p"] == CommandType.CHANGE_COLOR
