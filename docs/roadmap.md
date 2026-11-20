# 로드맵과 초기 이슈 목록

이슈 폼(Issues → New issue → 이슈 생성)으로 등록하세요. 괄호 안은 자동 생성될 브랜치 이름 예시입니다.

## v0.1 MVP: 허공에 사각형 그리기 → 깨끗한 사각형

### 팀원 A: tracking / canvas
- [ ] 웹캠 래퍼 `Camera` 구현 (`feat/#번호-camera`)
- [ ] MediaPipe HandLandmarker로 `MediaPipeHandTracker` 구현 (`feat/#번호-hand-tracker`)
- [ ] 검지 끝 좌표 스무딩 `PointSmoother` (EMA) (`feat/#번호-smoothing`)
- [ ] `AirCanvas` 커맨드 처리 (PEN_DOWN/MOVE/PEN_UP/UNDO/CLEAR) (`feat/#번호-air-canvas`)
- [ ] `OpenCVRenderer` 획 그리기 + 상태 표시 UI (`feat/#번호-renderer`)

### 팀원 B: recognition / export
- [ ] `strokes_to_image` 전처리 (`feat/#번호-preprocess`)
- [ ] `ShapeRecognizer`: 사각형, 원, 삼각형, 선 인식 (`feat/#번호-shape-recognizer`)
- [ ] Renderer에서 쓸 '깨끗한 도형' 좌표 계산 (A와 협업)
- [ ] `SVGExporter` (`feat/#번호-svg-export`)

### 팀원 C: gestures / app / tests
- [ ] `RuleBasedGestureClassifier`: 손가락 펴짐 판정, DRAW/HOVER/ERASE/FIST (`feat/#번호-gesture-classifier`)
- [ ] `GestureCommandInterpreter`: debounce 상태 머신 (`feat/#번호-command-interpreter`)
- [ ] 랜드마크 녹화 스크립트 `scripts/record_landmarks.py` → `tests/fixtures/*.json` (`test/#번호-landmark-fixtures`)
- [ ] 실제 구현체를 하나씩 끼운 통합 테스트 확장

### 공통
- [ ] 데모 GIF 촬영 후 README에 추가 (`docs/#번호-demo-gif`)

## v0.2: AI 인식과 Code Canvas
- [ ] (B) `HFTextRecognizer`: TrOCR 손글씨 인식, 한국어 모델 조사
- [ ] (B) `MermaidExporter`: 박스 + 화살표 → flowchart 코드
- [ ] (B) ARROW 도형 인식
- [ ] (C) PINCH 제스처로 색 변경, ERASE 지우개
- [ ] (A) 인식된 텍스트를 화면에 표시 (한글 폰트)

## 이후 아이디어
- 두 손 제스처 (확대/축소, 이동)
- Image-to-Image 파이프라인으로 스케치 → 그림 생성
- 웹 데모 (Gradio, Hugging Face Spaces)
