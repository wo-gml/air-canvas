"""손가락 끝 좌표 떨림 보정."""

from __future__ import annotations

from air_canvas.core.types import Point


class PointSmoother:
    """지수이동평균(EMA)으로 손가락 좌표를 보정한다."""

    def __init__(self, alpha: float = 0.5) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha는 0보다 크고 1 이하여야 합니다.")

        self.alpha = alpha
        self._previous: Point | None = None

    def update(self, point: Point) -> Point:
        """현재 좌표를 이전 보정 좌표와 평균 낸다."""

        if self._previous is None:
            self._previous = point
            return point

        x = self.alpha * point.x + (1 - self.alpha) * self._previous.x
        y = self.alpha * point.y + (1 - self.alpha) * self._previous.y

        smoothed = Point(x, y)
        self._previous = smoothed

        return smoothed

    def reset(self) -> None:
        """이전 좌표를 초기화한다."""
        self._previous = None
