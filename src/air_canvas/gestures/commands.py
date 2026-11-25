"""손 모양을 실제 프로그램 명령으로 바꾸는 모듈."""

from __future__ import annotations

from air_canvas.config import GestureConfig
from air_canvas.core.types import Command, CommandType, Gesture, Point


class GestureCommandInterpreter:
    def __init__(self, config: GestureConfig) -> None:
        self.config = config
        self.current = Gesture.NONE
        self.candidate = Gesture.NONE
        self.count = 0
        self.pen_down = False

    def update(self, gesture: Gesture, position: Point | None) -> list[Command]:
        commands = []

        if gesture == self.candidate:
            self.count += 1
        else:
            self.candidate = gesture
            self.count = 1

        if self.count >= self.config.debounce_frames and self.candidate != self.current:
            if self.current == Gesture.DRAW and self.pen_down:
                commands.append(Command(CommandType.PEN_UP))
                self.pen_down = False

            self.current = self.candidate

            if self.current == Gesture.FIST:
                commands.append(Command(CommandType.RECOGNIZE))

            elif self.current == Gesture.PINCH:
                commands.append(Command(CommandType.CHANGE_COLOR))

        if self.current == Gesture.DRAW and position is not None:
            if not self.pen_down:
                commands.append(Command(CommandType.PEN_DOWN, position))
                self.pen_down = True
            else:
                commands.append(Command(CommandType.MOVE, position))

        elif self.current == Gesture.ERASE and position is not None:
            commands.append(Command(CommandType.ERASE, position))

        return commands
