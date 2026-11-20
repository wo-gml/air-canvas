"""인식 결과 -> SVG 이미지. `core.interfaces.Exporter` 구현."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from air_canvas.core.types import RecognitionResult


class SVGExporter:
    """TODO(팀원 B):
    - RECTANGLE -> <rect>, CIRCLE -> <ellipse>, TRIANGLE -> <polygon>, LINE -> <line>
    - 텍스트 -> <text>
    - 외부 라이브러리 없이 문자열로 SVG 작성 (테스트하기 쉬움)
    """

    def export(self, results: Sequence[RecognitionResult], path: Path) -> Path:
        raise NotImplementedError("TODO(팀원 B): SVG 내보내기")
