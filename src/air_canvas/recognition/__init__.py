"""[팀원 B] 그린 획을 도형/텍스트로 인식.

- shape.py: OpenCV 기하 연산 기반 도형 인식 (가볍고 빨라서 실시간용)
- ocr.py:   Hugging Face 손글씨 OCR (무거우므로 '인식' 제스처 때만 실행)
- composite.py: 두 인식기를 묶어 하나의 Recognizer로 제공
"""

from air_canvas.recognition.composite import CompositeRecognizer
from air_canvas.recognition.shape import ShapeRecognizer

__all__ = ["CompositeRecognizer", "ShapeRecognizer"]
