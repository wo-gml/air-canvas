# Air Canvas ✋🖊️

> 손동작으로 그리는 AI 스마트 화이트보드 (Gesture-to-Image / Code Canvas)

키보드나 마우스 없이, 허공에서 손가락으로 그린 그림과 글씨를 AI가 인식해
**깨끗한 디지털 도형, 텍스트, 다이어그램 코드(Mermaid)** 로 바꿔주는 인터랙티브 도구입니다.

<!-- 데모 GIF가 준비되면 아래 주석을 해제하세요 -->
<!-- ![demo](assets/demo.gif) -->

## 주요 기능

- **에어 드로잉**: 검지 끝을 펜처럼 써서 허공에 그리기 (MediaPipe Hands)
- **제스처 커맨드**: 손 모양만으로 그리기, 지우기, 색 변경, 인식, 저장
- **실시간 도형 보정**: 손으로 그린 사각형/원/삼각형/선을 깨끗한 도형으로 변환
- **손글씨 인식**: Hugging Face OCR 모델로 공중에 쓴 글씨를 텍스트로 변환
- **Code Canvas**: 그린 박스와 화살표를 Mermaid flowchart 코드로 내보내기

## 제스처

| 손 모양 | 동작 |
|---|---|
| ☝️ 검지만 펴기 | 그리기 |
| ✌️ 검지 + 중지 | 펜 들고 이동 |
| 🖐️ 손바닥 펴기 | 지우개 |
| 🤏 엄지 + 검지 집기 | 색 변경 |
| ✊ 주먹 | AI 인식 실행 |

디버깅용 키보드 단축키: `r` 인식, `s` 저장, `z` 되돌리기, `c` 전체 지우기, `p` 색 변경, `q`/`ESC` 종료

## 동작 구조

```mermaid
flowchart LR
    Cam[웹캠] --> Track[tracking<br/>손 랜드마크]
    Track --> Gest[gestures<br/>손 모양 → 커맨드]
    Gest --> Canvas[canvas<br/>획 저장]
    Canvas --> Rec[recognition<br/>도형 + OCR]
    Rec --> Render[canvas.renderer<br/>화면 출력]
    Rec --> Export[export<br/>SVG / Mermaid]
```

자세한 설계와 모듈 간 계약은 [docs/architecture.md](docs/architecture.md)를 참고하세요.

## 사용한 패키지와 버전

아래 버전으로 설치와 테스트를 확인했습니다. 설치는 [시작하기](#시작하기)의 `pip install` 한 번으로 끝납니다.

| 패키지 | 버전 | 용도 |
|---|---|---|
| Python | 3.11.18 | |
| [mediapipe](https://pypi.org/project/mediapipe/) | 1.2.3 | 손 랜드마크 추적 (Hand Landmarker) |
| [opencv-contrib-python](https://pypi.org/project/opencv-contrib-python/) | 5.1.0.95 | 웹캠 입력, 그리기, 도형 인식 |
| [numpy](https://pypi.org/project/numpy/) | 2.4.6 | 좌표와 이미지 배열 처리 |
| [transformers](https://pypi.org/project/transformers/) | 구현 후 기재 | (선택) Hugging Face 손글씨 OCR |
| [torch](https://pypi.org/project/torch/) | 구현 후 기재 | (선택) transformers 실행 백엔드 |
| [pytest](https://pypi.org/project/pytest/) | 9.2.0 | (개발) 테스트 |
| [ruff](https://pypi.org/project/ruff/) | 0.17.6 | (개발) 린트와 포맷 |

## 시작하기

> **Python 3.11** 사용을 권장합니다. CI와 같은 버전이고, OCR에 쓰는 `torch`는 Python 3.15용 패키지가 아직 없습니다.
> macOS: `brew install python@3.11`

```bash
git clone https://github.com/wo-gml/air-canvas.git
cd air-canvas
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"            # 기본 + 개발 도구
pip install -e ".[ocr]"            # (선택) Hugging Face 손글씨 OCR
pre-commit install
```

손 추적 모델을 받아 `models/hand_landmarker.task` 에 저장합니다.
([MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker))

```bash
python -m air_canvas               # 실행
python -m air_canvas --no-ocr      # OCR 없이 도형 인식만
pytest                             # 테스트
```

## 프로젝트 구조

```
src/air_canvas/
├── core/          공통 타입과 인터페이스 (모듈 간 계약)
├── tracking/      웹캠, MediaPipe 손 추적, 좌표 떨림 보정
├── canvas/        획 저장소와 OpenCV 렌더링
├── gestures/      손 모양 판정과 제스처 → 커맨드 상태 머신
├── recognition/   도형 인식(OpenCV) + 손글씨 OCR(Hugging Face)
├── export/        SVG / Mermaid 내보내기
├── app.py         파이프라인 조립과 메인 루프
└── config.py      튜닝 값 모음
tests/             가짜 객체 기반 단위·통합 테스트
docs/              설계 문서, 로드맵
```

## 팀

| 역할 | 담당 모듈 | 담당자 |
|---|---|---|
| 팀원 A | 손가락 마디 추적, 공중 캔버스 궤적 렌더링 (`tracking/`, `canvas/`) | |
| 팀원 B | Hugging Face 추론 래퍼, 궤적 → 텍스트/도형 변환 (`recognition/`, `export/`) | |
| 팀원 C | 제스처 커맨드 파서, 통합 테스트 (`gestures/`, `app.py`, `tests/`) | |

## 기여하기

작업 브랜치를 `main`으로 PR하고, 리뷰를 받은 뒤 merge commit으로 병합합니다 (GitHub Flow).
브랜치 이름, 커밋 규칙, PR 절차는 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 참고 자료

참고한 문서, 논문, 블로그, 영상, 코드는 모두 여기에 추가합니다.

**손 추적**
- [MediaPipe Hand Landmarker 가이드](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker): 21개 손 랜드마크 정의와 모델 파일
- [MediaPipe Hand Landmarker Python 가이드](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python): Tasks API 사용법
- [1€ Filter](https://gery.casiez.net/1euro/): Casiez et al., CHI 2012. 손가락 좌표 떨림 보정

**인식**
- [OpenCV Contour Features](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html): `approxPolyDP` 로 도형 꼭짓점 근사
- [microsoft/trocr-small-handwritten](https://huggingface.co/microsoft/trocr-small-handwritten): 손글씨 OCR 모델 카드
- [TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models](https://arxiv.org/abs/2109.10282): Li et al., 2021

**내보내기 / 개발 도구**
- [Mermaid Flowchart 문법](https://mermaid.js.org/syntax/flowchart.html)
- [Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/)
- [Ruff](https://docs.astral.sh/ruff/)

## 라이선스

[MIT](LICENSE)

사용하는 외부 모델의 라이선스는 각 모델 카드를 따릅니다.
- MediaPipe Hand Landmarker: Apache-2.0
- Hugging Face OCR 모델: 사용하는 모델 카드에서 확인 후 여기에 기재
