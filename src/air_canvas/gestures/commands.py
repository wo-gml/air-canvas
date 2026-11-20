"""제스처 흐름 -> 커맨드. `core.interfaces.CommandInterpreter` 구현."""

from __future__ import annotations

from air_canvas.config import GestureConfig
from air_canvas.core.types import Command, Gesture, Point


class GestureCommandInterpreter:
    """제스처를 프레임 단위로 받아 커맨드로 바꾸는 상태 머신.

    TODO(팀원 C):
    - debounce: 같은 제스처가 config.debounce_frames 프레임 연속일 때만 상태 전환
    - 상태 전환 규칙 예시
        (아무 상태) -> DRAW      : [PEN_DOWN(pos)]
        DRAW 유지                : [MOVE(pos)]
        DRAW -> 다른 제스처      : [PEN_UP]
        ERASE 유지               : [ERASE(pos)]
        FIST로 바뀌는 순간 1번   : [RECOGNIZE]
        PINCH로 바뀌는 순간 1번  : [CHANGE_COLOR]
    - 키보드 단축키(z/c/r/s)는 app.py에서 이미 Command로 처리하므로 여기서는 제스처만 담당
    """

    def __init__(self, config: GestureConfig) -> None:
        self.config = config

    def update(self, gesture: Gesture, position: Point | None) -> list[Command]:
        raise NotImplementedError("TODO(팀원 C): 제스처 상태 머신")
