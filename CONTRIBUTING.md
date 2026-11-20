# 기여 가이드

## 꼭 지켜야 할 과제 규칙

- **채점은 `main` 브랜치만 봅니다.** 모든 작업은 마감 전에 `main`에 병합되어 있어야 합니다.
- **팀원 모두 자기 계정으로 커밋하고 PR을 올립니다.** 커밋이 한 번도 없는 팀원은 0점입니다.
  팀장이 대신 push하지 않고, 각자 PR을 올리면 팀장이 리뷰·승인해서 병합합니다.
- **커밋과 병합 기록이 남아야 합니다.** 그래서 PR은 **Create a merge commit** 으로만 병합합니다.
- **마감 시각 이후에는 push와 PR 병합을 하지 않습니다.** (발견 시 0점)
- **참고한 자료는 반드시 README의 "참고 자료"에 추가합니다.** (문서, 블로그, 영상, 코드)

## 처음 한 번 준비

1. 팀장이 보낸 Collaborator 초대를 수락합니다. (GitHub 알림 또는 이메일)
2. 내 컴퓨터에 받아서 개발 환경을 만듭니다.
   ```bash
   git clone https://github.com/wo-gml/air-canvas.git
   cd air-canvas
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   pre-commit install
   ```
3. 커밋에 내 GitHub 계정이 찍히도록 이름과 이메일을 설정합니다.
   이메일은 GitHub에 등록된 주소여야 잔디와 기여 기록에 반영됩니다.
   ```bash
   git config user.name "내 GitHub 아이디"
   git config user.email "GitHub에 등록한 이메일"
   ```

## 브랜치 전략 (GitHub Flow)

| 브랜치 | 용도 | 규칙 |
|---|---|---|
| `main` | 채점 대상, 항상 실행 가능한 상태 | 직접 push 금지. PR로만 병합 |
| `<type>/<이슈번호>-<설명>` | 작업 브랜치 | `main`에서 분기, 작업 후 `main`으로 PR |

브랜치 type: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`

```
feat/3-hand-tracking
feat/7-hf-ocr-wrapper
fix/12-stroke-jitter
docs/15-readme-demo-gif
```

## 작업 순서

1. **이슈 만들기**: 템플릿을 사용하고 라벨과 마일스톤을 지정합니다. 이슈 없이 작업하지 않습니다.
2. **브랜치 만들기**
   ```bash
   git switch main
   git pull
   git switch -c feat/3-hand-tracking
   ```
3. **작업하고 커밋하기**: 아래 커밋 규칙을 따르고, 작은 단위로 자주 커밋합니다.
4. **올리기 전에 최신 main 반영**: 충돌이 나면 내 브랜치에서 해결합니다.
   ```bash
   git pull origin main
   git push -u origin feat/3-hand-tracking
   ```
5. **PR 열기**: base는 `main`, 본문에 `Closes #3`
6. **리뷰 받기**: 승인 1명 이상, CI 통과 후 **Create a merge commit** 으로 병합하고 작업 브랜치를 삭제합니다.

## 커밋 메시지 (Conventional Commits)

```
<type>(<scope>): <요약> (#이슈번호)
```

- type: `feat` `fix` `refactor` `test` `docs` `chore` `ci` `build`
- scope: `core` `tracking` `canvas` `gestures` `recognition` `export` `app`

```
feat(tracking): 검지 끝 좌표 지수 이동평균 스무딩 추가 (#3)
fix(recognition): 빈 캔버스 입력 시 예외 처리 (#9)
test(gestures): debounce 상태 전환 테스트 추가 (#11)
docs(readme): 데모 GIF 추가 (#15)
```

## 코드 규칙

- 포맷과 린트는 **ruff**로 통일합니다. `pre-commit install` 을 하면 커밋할 때 자동 검사합니다.
  ```bash
  ruff check . --fix
  ruff format .
  ```
- 임계값 같은 숫자는 코드에 직접 쓰지 말고 `config.py` 에 추가합니다.
- 모듈끼리는 `core/interfaces.py` 의 Protocol과 `core/types.py` 의 타입으로만 주고받습니다.
  다른 팀원 모듈의 내부 함수를 직접 import하지 않습니다.
- **`core/` 를 바꾸는 PR은 모든 팀원에게 리뷰를 요청합니다.** (모두가 의존하는 계약)
- 모델 가중치, 녹화 영상 같은 큰 파일은 커밋하지 않습니다. (`.gitignore` 참고)
- 새 패키지를 추가하면 `pyproject.toml` 과 README의 "사용한 패키지와 버전" 표를 함께 고칩니다.

## 테스트

- 새 기능에는 단위 테스트를 함께 추가합니다.
- CI에는 웹캠과 GPU가 없습니다. 카메라나 모델이 필요한 부분은 `tests/fakes.py` 의 가짜 객체나
  `tests/fixtures/` 에 저장한 랜드마크 데이터로 테스트합니다.
- 실제 웹캠이 필요한 확인은 PR 본문의 "테스트 방법"에 적고, 가능하면 GIF를 첨부합니다.

## 버전 태그

마일스톤을 마치면 `main` 에 태그를 답니다.

```bash
git switch main
git pull
git tag -a v0.1.0 -m "v0.1.0: MVP"
git push origin v0.1.0
```
