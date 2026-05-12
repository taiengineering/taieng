# TAI Safe 세션 메모리 — 2026-04-08

## 완료 작업 목록

### 1. 메뉴 구조 전면 개편 (`menu-tadmin.js` v4.0.1)

#### 시설관리 서브메뉴 순서 확정
- 시설관리 → 공정관리 → 설비관리 → **점검항목관리** → 점검관리 → 점검캘린더
- 공정관리: `process-manage.html`
- 점검항목관리: `inspection-anchor.html` (법령 기반 통합 페이지)
- 법정점검 기준일 설정, 점검항목 수동입력 메뉴 삭제

#### 건설관리 그룹 재편 + 위치 이동
- 위치: 시설관리 바로 뒤로 이동 (v4.0.1)
- 하위 메뉴: **현장관리 / 공정관리 / 작업관리 / 점검항목관리 / 점검관리**

#### 섹터별 분기 기능 구현 (주석 처리로 전체 표시 유지)
- PLAN_MAP에 `CONSTRUCTION_BASIC/STD/PRO` 추가 (sector: 'CONSTRUCTION')
- 건물/산업 → 시설관리 표시 (추후 활성화)
- 건설 → 건설관리 표시 (추후 활성화)

---

### 2. 점검항목관리 페이지 전면 개선 (`inspection-anchor.html`)

#### 탭: obligation_type 기준 (8종)
| 탭 | obligation_type |
|----|----------------|
| 점검 | INSPECT |
| 작업 전 점검 | BEFORE_WORK |
| 보고 | REPORT |
| 서류·보관 | DOCUMENT |
| 신고 | NOTIFY |
| 선임 | APPOINT |
| 조치 | ACTION |
| 기타 | OTHER |

#### 컬럼 구성
- 법령명/대상 (law_name + inspection_set_name)
- 조문·항목명 → 클릭 시 법령 원문 모달
- 무엇을 (obligation_summary) — 신규
- 의무구분 배지
- 주기
- 기준일 (인라인 date input, 특정일 행 노란색)
- 직전 점검일
- 담당자 → 인라인 드롭다운 (기존 모달 방식 제거)
- 사용여부 토글
- 상태 배지

#### 삭제
- 다음 점검 예정일 컬럼 제거

#### 법령 원문 모달 내용
- 무엇을 (obligation_summary)
- 언제 (cycle_base_guide + 주기텍스트)
- 위반 시 벌칙 (penalty_summary)
- 관련 서식 (form_name)
- 온라인 시스템 (online_system, system_url)
- 비고 (remarks)

---

### 3. 백엔드 `inspection_sets.py` v1.8.0 (tai-api)

- GET /inspection-sets 배치 조인 확장:
  - `obligation_type` (기존)
  - `obligation_summary` ← 신규
  - `penalty_summary` ← 신규
  - `form_name`, `form_url` ← 신규
  - `remarks` ← 신규
  - `online_system`, `system_url` ← 신규
  - `cycle_base_guide_rule` ← 신규
- PATCH /{id}: `is_active`, `schedule_anchor_date`, `last_inspection_date`, `assignee_user_id` 수정
- size 상한 le=200

---

### 4. DB 마이그레이션

```sql
ALTER TABLE inspection_sets
  ADD COLUMN IF NOT EXISTS assignee_user_id UUID REFERENCES users(id) ON DELETE SET NULL;
```

---

### 5. 도메인 하드코딩 수정 (`tadmin.taieng.co.kr` → `safe.taieng.co.kr`)

| 파일 | 수정 위치 |
|------|----------|
| `tadmin/full-version/assets/js/tai/auth-guard.js` | 비로그인 리다이렉트 URL |
| `tadmin/full-version/assets/js/utils.js` | logout() 리다이렉트 URL |
| `admin/full-version/assets/js/tai/auth-guard.js` | 권한 없음 리다이렉트 URL |

- `tai-api/main.py` CORS: `safe.taieng.co.kr` 이미 포함, 정상
- `_headers`: 파일 경로 규칙 기반, 수정 불필요

---

### 6. 한국제조 인천공장 목업 데이터 등록 (DB)

- factory_id: `bbbbbbbb-0001-0001-0001-000000000001`

#### 설비 10개 (5개 공정 × 2개씩)
| 공정 | 설비 |
|------|------|
| 원료처리 > 장입 | 원료 장입호퍼, 원료 이송 컨베이어 |
| 용해 > 용해·정련 | 전기 용해로 1호, 정련로 |
| 주조 > 주입 | 연속주조기, 래들 |
| 가공 > 압연·인발 | 압연기 2호, 인발기 |
| 열처리 > 열처리 | 소둔로(어닐링), 담금질 냉각조 |

#### inspection_sets 8개 (obligation_type 8종)
| obligation_type | 세트명 |
|-----------------|--------|
| INSPECT | 압연·인발 설비 정기 안전검사 |
| BEFORE_WORK | 용해·주조 작업 전 안전점검 |
| REPORT | VOC 배출시설 설치신고 및 보고 |
| DOCUMENT | 안전보건 관련 서류 3년 보존 |
| NOTIFY | 안전관리자 선임 신고 |
| APPOINT | 유해화학물질 관리자 선임 |
| ACTION | 대기오염 방지시설 개선조치 |
| OTHER | 화학물질 취급시설 기타 안전관리 |

---

## 커밋 목록 (tai-admin)

| 커밋 SHA | 내용 |
|---------|------|
| bfa2e88 | menu: 시설관리 서브메뉴 개편 v3.0.0 |
| 70a2f5f | inspection-anchor.html 통합 페이지 초안 |
| 4cf23ae | 탭 obligation_type 기준, size=100, PATCH URL 수정 |
| d4c47a9 | 법령원문 모달, 무엇을 열, 담당자 인라인셀렉트, 다음점검예정일 제거 |
| 056eb46 | menu: 건설관리 메뉴 재편, 섹터분기 구현+주석처리 v4.0.0 |
| 899288 | menu: 건설관리 위치 시설관리 바로 뒤로 이동 v4.0.1 |
| 95443fe | fix: auth-guard.js tadmin→safe |
| 3e939a2 | fix: utils.js logout 리다이렉트 tadmin→safe |
| e7d3422 | fix: admin auth-guard 리다이렉트 tadmin→safe |

## 커밋 목록 (tai-api)

| 커밋 SHA | 내용 |
|---------|------|
| b15bcb6 | inspection_sets v1.7.0: PATCH /{id}, size 200 |
| 147fb37 | inspection_sets v1.8.0: obligation_summary 등 응답 추가 |

---

## PENDING (다음 세션)

- taieng.co.kr/tai-safe 요금 안내 페이지 "원"/"월" 텍스트 삭제
  - 해당 파일 미확인 (tai-safe.html에는 해당 가격 카드 없음)
  - 파일 위치: 별도 확인 필요
- inspection-anchor.html 탭 카운트 배지
- process-manage.html 구현 (현재 빈 파일)
- 섹터 분기 visible 조건 활성화 (주석 해제)
