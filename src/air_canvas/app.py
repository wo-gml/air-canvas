"""[팀원 C] 모든 모듈을 연결하는 파이프라인과 메인 루프.

    카메라 프레임
      -> HandTracker.detect          (A) 손 랜드마크
      -> GestureClassifier.classify  (C) 손 모양
      -> CommandInterpreter.update   (C) 커맨드
      -> Canvas.apply                (A) 획 저장
      -> Recognizer.recognize        (B) 도형/텍스트 인식 (RECOGNIZE 커맨드일 때만)
      -> Exporter.export             (B) SVG/Mermaid 저장 (SAVE 커맨드일 때만)
      -> Renderer.render             (A) 화면 출력

Pipeline은 Protocol에만 의존하므로 tests/에서 가짜 객체로 통합 테스트를 할 수 있습니다.
"""

from __future__ import annotations

import importlib.util
import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from air_canvas.config import AppConfig
from air_canvas.core.interfaces import (
    Canvas,
    CommandInterpreter,
    Exporter,
    GestureClassifier,
    HandTracker,
    PointFilter,
    Recognizer,
)
from air_canvas.core.types import (
    INDEX_TIP,
    Command,
    CommandType,
    Gesture,
    HandLandmarks,
    Point,
    RecognitionResult,
)

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

# 디버깅용 키보드 단축키 (제스처가 완성되기 전에도 기능 테스트 가능)
KEY_COMMANDS: dict[str, CommandType] = {
    "z": CommandType.UNDO,
    "c": CommandType.CLEAR,
    "r": CommandType.RECOGNIZE,
    "s": CommandType.SAVE,
    "p": CommandType.CHANGE_COLOR,
}


@dataclass
class FrameResult:
    """한 프레임 처리 결과 (화면 표시와 디버깅용)."""

    hand: HandLandmarks | None
    gesture: Gesture
    position: Point | None
    commands: list[Command] = field(default_factory=list)


class Pipeline:
    def __init__(
        self,
        tracker: HandTracker,
        classifier: GestureClassifier,
        interpreter: CommandInterpreter,
        canvas: Canvas,
        recognizer: Recognizer,
        exporters: Mapping[str, Exporter] | None = None,  # {".svg": SVGExporter(), ...}
        smoother: PointFilter | None = None,
        output_dir: Path = Path("outputs"),
    ) -> None:
        self.tracker = tracker
        self.classifier = classifier
        self.interpreter = interpreter
        self.canvas = canvas
        self.recognizer = recognizer
        self.exporters = dict(exporters or {})
        self.smoother = smoother
        self.output_dir = output_dir
        self.results: list[RecognitionResult] = []
        self.saved_paths: list[Path] = []

    def process(self, frame: np.ndarray) -> FrameResult:
        height, width = frame.shape[:2]
        hand = self.tracker.detect(frame)

        position: Point | None
        if hand is None:
            gesture, position = Gesture.NONE, None
            if self.smoother is not None:
                self.smoother.reset()
        else:
            gesture = self.classifier.classify(hand)
            position = hand.to_pixel(INDEX_TIP, width, height)
            if self.smoother is not None:
                position = self.smoother.update(position)

        commands = self.interpreter.update(gesture, position)
        for command in commands:
            self.handle(command)
        return FrameResult(hand=hand, gesture=gesture, position=position, commands=commands)

    def handle(self, command: Command) -> None:
        """커맨드 하나 실행. 인식/저장은 앱이, 나머지는 캔버스가 처리한다."""
        if command.type is CommandType.RECOGNIZE:
            self.results = self.recognizer.recognize(self.canvas.strokes)
        elif command.type is CommandType.SAVE:
            self.save()
        else:
            self.canvas.apply(command)
            if command.type in (CommandType.CLEAR, CommandType.UNDO, CommandType.ERASE):
                self.results = []  # 획이 바뀌었으니 이전 인식 결과는 무효

    def save(self) -> list[Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stem = datetime.now().strftime("canvas-%Y%m%d-%H%M%S")
        paths = [
            exporter.export(self.results, self.output_dir / f"{stem}{suffix}")
            for suffix, exporter in self.exporters.items()
        ]
        self.saved_paths.extend(paths)
        return paths


def build_pipeline(config: AppConfig) -> Pipeline:
    """실제 구현체로 파이프라인 조립."""
    from air_canvas.canvas import AirCanvas
    from air_canvas.export import MermaidExporter, SVGExporter
    from air_canvas.gestures import GestureCommandInterpreter, RuleBasedGestureClassifier
    from air_canvas.recognition import CompositeRecognizer, ShapeRecognizer
    from air_canvas.tracking import MediaPipeHandTracker, PointSmoother

    text_recognizer = None
    if config.recognition.enable_ocr:
        if importlib.util.find_spec("transformers") is None:
            logger.warning('transformers가 없어 OCR을 끕니다. 설치: pip install -e ".[ocr]"')
        else:
            from air_canvas.recognition.ocr import HFTextRecognizer

            text_recognizer = HFTextRecognizer(config.recognition)

    return Pipeline(
        tracker=MediaPipeHandTracker(config.tracking),
        classifier=RuleBasedGestureClassifier(config.gesture),
        interpreter=GestureCommandInterpreter(config.gesture),
        canvas=AirCanvas(config.canvas),
        recognizer=CompositeRecognizer(ShapeRecognizer(config.recognition), text_recognizer),
        exporters={".svg": SVGExporter(), ".mmd": MermaidExporter()},
        smoother=PointSmoother(config.tracking.smoothing_alpha),
        output_dir=config.output_dir,
    )


def run(config: AppConfig) -> None:
    """웹캠 메인 루프. q 또는 ESC로 종료."""
    import cv2

    from air_canvas.canvas import OpenCVRenderer
    from air_canvas.tracking import Camera

    pipeline = build_pipeline(config)
    renderer = OpenCVRenderer()
    key_commands = {ord(k): v for k, v in KEY_COMMANDS.items()}

    try:
        with Camera(config.camera) as camera:
            while True:
                frame = camera.read()
                if frame is None:
                    break
                pipeline.process(frame)
                cv2.imshow(
                    "Air Canvas", renderer.render(frame, pipeline.canvas.strokes, pipeline.results)
                )

                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
                if key in key_commands:
                    pipeline.handle(Command(key_commands[key]))
    finally:
        pipeline.tracker.close()
        cv2.destroyAllWindows()
