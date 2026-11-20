# 기여 가이드

## 브랜치 전략

| 브랜치 | 용도 | 규칙 |
|---|---|---|
| `main` | 항상 데모가 돌아가는 안정 버전 | 직접 push 금지. `develop`에서만 병합하고 병합 시 태그(`v0.1.0`) |
| `develop` | 통합 브랜치 | 직접 push 금지. 작업 브랜치의 PR만 받음 |
| `<type>/<이슈번호>-<설명>` | 작업 브랜치 | `develop`에서 분기, 작업 후 `develop`으로 PR |

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
   git switch develop
   git pull
   git switch -c feat/3-hand-tracking
   ```
3. **작업하고 커밋하기**: 아래 커밋 규칙을 따릅니다.
4. **최신 develop 반영**: PR 전에 충돌을 미리 해결합니다.
   ```bash
   git fetch origin
   git rebase origin/develop
   ```
5. **PR 열기**: base는 `develop`, 본문에 `Closes #3`
6. **리뷰 받기**: 승인 1명 이상, CI 통과 후 **Squash and merge**, 작업 브랜치 삭제

## 커밋 메시지 (Conventional Commits)

```
<type>(<scope>): <요약> (#이슈번호)
```

- type: `feat` `fix` `refactor` `test` `docs` `chore` `ci`
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

## 테스트

- 새 기능에는 단위 테스트를 함께 추가합니다.
- CI에는 웹캠과 GPU가 없습니다. 카메라나 모델이 필요한 부분은 `tests/fakes.py` 의 가짜 객체나
  `tests/fixtures/` 에 저장한 랜드마크 데이터로 테스트합니다.
- 실제 웹캠이 필요한 확인은 PR 본문의 "테스트 방법"에 적고, 가능하면 GIF를 첨부합니다.

## 릴리스

마일스톤 단위로 `develop` → `main` PR을 열고 **Merge commit** 으로 병합한 뒤 태그를 답니다.

```bash
git switch main
git pull
git tag -a v0.1.0 -m "v0.1.0: MVP"
git push origin v0.1.0
```
