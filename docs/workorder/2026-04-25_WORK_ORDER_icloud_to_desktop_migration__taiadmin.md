# WORK ORDER 2026-04-25 · iCloud Drive → Desktop 환경 이전

- **대상**: Cursor (전 영역창)
- **목적**: git 저장소 3개를 iCloud Drive 밖 `~/Desktop/tai-engineering/`으로 이전
- **소요**: 30~45분
- **선행**: T2 미푸시 정리 완료 (양 레포 clean 상태 ✅)

---

## 배경

현재 작업 폴더가 iCloud Drive 안에 있음:
```
~/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/
```

문제:
- iCloud 자동 동기화로 23개 macOS Finder 복사본 자동 생성됨 (T2에서 삭제했지만 재발 위험)
- `.git/index`, `.git/objects/` 동기화 중 파일 락 발생 가능 → repository corruption 위험
- 빌드 산출물(`node_modules`, `__pycache__`)이 iCloud로 매번 업로드 → 클라우드 용량/속도 낭비
- Cursor 저장 시 race condition

해결: **iCloud 외부 + 로컬 SSD 전용**으로 이전.

```
~/Desktop/tai-engineering/
├── tai-api/
├── tai-admin/
└── taieng/
```

**백업 우려 해소**: GitHub origin이 진실의 원천(source of truth). 로컬 SSD 손상 시 어떤 기기에서든 `git clone`으로 완전 복원 가능. iCloud는 추가 보호가 아닌 추가 위험.

---

## 사전 원칙

### 절대 하지 말 것
- ❌ 기존 iCloud 폴더를 곧장 삭제하지 말 것 (이전 검증 후 격리만)
- ❌ `.git/` 폴더만 복사하지 말 것 (전체 폴더 복사)
- ❌ Cursor가 자동으로 결정하지 말 것 (각 단계 결과 보고 → 승인 → 다음)

### 반드시 할 것
- ✅ 단계별 결과 보고 후 승인 받아 진행
- ✅ `git status`, `git remote -v`, `git log -1`로 검증
- ✅ 모든 명령에서 절대경로 사용 (Cursor가 임의로 경로 줄이지 말 것)

---

## TASK 1. 현재 위치 정확히 파악

### 1-1. 3개 레포 위치 확인

```bash
# tai-api는 이미 알려진 위치
TAI_API="/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/tai-api"

# tai-admin, taieng도 같은 부모 폴더에 있는지 확인
ls -la "/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/"
```

기대 결과: `tai-api/`, `tai-admin/`, `taieng/` 3개 폴더 확인

만약 다른 위치에 있으면:
```bash
# 홈 폴더 전체에서 .git 디렉토리 검색 (10~30초 소요)
find ~ -maxdepth 8 -type d -name ".git" 2>/dev/null | grep -v "node_modules"
```

### 1-2. 각 레포의 작업트리 상태 검증 (clean인지)

```bash
for repo in "tai-api" "tai-admin" "taieng"; do
  REPO_PATH="/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/$repo"
  if [ -d "$REPO_PATH/.git" ]; then
    echo "═══════════════════════════════"
    echo "📁 $repo"
    cd "$REPO_PATH"
    echo "Branch: $(git branch --show-current)"
    echo "Remote: $(git remote -v | head -1)"
    echo "Last commit: $(git log -1 --oneline)"
    echo "Status:"
    git status --short
    echo ""
  fi
done
```

### 1-3. 보고 형식

다음 표로 보고:

```
| 레포 | 위치 | 브랜치 | Last SHA | 작업트리 |
|------|------|--------|----------|----------|
| tai-api | /Users/.../무제/tai-api | dev | e7541e9 | clean |
| tai-admin | /Users/.../무제/tai-admin | main | (sha) | clean |
| taieng | /Users/.../무제/taieng | main | 2c1616f | clean |
```

⚠️ **모든 레포가 clean이 아니면 즉시 중단하고 보고.** 미커밋 변경이 있으면 이전 전에 처리 필요.

---

## TASK 2. 새 위치 준비

### 2-1. Desktop 디렉토리 생성

```bash
mkdir -p ~/Desktop/tai-engineering
ls -la ~/Desktop/tai-engineering
```

비어있는 디렉토리여야 함. 만약 이미 뭔가 있으면 즉시 보고.

### 2-2. 디스크 공간 확인

```bash
# 각 레포 크기 확인 (node_modules 등 포함 전체)
du -sh "/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/tai-api"
du -sh "/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/tai-admin"
du -sh "/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/taieng"

# Desktop 여유 공간
df -h ~/Desktop
```

전체 합계가 Desktop 여유 공간보다 작은지 확인.

---

## TASK 3. 이전 (clone 방식 권장)

### 두 가지 방법 비교

| 방법 | 장점 | 단점 |
|---|---|---|
| **A. fresh git clone** (권장) | 깨끗한 상태, iCloud 메타데이터 완전 제거, node_modules 재설치 | 재설치 시간 필요 |
| B. cp -R 복사 | 빌드 산출물 그대로 유지 | iCloud 잔재(`.icloud` placeholder, `._` 메타파일) 따라옴 |

→ **방법 A 채택**. 더 깨끗하고 안전.

### 3-1. 3개 레포 fresh clone

```bash
cd ~/Desktop/tai-engineering

# tai-api (dev 브랜치 기본)
git clone -b dev git@github.com:taiengineering/tai-api.git
# 또는 HTTPS:
# git clone -b dev https://github.com/taiengineering/tai-api.git

# tai-admin (main)
git clone git@github.com:taiengineering/tai-admin.git

# taieng (main)
git clone git@github.com:taiengineering/taieng.git
```

⚠️ SSH 키가 없으면 HTTPS 사용. SSH 키 설정은 별도 작업.

### 3-2. 검증

```bash
for repo in "tai-api" "tai-admin" "taieng"; do
  echo "═══════════════════════════════"
  echo "📁 $repo (new location)"
  cd ~/Desktop/tai-engineering/$repo
  echo "Branch: $(git branch --show-current)"
  echo "Last commit: $(git log -1 --oneline)"
  echo "Status:"
  git status --short
done
```

기대: 3개 모두 clean, 각 브랜치의 origin 최신 SHA와 일치.

### 3-3. 비교 검증 (이전 전후 동일성 확인)

```bash
# 기존 위치의 마지막 커밋
cd "/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/무제/tai-api"
OLD_API=$(git log -1 --oneline)

# 새 위치
cd ~/Desktop/tai-engineering/tai-api
NEW_API=$(git log -1 --oneline)

echo "OLD: $OLD_API"
echo "NEW: $NEW_API"

# 두 SHA가 일치해야 정상
```

3개 레포 모두 동일하게 비교.

---

## TASK 4. 의존성 설치 (각 레포별)

### 4-1. tai-api (Python)

```bash
cd ~/Desktop/tai-engineering/tai-api

# 가상환경 생성 (기존 venv 이름 확인 후)
ls -la | grep -E "venv|.venv|env"

# 만약 .venv 사용했으면
python3 -m venv .venv
source .venv/bin/activate

# requirements 설치
pip install -r requirements.txt

# 검증: 가벼운 테스트
python -c "import fastapi; print(fastapi.__version__)"
```

### 4-2. tai-admin (정적 사이트)

```bash
cd ~/Desktop/tai-engineering/tai-admin

# package.json 있으면
if [ -f package.json ]; then
  npm install
fi
```

### 4-3. taieng (정적 사이트)

```bash
cd ~/Desktop/tai-engineering/taieng

if [ -f package.json ]; then
  npm install
fi
```

---

## TASK 5. Cursor / VSCode 작업 폴더 갱신

### 5-1. Cursor에서

1. 현재 열려있는 iCloud 폴더 모두 닫기
2. `File → Open Folder` → `~/Desktop/tai-engineering/`로 이동
3. 또는 각 레포별로 별도 워크스페이스 생성:
   - `tai-api.code-workspace`
   - `tai-admin.code-workspace`
   - `taieng.code-workspace`

### 5-2. 최근 폴더 목록 정리

`File → Open Recent`에 iCloud 경로들이 남아있으면 무시. 사용하지 말 것.

---

## TASK 6. 기존 iCloud 폴더 격리 (삭제는 1주일 후)

### 6-1. 즉시 격리 (이름 변경)

```bash
# 기존 폴더를 "_archived_"로 prefix → 실수 방지
cd "/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/"
mv "무제" "_archived_무제_2026-04-25"
```

⚠️ 이렇게 이름만 바꾸면:
- iCloud는 동기화를 멈추지 않지만 (파일 자체는 그대로)
- Cursor/Finder에서 실수로 다시 열 위험 차단
- 1주일 후 작업이 안정되면 완전 삭제

### 6-2. 1주일 후 완전 삭제 (별도 작업)

```bash
# 1주일 후 (5월 2일경) 실행
rm -rf "/Users/taiwangsim/Library/Mobile Documents/com~apple~CloudDocs/1.TAI엔지니어링/admin/tai-admin/GitHub/_archived_무제_2026-04-25"
```

이건 즉시 실행 금지. 일정 기록만 해두기.

---

## TASK 7. 환경 변수 / 경로 설정 갱신

### 7-1. 셸 별칭(alias) 설정

`~/.zshrc`에 다음 추가:

```bash
cat >> ~/.zshrc <<'EOF'

# ── TAI Engineering 작업 단축키 ──
alias cd-api='cd ~/Desktop/tai-engineering/tai-api'
alias cd-admin='cd ~/Desktop/tai-engineering/tai-admin'
alias cd-eng='cd ~/Desktop/tai-engineering/taieng'
alias cd-tai='cd ~/Desktop/tai-engineering'
EOF

source ~/.zshrc
```

### 7-2. Capacitor 작업 경로 갱신

이전 Capacitor 작업지시서에서 `tai-admin/mobile/`로 명시됐던 부분이 이제 `~/Desktop/tai-engineering/tai-admin/mobile/`이 됨.

내부적으로는 변경 없음 (상대 경로 사용).

---

## 체크리스트

### 검증 단계
- [ ] TASK 1-1: 3개 레포 위치 확인
- [ ] TASK 1-2: 모든 레포 clean 상태
- [ ] TASK 1-3: 위치/브랜치/SHA 표 보고
- [ ] TASK 2-1: `~/Desktop/tai-engineering/` 빈 디렉토리 생성
- [ ] TASK 2-2: 디스크 공간 충분

### 이전 단계
- [ ] TASK 3-1: 3개 레포 fresh clone
- [ ] TASK 3-2: 새 위치 검증 (clean + correct branch)
- [ ] TASK 3-3: SHA 비교 검증 (구↔신 동일)

### 의존성
- [ ] TASK 4-1: tai-api Python 환경
- [ ] TASK 4-2: tai-admin npm install
- [ ] TASK 4-3: taieng npm install

### 마무리
- [ ] TASK 5-1: Cursor에서 새 폴더 열기
- [ ] TASK 5-2: 최근 폴더 목록 무시
- [ ] TASK 6-1: 기존 iCloud 폴더 이름 변경 (`_archived_`)
- [ ] TASK 7-1: 셸 alias 설정

### 후속 작업 일정
- [ ] 5월 2일: TASK 6-2 (구 폴더 완전 삭제) — 별도 작업

---

## 위험 대응

| 위험 | 대응 |
|---|---|
| TASK 1에서 미커밋 변경 발견 | 즉시 중단, 변경 내용 보고 후 커밋/스태시 결정 |
| `git clone` 실패 (인증) | HTTPS로 시도, 안 되면 GitHub Personal Access Token 사용 |
| TASK 3-3에서 SHA 불일치 | 구 폴더에 미푸시 작업이 있을 가능성 → 즉시 중단, 분석 |
| `npm install` 실패 | Node 버전 확인 (`node -v` → v20.x 여야 함) |
| Python `pip install` 실패 | 가상환경 활성화 확인, `python3 --version` 확인 |
| Cursor가 새 폴더 못 찾음 | Cursor 완전 종료 후 재실행 |

---

## 사후 관리 (영구적 원칙)

이 이전 후 다음을 영구 원칙으로:

1. **iCloud Drive 안에 git 저장소 절대 만들지 않기**
2. **신규 git 작업은 항상 `~/Desktop/tai-engineering/` 또는 `~/Code/` 아래**
3. **백업이 필요하면**: GitHub origin push로 충분 (이미 자동)
4. **추가 백업 원하면**: Time Machine 외장 SSD (iCloud 아님)
5. **여러 기기 동기화 원하면**: git 자체가 도구. 다른 기기에서도 `git clone`

---

## 진행 순서 요약

```
TASK 1 (검증) → 보고 → 승인
TASK 2 (준비) → 보고 → 승인
TASK 3 (clone) → 보고 → 승인
TASK 4 (의존성) → 보고
TASK 5 (Cursor) → 본인 직접
TASK 6 (격리) → 보고
TASK 7 (alias) → 보고
완료
```

각 TASK 마치면 결과 보고 후 다음 TASK 진행. 한번에 다 하지 말 것.

---

**작성**: Claude (기획창)  
**실행**: Cursor (전 영역창)  
**검증**: 심태왕 (각 TASK 결과 확인)
