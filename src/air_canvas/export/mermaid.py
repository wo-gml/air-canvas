"""인식 결과 -> Mermaid 다이어그램 코드 ("Code Canvas"). `core.interfaces.Exporter` 구현."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from air_canvas.core.types import RecognitionResult


class MermaidExporter:
    """허공에 그린 박스와 화살표를 flowchart 코드로 바꾼다.

    TODO(팀원 B):
    - 도형 -> 노드 (RECTANGLE: A[텍스트], CIRCLE: A((텍스트)))
    - 도형 안(bbox 포함)에 있는 텍스트 결과를 노드 라벨로 사용
    - LINE/ARROW의 양 끝점에 가장 가까운 노드를 찾아 A --> B 엣지 생성
    - 결과를 .mmd 파일로 저장 (README와 GitHub에서 바로 렌더링됨)
    """

    def export(self, results: Sequence[RecognitionResult], path: Path) -> Path:
        raise NotImplementedError("TODO(팀원 B): Mermaid 코드 생성")
