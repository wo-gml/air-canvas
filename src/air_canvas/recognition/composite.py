"""여러 인식기를 묶어 하나처럼 쓰는 Recognizer."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from air_canvas.core.interfaces import Recognizer
from air_canvas.core.types import RecognitionResult, Stroke


class CompositeRecognizer:
    """도형 인식기를 먼저 돌리고, 도형으로 인식되지 않은 획만 OCR에 넘긴다."""

    def __init__(self, shape: Recognizer, text: Recognizer | None = None) -> None:
        self.shape = shape
        self.text = text

    def recognize(self, strokes: Sequence[Stroke]) -> list[RecognitionResult]:
        results = self.shape.recognize(strokes)
        if self.text is None:
            return results

        used = {i for r in results for i in r.stroke_indices}
        leftover = [s for i, s in enumerate(strokes) if i not in used]
        if not leftover:
            return results

        # OCR 결과의 stroke_indices를 원래 strokes 기준 인덱스로 되돌린다.
        index_map = [i for i in range(len(strokes)) if i not in used]
        # replace로 인덱스만 바꿔야 outline 등 나머지 필드가 빠지지 않는다.
        for r in self.text.recognize(leftover):
            mapped = tuple(index_map[i] for i in r.stroke_indices)
            results.append(replace(r, stroke_indices=mapped))
        return results
