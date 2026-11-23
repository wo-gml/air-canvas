"""테스트용 가짜 손그림(Stroke) 생성기.

카메라와 손 인식 없이도 도형 인식기를 개발하고 테스트할 수 있도록,
사람이 손가락으로 그린 것처럼 떨리고, 휘고, 덜 닫힌 획을 만든다.

- 좌표는 화면 픽셀 좌표 (core.types의 좌표 규칙과 같음)
- 같은 seed면 항상 같은 획이 나오므로 테스트에 그대로 쓸 수 있다
- sample_cases()는 "이 획은 이 도형으로 인식돼야 한다"는 정답이 붙은 예제 모음

미리보기 이미지: python -m tests.strokes  ->  outputs/fake_strokes.png
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, replace

import numpy as np

from air_canvas.core.types import Point, ShapeKind, Stroke


@dataclass(frozen=True)
class HandStyle:
    """손그림 느낌을 정하는 값. jitter / wobble 단위는 픽셀, gap / overshoot는 둘레 대비 비율."""

    jitter: float = 1.5  # 점마다 생기는 작은 떨림 (표준편차)
    wobble: float = 4.0  # 천천히 휘어지는 큰 흔들림 (최대 진폭)
    gap: float = 0.0  # 끝점이 시작점까지 못 돌아온 정도 (0.1이면 둘레의 10% 덜 그림)
    overshoot: float = 0.0  # 시작점을 지나쳐 더 그린 정도
    uneven_speed: float = 0.4  # 점 간격이 고르지 않은 정도 (0이면 일정)
    round_corners: float = 0.0  # 모서리 둥근 정도 (짧은 변 대비 비율, 0 ~ 0.5)
    random_start: bool = True  # 닫힌 도형을 둘레의 아무 지점에서나 그리기 시작
    num_points: int = 80


HAND = HandStyle()
NEAT = HandStyle(jitter=0, wobble=0, uneven_speed=0, random_start=False)
SHAKY = HandStyle(jitter=3.0, wobble=8.0, uneven_speed=0.6)


# --- 도형별 생성 함수 ---------------------------------------------------------


def polygon(
    vertices: Sequence[tuple[float, float]], style: HandStyle = HAND, seed: int = 0
) -> Stroke:
    """꼭짓점을 차례로 이어 한 붓으로 그린 닫힌 다각형."""
    path = np.asarray(vertices, dtype=float)
    path = _round_corners(path, style.round_corners)
    return _to_stroke(_trace(path, closed=True, style=style, rng=np.random.default_rng(seed)))


def rectangle(
    center: tuple[float, float] = (320, 240),
    width: float = 200,
    height: float = 140,
    angle: float = 0.0,
    style: HandStyle = HAND,
    seed: int = 0,
) -> Stroke:
    """사각형. angle은 도(degree) 단위 회전."""
    cx, cy = center
    w, h = width / 2, height / 2
    corners = np.array([(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h)])
    return polygon(_rotate(corners, center, angle), style, seed)


def triangle(
    center: tuple[float, float] = (320, 240),
    size: float = 200,
    angle: float = 0.0,
    style: HandStyle = HAND,
    seed: int = 0,
) -> Stroke:
    """꼭짓점이 위를 향한 정삼각형. size는 한 변의 길이."""
    cx, cy = center
    r = size / math.sqrt(3)  # 외접원 반지름
    corners = np.array(
        [
            (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in (-90, 30, 150)
        ]
    )
    return polygon(_rotate(corners, center, angle), style, seed)


def ellipse(
    center: tuple[float, float] = (320, 240),
    rx: float = 120,
    ry: float = 80,
    angle: float = 0.0,
    style: HandStyle = HAND,
    seed: int = 0,
) -> Stroke:
    """타원. 손으로 그린 원은 대부분 살짝 타원이 된다."""
    cx, cy = center
    a = np.linspace(0, 2 * math.pi, 96, endpoint=False)
    path = np.column_stack([cx + rx * np.cos(a), cy + ry * np.sin(a)])
    path = _rotate(path, center, angle)
    return _to_stroke(_trace(path, closed=True, style=style, rng=np.random.default_rng(seed)))


def circle(
    center: tuple[float, float] = (320, 240),
    radius: float = 100,
    style: HandStyle = HAND,
    seed: int = 0,
) -> Stroke:
    return ellipse(center, radius, radius, style=style, seed=seed)


def line(
    start: tuple[float, float] = (200, 240),
    end: tuple[float, float] = (440, 240),
    style: HandStyle = HAND,
    seed: int = 0,
) -> Stroke:
    """열린 직선. gap / overshoot / random_start는 쓰지 않는다."""
    path = np.array([start, end], dtype=float)
    return _to_stroke(_trace(path, closed=False, style=style, rng=np.random.default_rng(seed)))


def scribble(
    center: tuple[float, float] = (320, 240),
    size: float = 200,
    num_points: int = 80,
    seed: int = 0,
) -> Stroke:
    """어떤 도형도 아닌 낙서 (인식기가 거절해야 하는 경우)."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(0, size / 8, (num_points, 2))
    pts = np.cumsum(steps, axis=0)
    pts -= pts.mean(axis=0)
    span = np.ptp(pts, axis=0).max() or 1.0
    pts = pts / span * size + np.asarray(center, dtype=float)
    return _to_stroke(pts)


# --- 정답이 붙은 예제 모음 ----------------------------------------------------


@dataclass(frozen=True)
class StrokeCase:
    name: str
    expected: ShapeKind
    stroke: Stroke


def sample_cases(seed: int = 0) -> list[StrokeCase]:
    """인식기 개발과 테스트에 쓸 대표 손그림 모음. 이름은 cv2.putText용이라 영어."""
    R, T, C, L, U = (
        ShapeKind.RECTANGLE,
        ShapeKind.TRIANGLE,
        ShapeKind.CIRCLE,
        ShapeKind.LINE,
        ShapeKind.UNKNOWN,
    )
    s = seed
    return [
        StrokeCase("rect_neat", R, rectangle(style=NEAT, seed=s)),
        StrokeCase("rect_hand", R, rectangle(seed=s)),
        StrokeCase("rect_shaky", R, rectangle(style=SHAKY, seed=s)),
        StrokeCase("rect_rotated_25", R, rectangle(angle=25, seed=s)),
        StrokeCase("rect_wide_thin", R, rectangle(width=320, height=70, seed=s)),
        StrokeCase("rect_unclosed", R, rectangle(style=replace(HAND, gap=0.08), seed=s)),
        StrokeCase("rect_overshoot", R, rectangle(style=replace(HAND, overshoot=0.12), seed=s)),
        StrokeCase(
            "rect_round_corner", R, rectangle(style=replace(HAND, round_corners=0.25), seed=s)
        ),
        StrokeCase("tri_neat", T, triangle(style=NEAT, seed=s)),
        StrokeCase("tri_hand", T, triangle(seed=s)),
        StrokeCase("tri_shaky", T, triangle(style=SHAKY, seed=s)),
        StrokeCase("tri_upside_down", T, triangle(angle=180, seed=s)),
        StrokeCase("tri_tall", T, polygon([(320, 80), (380, 400), (260, 400)], seed=s)),
        StrokeCase("tri_unclosed", T, triangle(style=replace(HAND, gap=0.08), seed=s)),
        StrokeCase(
            "tri_round_corner", T, triangle(style=replace(HAND, round_corners=0.25), seed=s)
        ),
        StrokeCase("circle_neat", C, circle(style=NEAT, seed=s)),
        StrokeCase("circle_hand", C, circle(seed=s)),
        StrokeCase("circle_shaky", C, circle(style=SHAKY, seed=s)),
        StrokeCase("circle_small", C, circle(radius=30, style=replace(HAND, jitter=1.0), seed=s)),
        StrokeCase("circle_oval", C, ellipse(rx=130, ry=90, angle=15, seed=s)),
        StrokeCase("circle_unclosed", C, circle(style=replace(HAND, gap=0.1), seed=s)),
        StrokeCase("circle_overshoot", C, circle(style=replace(HAND, overshoot=0.15), seed=s)),
        StrokeCase("line_neat", L, line(style=NEAT, seed=s)),
        StrokeCase("line_hand", L, line(seed=s)),
        StrokeCase("line_diagonal", L, line((180, 360), (460, 120), seed=s)),
        StrokeCase("scribble", U, scribble(seed=s)),
    ]


# --- 내부 구현 ----------------------------------------------------------------


def _trace(
    path: np.ndarray, closed: bool, style: HandStyle, rng: np.random.Generator
) -> np.ndarray:
    """경로를 따라 손으로 그린 것처럼 점을 찍는다. 반환: (num_points, 2) 배열."""
    verts = np.vstack([path, path[:1]]) if closed else path
    seg = np.linalg.norm(np.diff(verts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]

    # 그리는 속도가 일정하지 않아 점 간격이 들쭉날쭉하다.
    n = style.num_points
    steps = np.clip(1 + style.uneven_speed * rng.uniform(-1, 1, n - 1), 0.05, None)
    t = np.concatenate([[0.0], np.cumsum(steps)])
    t /= t[-1]

    if closed:
        length = total * (1 - style.gap + style.overshoot)
        start = rng.uniform(0, total) if style.random_start else 0.0
        s = (start + t * length) % total
    else:
        s = t * total

    pts = np.column_stack([np.interp(s, cum, verts[:, 0]), np.interp(s, cum, verts[:, 1])])

    # 큰 흔들림: 주파수가 낮은 사인파 몇 개를 겹친 부드러운 휘어짐
    if style.wobble > 0:
        for axis in range(2):
            freq = rng.uniform(0.5, 2.0, 3)
            phase = rng.uniform(0, 2 * math.pi, 3)
            amp = rng.uniform(0.3, 1.0, 3)
            drift = (amp[:, None] * np.sin(2 * math.pi * freq[:, None] * t + phase[:, None])).sum(0)
            pts[:, axis] += drift * style.wobble / amp.sum()

    # 작은 떨림: 점마다 독립적인 노이즈
    if style.jitter > 0:
        pts += rng.normal(0, style.jitter, pts.shape)

    return pts


def _round_corners(path: np.ndarray, ratio: float, samples: int = 8) -> np.ndarray:
    """닫힌 다각형의 각 꼭짓점을 곡선으로 바꾼다.

    꼭짓점에서 양쪽 변을 따라 (짧은 변 길이 * ratio)만큼 떨어진 두 점을
    꼭짓점을 조절점으로 하는 2차 베지어 곡선으로 잇는다. 변의 가운데는 직선으로 남는다.
    """
    if ratio <= 0:
        return path
    t = np.linspace(0, 1, samples)[:, None]
    out = []
    for i, cur in enumerate(path):
        prev, nxt = path[i - 1], path[(i + 1) % len(path)]
        to_prev, to_next = prev - cur, nxt - cur
        d = ratio * min(np.linalg.norm(to_prev), np.linalg.norm(to_next))
        a = cur + to_prev / np.linalg.norm(to_prev) * d
        b = cur + to_next / np.linalg.norm(to_next) * d
        out.append((1 - t) ** 2 * a + 2 * (1 - t) * t * cur + t**2 * b)
    return np.vstack(out)


def _rotate(points: np.ndarray, center: tuple[float, float], angle: float) -> np.ndarray:
    th = math.radians(angle)
    c, s = math.cos(th), math.sin(th)
    origin = np.asarray(center, dtype=float)
    return (np.asarray(points, dtype=float) - origin) @ np.array([[c, s], [-s, c]]) + origin


def _to_stroke(pts: np.ndarray) -> Stroke:
    return Stroke(points=[Point(float(x), float(y)) for x, y in pts])


# --- 미리보기 -----------------------------------------------------------------


def render_preview(cases: Sequence[StrokeCase], cell: int = 220, cols: int = 6) -> np.ndarray:
    """예제를 격자로 그린 이미지. 초록 점 = 시작점, 빨간 점 = 끝점."""
    import cv2

    rows = math.ceil(len(cases) / cols)
    img = np.full((rows * cell, cols * cell, 3), 255, dtype=np.uint8)
    pad = 30
    for i, case in enumerate(cases):
        ox, oy = (i % cols) * cell, (i // cols) * cell
        pts = np.array(case.stroke.points)
        lo, span = pts.min(axis=0), max(np.ptp(pts, axis=0).max(), 1.0)
        scaled = (pts - lo) / span * (cell - 2 * pad) + (ox + pad, oy + pad)
        poly = scaled.round().astype(np.int32)
        cv2.rectangle(img, (ox, oy), (ox + cell - 1, oy + cell - 1), (220, 220, 220), 1)
        cv2.polylines(img, [poly], isClosed=False, color=(40, 40, 40), thickness=2)
        cv2.circle(img, tuple(int(v) for v in poly[0]), 5, (0, 170, 0), -1)
        cv2.circle(img, tuple(int(v) for v in poly[-1]), 5, (0, 0, 220), -1)
        cv2.putText(
            img, case.name, (ox + 6, oy + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (90, 90, 90), 1
        )
    return img


if __name__ == "__main__":
    from pathlib import Path

    import cv2

    out = Path("outputs/fake_strokes.png")
    out.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(out), render_preview(sample_cases()))
    print(f"saved {out}")
