"""획(Stroke) 저장소. core.interfaces.Canvas 구현."""

from __future__ import annotations

from collections.abc import Sequence

from air_canvas.config import CanvasConfig
from air_canvas.core.types import Command, CommandType, Point, Stroke


class AirCanvas:
    """커맨드를 받아 획을 생성, 추가, 삭제 및 관리한다."""

    def __init__(self, config: CanvasConfig) -> None:
        self.config = config

        self._strokes: list[Stroke] = []
        self._current_stroke: Stroke | None = None

        self._color_index = 0
        self._current_color = config.palette[0] if config.palette else (0, 0, 255)

    @property
    def strokes(self) -> Sequence[Stroke]:
        """저장된 획 목록을 반환한다."""
        return self._strokes

    def apply(self, command: Command) -> None:
        """명령 종류에 따라 캔버스 상태를 변경한다."""

        if command.type is CommandType.PEN_DOWN:
            self._pen_down(command.position)

        elif command.type is CommandType.MOVE:
            self._move(command.position)

        elif command.type is CommandType.PEN_UP:
            self._pen_up()

        elif command.type is CommandType.CLEAR:
            self._clear()

        elif command.type is CommandType.UNDO:
            self._undo()

        elif command.type is CommandType.ERASE:
            self._erase(command.position)

        elif command.type is CommandType.CHANGE_COLOR:
            self._change_color(command.payload)

    def _pen_down(self, position: Point | None) -> None:
        """새로운 획을 시작한다."""

        if position is None:
            return

        stroke = Stroke(
            points=[position],
            color=self._current_color,
            thickness=self.config.thickness,
        )

        self._strokes.append(stroke)
        self._current_stroke = stroke

    def _move(self, position: Point | None) -> None:
        """현재 그리고 있는 획에 새로운 좌표를 추가한다."""

        if position is None or self._current_stroke is None:
            return

        self._current_stroke.points.append(position)

    def _pen_up(self) -> None:
        """현재 획 그리기를 종료한다."""

        self._current_stroke = None

    def _clear(self) -> None:
        """모든 획을 삭제한다."""

        self._strokes.clear()
        self._current_stroke = None

    def _undo(self) -> None:
        """가장 마지막 획을 삭제한다."""

        if self._strokes:
            self._strokes.pop()

        self._current_stroke = None

    def _erase(self, position: Point | None) -> None:
        """지우개 반경 안에 점이 있는 획을 삭제한다."""

        if position is None:
            return

        radius_squared = self.config.eraser_radius**2

        remaining_strokes = []

        for stroke in self._strokes:
            should_erase = False

            for point in stroke.points:
                distance_squared = (point.x - position.x) ** 2 + (point.y - position.y) ** 2

                if distance_squared <= radius_squared:
                    should_erase = True
                    break

            if not should_erase:
                remaining_strokes.append(stroke)

        self._strokes = remaining_strokes
        self._current_stroke = None

    def _change_color(self, payload: dict) -> None:
        """펜 색상을 변경한다."""

        if "color" in payload:
            self._current_color = tuple(payload["color"])
            return

        if not self.config.palette:
            return

        self._color_index = (self._color_index + 1) % len(self.config.palette)

        self._current_color = self.config.palette[self._color_index]
