"""Hugging Face 손글씨 OCR. `core.interfaces.Recognizer` 구현.

설치: pip install -e ".[ocr]"  (transformers, torch)
"""

from __future__ import annotations

from collections.abc import Sequence

from air_canvas.config import RecognitionConfig
from air_canvas.core.types import RecognitionResult, Stroke


class HFTextRecognizer:
    """TODO(팀원 B):
    - transformers의 TrOCRProcessor + VisionEncoderDecoderModel 로드
      (config.ocr_model_id, 기본값 microsoft/trocr-small-handwritten)
    - 모델 로드는 느리니 첫 recognize() 호출 때 한 번만 (lazy load)
    - preprocess.strokes_to_image()로 만든 이미지를 넣어 텍스트 추출
    - 한글이 필요하면 한국어 손글씨 OCR 모델 후보를 조사해서 README에 정리
    - transformers가 설치 안 된 환경에서도 앱이 죽지 않도록 ImportError 처리
    """

    def __init__(self, config: RecognitionConfig) -> None:
        self.config = config
        self._model = None
        self._processor = None

    def recognize(self, strokes: Sequence[Stroke]) -> list[RecognitionResult]:
        raise NotImplementedError("TODO(팀원 B): Hugging Face OCR 추론")
