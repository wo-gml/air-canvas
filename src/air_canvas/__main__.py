"""실행: `python -m air_canvas` 또는 설치 후 `air-canvas`."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from air_canvas.config import AppConfig


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="air-canvas", description="손동작으로 그리는 AI 화이트보드"
    )
    parser.add_argument("--camera", type=int, default=0, help="웹캠 번호 (기본 0)")
    parser.add_argument("--no-ocr", action="store_true", help="Hugging Face OCR 끄기 (도형 인식만)")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="저장 폴더")
    parser.add_argument("-v", "--verbose", action="store_true", help="디버그 로그 출력")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    config = AppConfig()
    config.camera.index = args.camera
    config.recognition.enable_ocr = not args.no_ocr
    config.output_dir = args.output_dir

    from air_canvas.app import run

    try:
        run(config)
    except NotImplementedError as e:
        print(f"아직 구현되지 않은 모듈이 있습니다: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
