# TAI 프론트 — Cursor 세션 작업 요약 (2026-04-01)

본 문서는 2026-04-01 Cursor 세션에서 수행한 프론트엔드·저장소 작업을 한 파일로 정리한 것이다.

---

## 1. 알럿 관리 (tadmin)

| 항목 | 내용 |
|------|------|
| **페이지** | `tadmin/full-version/html/horizontal-menu-template/alert-list.html` |
| **기능** | `system_alert_messages` 연동 — 목록·필터·요약 카드·인라인 `message_ko` 수정·활성 토글·등록/수정 모달 |
| **API** | `GET/POST/PATCH /alert-messages`, `PATCH .../toggle` 등 |
| **메뉴** | `tadmin/full-version/assets/js/tai/menu-tadmin.js` — **시스템관리** 그룹 하위 **알럿관리** (`alert-list.html`, `badge: NEW`), `isAdmin()`(role `001`)로 표시 제어 |

원격 `main` 병합 후에도 동일 메뉴 블록이 유지되도록 로컬에서 한 번 더 반영됨.

---

## 2. 시설 목록 — 건설 전용 필드 (F-CON-001)

| 항목 | 내용 |
|------|------|
| **지시서** | F-CON-001 |
| **파일** | `factory-list.html` (동일 변경 3경로) |
| **경로** | `tadmin/`, `admin/`, `site/` 각 `full-version/html/horizontal-menu-template/` |

**UI (시설 상세옵션 탭)**

- 공사금액 입력 `id="construction_amount"` (기존 `fp-construction` 대체).
- 공사금액 &gt; 0일 때만 표시: `#construction_extra_fields`
  - 건설공사 유형 `construction_type` (건축/토목/공통/기타)
  - 하도급 근로자수 `subcontractor_worker_count`
  - 합산 표시 `#total_worker_display` = 상시 근무인원(`worker_count`) + 하도급
- 기본정보 탭 상시 근무인원 `id="worker_count"` (기존 `fp-workers` 대체).

**저장**

- `collectFactoryBody()`에 `construction_cost`, `construction_type`, `subcontractor_worker_count` 포함 (`POST /factories`, `PATCH /factories/{id}`).

---

## 3. Git 저장소 동기화

| 항목 | 내용 |
|------|------|
| **저장소** | `taiengineering/tai-admin` (`main`) |
| **작업** | 로컬이 `origin/main` 대비 뒤처진 상태에서 `merge`로 통합, 충돌 해결 후 `push` |
| **충돌 파일** | `site/full-version/html/_redirects`, `site/full-version/html/home/index.html`, `tadmin/.../menu-tadmin.js` (원격 기준 반영 + 알럿 메뉴·`isAdmin` 보강) |

---

## 4. 검증 체크리스트 (참고)

- [ ] tadmin 로그인 role `001` → 시스템관리 → 알럿관리 진입
- [ ] 시설 목록 → 상세옵션 → 공사금액 입력 시 건설 블록 표시·합산·저장

---

## 5. 백엔드 의존

- 알럿: `/alert-messages` 라우트 및 스키마
- 시설: `factories`에 `construction_type`, `subcontractor_worker_count` (및 기존 `construction_cost` 등) 저장 가능 여부

---

*문서 생성: Cursor 에이전트 세션 — 사용자 요청에 따라 작업 이력 파일화 후 Git 반영용.*
