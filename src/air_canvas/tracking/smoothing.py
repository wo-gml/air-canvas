"""손가락 끝 좌표 떨림 보정."""

from __future__ import annotations

from air_canvas.core.types import Point


class PointSmoother:
    """손 떨림으로 선이 지글거리지 않게 좌표를 부드럽게 만든다.

    TODO(팀원 A):
    - 지수 이동평균(EMA)부터 구현: s = alpha * p + (1 - alpha) * s_prev
    - 여유가 되면 One Euro Filter로 교체 (느릴 땐 부드럽게, 빠를 땐 지연 없이)
    - reset(): 펜을 들었을 때 이전 좌표를 잊기
    """

    def __init__(self, alpha: float = 0.5) -> None:
        self.alpha = alpha

    def update(self, point: Point) -> Point:
        raise NotImplementedError("TODO(팀원 A): 좌표 스무딩")

    def reset(self) -> None:
        raise NotImplementedError("TODO(팀원 A): 스무딩 상태 초기화")
