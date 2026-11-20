"""획(Stroke) 저장소. `core.interfaces.Canvas` 구현."""

from __future__ import annotations

from collections.abc import Sequence

from air_canvas.config import CanvasConfig
from air_canvas.core.types import Command, Stroke


class AirCanvas:
    """커맨드를 받아 획을 추가하고 지운다. 화면에 그리는 일은 Renderer 담당.

    TODO(팀원 A): apply()에서 CommandType별 처리
    - PEN_DOWN: 새 Stroke 시작 / MOVE: 현재 Stroke에 점 추가 / PEN_UP: 현재 Stroke 확정
    - ERASE: position 주변(eraser_radius) 점이 있는 획 제거
    - UNDO: 마지막 획 제거 / CLEAR: 전체 삭제
    - CHANGE_COLOR: payload["color"] 또는 팔레트 다음 색
    """

    def __init__(self, config: CanvasConfig) -> None:
        self.config = config
        self._strokes: list[Stroke] = []

    @property
    def strokes(self) -> Sequence[Stroke]:
        return self._strokes

    def apply(self, command: Command) -> None:
        raise NotImplementedError("TODO(팀원 A): 커맨드별 캔버스 상태 변경")
