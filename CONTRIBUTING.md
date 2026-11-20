# 🤝 Contributing

## 🚨 꼭 지켜야 할 규칙

- **모든 작업은 PR로 `main`에 병합합니다.** `main`에는 직접 push하지 않습니다.
- **팀원 모두 자기 계정으로 커밋하고 PR을 올립니다.**
  팀장이 대신 push하지 않고, 각자 PR을 올리면 팀장이 리뷰·승인해서 병합합니다.
- **커밋과 병합 기록이 남아야 합니다.** 그래서 PR은 **Create a merge commit** 으로만 병합합니다.
- **참고한 자료는 반드시 README의 `📚 참고 자료` 에 추가합니다.** (문서, 블로그, 영상, 코드)

---

## 🌳 Branch Strategy

`main` 하나만 두고, 이슈마다 작업 브랜치를 만들어 `main` 으로 PR합니다. (GitHub Flow)

```
main ─────●──────────────●──────────────●──── (직접 push 금지)
           \            /  \            /
            feat/#3-...●    fix/#7-...●
```

| 브랜치 | 설명 |
|---|---|
| `main` | 항상 실행 가능한 상태. PR + 승인 1명 + CI 통과 후에만 병합 |
| `{type}/#{이슈번호}-{브랜치명}` | 작업 브랜치. **이슈를 만들면 자동으로 생성됩니다** |

브랜치 예시

```
feat/#3-손-랜드마크-추적-구현
fix/#12-획-떨림-수정
docs/#15-README-데모-GIF-추가
```

### 브랜치 타입

| 타입 | 설명 | 이슈 제목 / 라벨 |
|---|---|---|
| `feat` | 새로운 기능 | `[Feature]` ✨ Feature |
| `fix` | 버그 수정 | `[BugFix]` 🐛 BugFix |
| `hotfix` | 급한 버그 수정 | `[BugFix]` 🐛 BugFix |
| `refactor` | 동작 변화 없는 코드 개선 | `[Refactor]` ♻️ Refactor |
| `test` | 테스트 추가·수정 | `[Test]` ✅ Test |
| `docs` | 문서 수정 | `[Docs]` 📋 Docs |
| `style` | 포맷, 오타 등 동작에 영향 없는 수정 | `[Style]` 🎨 Style |
| `chore` | 설정, 패키지 등 기타 작업 | `[Chore]` 🛠️ Chore |
| `ci` | GitHub Actions 등 CI 수정 | `[CI]` ⚙️ CI |

---

## 🔁 Workflow

### 1. 이슈 생성 → 브랜치 자동 생성

[Issues → New issue → 이슈 생성](../../issues/new/choose) 에서 폼을 채웁니다.

- 🌳 브랜치명: `손 랜드마크 추적 구현` (띄어쓰기는 `-` 로 바뀜)
- 📂 브랜치 타입: `feat`

이슈를 만들면 GitHub Actions가 자동으로

- 이슈 제목을 `[Feature] #3 손 추적` 형식으로 바꾸고 라벨과 담당자를 붙이고
- `main` 에서 `feat/#3-손-랜드마크-추적-구현` 브랜치를 만들고
- 이슈 댓글로 브랜치 이름을 알려줍니다.

### 2. 브랜치로 이동

```bash
git switch main
git pull
git fetch origin
git switch feat/#3-손-랜드마크-추적-구현
```

### 3. 작업하고 커밋

작은 단위로 자주 커밋합니다. 커밋 규칙은 아래 [💬 Commit Convention](#-commit-convention) 참고.

```bash
git add .
git commit -m "[FEAT] #3 MediaPipe HandLandmarker로 손 랜드마크 검출"
```

### 4. push 전에 최신 main 반영

```bash
git pull origin main      # 충돌이 나면 내 브랜치에서 해결
git push
```

### 5. PR 생성

- base: `main` ← compare: 내 작업 브랜치
- 제목: `[FEAT] #3 손 랜드마크 추적 구현`
- 본문: PR 템플릿을 채우고 `- Closed #3` 에 이슈 번호 기입 (병합 시 이슈 자동 종료)

### 6. 리뷰 → 병합

- 승인 1명 이상 + CI(`lint`, `test`) 통과
- **Create a merge commit** 으로 병합 (병합된 브랜치는 자동 삭제)

---

## 💬 Commit Convention

```
[TYPE] #이슈번호 작업 내용
```

| 타입 | 설명 |
|---|---|
| `[FEAT]` | 새로운 기능 추가 |
| `[FIX]` | 버그 수정 |
| `[HOTFIX]` | 급한 버그 수정 |
| `[REFACTOR]` | 코드 리팩토링 |
| `[TEST]` | 테스트 코드 추가·수정 |
| `[DOCS]` | 문서 수정 |
| `[STYLE]` | 코드 포맷, 오타 등 동작에 영향 없는 수정 |
| `[CHORE]` | 빌드, 패키지, 설정 등 기타 작업 |
| `[CI]` | GitHub Actions 등 CI 수정 |

```
[FEAT] #3 MediaPipe HandLandmarker로 손 랜드마크 검출
[FIX] #12 펜을 들 때 마지막 점이 이어지는 문제 수정
[TEST] #11 제스처 debounce 상태 전환 테스트 추가
[DOCS] #15 README 데모 GIF 추가
```

---

## 🛠 Setup

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

---

## 📏 Code Rules

- 포맷과 린트는 **ruff** 로 통일합니다. `pre-commit install` 을 하면 커밋할 때 자동 검사합니다.
  ```bash
  ruff check . --fix
  ruff format .
  ```
- 임계값 같은 숫자는 코드에 직접 쓰지 말고 `config.py` 에 추가합니다.
- 모듈끼리는 `core/interfaces.py` 의 Protocol과 `core/types.py` 의 타입으로만 주고받습니다.
  다른 팀원 모듈의 내부 함수를 직접 import하지 않습니다.
- **`core/` 를 바꾸는 PR은 모든 팀원에게 리뷰를 요청합니다.** (모두가 의존하는 계약)
- 모델 가중치, 녹화 영상 같은 큰 파일은 커밋하지 않습니다. (`.gitignore` 참고)
- 새 패키지를 추가하면 `pyproject.toml` 과 README의 `🛠 Tech Stack` 을 함께 고칩니다.

## 🧪 Test

- 새 기능에는 단위 테스트를 함께 추가합니다.
- CI에는 웹캠과 GPU가 없습니다. 카메라나 모델이 필요한 부분은 `tests/fakes.py` 의 가짜 객체나
  `tests/fixtures/` 에 저장한 랜드마크 데이터로 테스트합니다.
- 실제 웹캠이 필요한 확인은 PR 본문의 `🧪 테스트 방법` 에 적고, 가능하면 GIF를 첨부합니다.

## 🏷 Release

마일스톤을 마치면 `main` 에 태그를 답니다.

```bash
git switch main
git pull
git tag -a v0.1.0 -m "v0.1.0: MVP"
git push origin v0.1.0
```
