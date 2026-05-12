# iCloud → Desktop 환경 이전 완료 보고

**작업일**: 2026-04-25  
**작업지시서**: `docs/WORK_ORDER_20260425_icloud_to_desktop_migration.md`  
**소요 시간**: 약 4시간 (Cursor 작업 + 검증 + 트러블슈팅)  
**최종 상태**: ✅ **100% 완료** (휴지통 이동까지)

---

## 최종 결과

| TASK | 내용 | 결과 |
|---|---|---|
| 1 | 위치 파악 + clean 검증 | ✅ |
| 2 | `~/Desktop/tai-engineering/` 준비 | ✅ |
| 3 | 3개 레포 fresh clone + SHA 비교 | ✅ |
| 4 | 의존성 설치 (Python venv + npm 4개소) | ✅ |
| 5 | Cursor 새 폴더 열기 | (본인 직접) |
| 6 | iCloud 폴더 `_archived_` 격리 | ✅ |
| 7 | 셸 alias 5개 추가 | ✅ |
| 8 | 시스템 Python 격리 검증 | ✅ |
| **9** | **누락 .env 2개 발견 + 안전 복사** | ✅ |
| **10** | **zip 백업 (376MB, 무결성 검증)** | ✅ |
| **11** | **iCloud 폴더 휴지통 이동 (12:51 KST)** | ✅ |

---

## 안전망 (3중)

| # | 안전망 | 위치 | 보존 기간 | 상태 |
|---|---|---|---|---|
| 1 | **휴지통** | `~/.Trash/_archived_무제_2026-04-25/` | 30일 (5월 25일) | ✅ |
| 2 | **zip 백업** | `~/Desktop/icloud_backup_20260425.zip` (376MB) | 60일 (6월 25일) | ✅ |
| 3 | **GitHub origin** | 모든 코드 (secrets 제외) | 영구 | ✅ |

---

## 환경 구조 (최종)

```
~/Desktop/tai-engineering/
├── tai-api/                          ✅ Python 3.11.15 venv
│   └── pytest collect: 92개
│
├── tai-admin/
│   ├── tadmin/full-version/
│   │   ├── .env                      (170B, chmod 600, gitignore 보호)
│   │   └── app/                      ← PWA 정적
│   ├── admin/full-version/
│   │   └── .env                      (151B, chmod 600, gitignore 보호)
│   ├── full-version/                 (admin 빌드, 826MB)
│   └── site/full-version/            (superadmin 빌드, 822MB)
│
└── taieng/
    ├── package.json                  (nexas 빌드 진입점)
    └── nexas/ (15MB)
```

---

## 이번 작업에서 발견한 부수 사실

### 1. 누락 .env 2개 (옵션 B 검증의 가치)
- `tai-admin/admin/full-version/.env` (151B)
- `tai-admin/tadmin/full-version/.env` (170B)
- 마스킹 보고로 안전하게 처리: `SUPABASE_ANON_KEY=sb_publishable_****`
- 형식 이상 발견 (tadmin은 JS 객체 리터럴) → 별도 백로그
- **이 2개를 못 잡았으면 영구 손실. 옵션 B (검증 + 백업) 선택이 옳았음.**

### 2. macOS 복사본 23개
- iCloud Drive 동기화 충돌로 생긴 ` 2.md` 패턴
- 모두 git 추적 원본 존재 확인 후 안전 삭제

### 3. xhtml2pdf 잔여 의존성
- `routers/report_forms.py`, `routers/contract_kmong.py`에서 사용 중
- 메모리 #16 정정 + 백로그: `docs/BACKLOG_xhtml2pdf_migration.md`

### 4. tai-admin 디렉토리 구조 정확 매핑
- `tadmin/full-version/`: PWA 정적 + npm 미사용
- `full-version/`: admin/tadmin 템플릿 빌드 (Sneat)
- `site/full-version/`: superadmin 빌드

---

## 셸 alias (`~/.zshrc`)

```bash
alias cd-api='cd ~/Desktop/tai-engineering/tai-api'
alias cd-admin='cd ~/Desktop/tai-engineering/tai-admin'
alias cd-eng='cd ~/Desktop/tai-engineering/taieng'
alias cd-tai='cd ~/Desktop/tai-engineering'
alias api-activate='cd ~/Desktop/tai-engineering/tai-api && source .venv/bin/activate'
```

---

## pytest 실행 (CI와 동일)

```bash
cd-api
source .venv/bin/activate
export INTERNAL_API_SECRET=test
export ANTHROPIC_API_KEY=test
pytest tests/ -v --tb=short \
  --ignore=tests/check_db_integrity.py \
  --ignore=tests/check_mapping_coverage.py \
  --ignore=tests/test_legal_engine.py \
  --ignore=tests/test_legal_engine_52.py \
  --ignore=tests/test_legal_engine_layer.py \
  --ignore=tests/wait_for_deploy.py
```

---

## 후속 일정

| 날짜 | 이벤트 | 상태 |
|---|---|---|
| **2026-04-25 (오늘)** | 환경 이전 완료 | ✅ |
| 2026-04-26~ | 정상 작업 시작 | Keystore 생성 등 |
| 2026-05-25 (D+30) | 휴지통 자동 비움 | 1Password 알람 권장 |
| 2026-06-25 (D+60) | Desktop zip 삭제 | 1Password 알람 권장 |

---

## 영구 원칙 (반복 금지)

1. ❌ iCloud Drive 안에 git 저장소 만들지 말 것
2. ❌ `sudo npm install -g` 사용 금지 (`~/.npm` 권한 손상)
3. ❌ 시스템 Python(3.14)에 직접 pip install 금지
4. ✅ 신규 git 작업은 항상 `~/Desktop/tai-engineering/`
5. ✅ Python 작업은 항상 `.venv` 활성화 후
6. ✅ 백업은 GitHub origin이 처리 (추가 원하면 Time Machine 외장 SSD)
7. ✅ secrets는 1Password + 로컬 파일 (절대 git 커밋 금지)
8. ✅ macOS 복사본 패턴(` 2.md`) = git 외부 동기화 신호 = 즉시 환경 점검

---

## 다음 작업 트랙 (재개 가능)

| 트랙 | 우선순위 | 문서 |
|---|---|---|
| Keystore 생성 | 🔴 P0 | 컨디션 좋을 때 30분 |
| Play Console 본인확인 | 🔴 매일 체크 | 메일 오면 24시간 내 |
| PWA 잔여 P0 (5건) | 🔴 P0 | `docs/WORK_ORDER_20260425_pwa_frontend_finish.md` |
| 백엔드 P0 | 🔴 P0 | `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md` |
| Capacitor Phase 2 | 🟡 P1 | `docs/WORK_ORDER_20260424_capacitor_setup.md` |

---

**작성**: Claude (기획창)  
**실행**: Cursor + 심태왕  
**완료일**: 2026-04-25
