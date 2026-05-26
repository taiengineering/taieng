# 법령 적용 상태 마크 시스템 설계

> 문서번호: LEGAL-STATUS-001
> 작성일: 2026-05-26
> 상태: 설계 확정

---

## 1. 개요

시설/공정/설비 각각에 법령 적용 상태 마크를 표시하여,
사용자가 "빨간 마크가 있으면 눌러서 해결" 패턴으로 법령 관리를 할 수 있게 한다.

---

## 2. 상태 정의

### 시설 (factories)
| 상태 | 값 | 의미 | UI |
|------|-----|------|----|
| 미적용 | `NOT_APPLIED` | 법령진단 한 번도 안 함 | 🔴 |
| 재진단 필요 | `NEEDS_UPDATE` | 공정/설비/상세 변경 후 미갱신 | 🟡 |
| 적용완료 | `APPLIED` | 법령진단 완료, 변경 없음 | 🟢 |

### 공정 (factory_process)
| 상태 | 값 | 의미 | UI |
|------|-----|------|----|
| 미매핑 | `NOT_MAPPED` | 새로 추가되어 법령 매핑 없음 | 🔴 |
| 매핑완료 | `MAPPED` | 법령 규칙 매핑됨 | 🟢 |

### 설비 (equipment_assets)
| 상태 | 값 | 의미 | UI |
|------|-----|------|----|
| 미매핑 | `NOT_MAPPED` | 새로 등록되어 점검항목 없음 | 🔴 |
| 매핑완료 | `MAPPED` | 점검항목 생성됨 | 🟢 |

---

## 3. 상태 변경 트리거

### 시설 legal_status → NEEDS_UPDATE 자동 전환
- 공정 추가/삭제 (factory_process INSERT/DELETE)
- 설비 추가/삭제 (equipment_assets INSERT/DELETE)
- 시설 상세정보 변경 (전기용량, 연면적, 공사금액 등)

### 시설 legal_status → APPLIED
- 법령엔진 실행 완료 시 (BE에서 자동 갱신)

### 공정 legal_status → MAPPED
- 법령엔진이 해당 공정에 규칙 매핑 완료 시

### 설비 legal_status → MAPPED
- 법령엔진이 해당 설비에 점검항목 생성 완료 시

---

## 4. 비활성화 연동

| 액션 | 연쇄 동작 |
|--------|----------|
| 시설 비활성화 (status_code=INACTIVE) | 해당 시설의 모든 점검일정 중지 (is_active=false) |
| 설비 미사용 (operation_status=INACTIVE) | 해당 설비 관련 점검항목 중지 |
| 공정 삭제 | 해당 공정 연결 점검항목 중지 |
| 재활성화 | 점검일정 자동 재개 (재진단 아님) |

---

## 5. UI 배치

### 대시보드
- 요약 카드: "법령 미적용 시설 N건" → 클릭 시 시설목록 이동

### 시설 목록 (factory-list.html)
- 각 행: 시설명 옆에 법령마크 배지 (🟢🟡🔴)
- 상단: **[전체 법령적용]** 버튼 — 클릭 시 확인 모달
  - "미적용 N건 + 재진단 M건 = 총 K건을 법령진단하시겠습니까?"
  - 프로그레스 바 표시 (3/7 처리 중...)
  - 완료 시 결과 요약 (성공 N건, 실패 M건)
- 미적용/재진단 건이 0이면 버튼 비활성화

### 공정관리 (process-manage.html)
- 각 행: 공정명 옆에 매핑마크 (🟢🔴)

### 설비관리 (my-equipment.html)
- 각 행: 설비명 옆에 매핑마크 (🟢🔴)

### 점검항목관리 (inspection-anchor.html)
- 법령엔진 결과로 자동 생성된 점검항목 목록
- 항목 0건이면: "법령진단을 실행하여 점검항목을 자동 생성하세요" + 버튼

---

## 6. DB 스키마

### factories 테이블 컨럼 추가
```sql
ALTER TABLE factories
  ADD COLUMN IF NOT EXISTS legal_status text NOT NULL DEFAULT 'NOT_APPLIED',
  ADD COLUMN IF NOT EXISTS legal_applied_at timestamptz;

COMMENT ON COLUMN factories.legal_status IS '법령적용상태: NOT_APPLIED | NEEDS_UPDATE | APPLIED';
COMMENT ON COLUMN factories.legal_applied_at IS '마지막 법령진단 일시';
```

### factory_process 테이블 컨럼 추가
```sql
ALTER TABLE factory_process
  ADD COLUMN IF NOT EXISTS legal_status text NOT NULL DEFAULT 'NOT_MAPPED';

COMMENT ON COLUMN factory_process.legal_status IS '법령매핑상태: NOT_MAPPED | MAPPED';
```

### equipment_assets 테이블 컨럼 추가
```sql
ALTER TABLE equipment_assets
  ADD COLUMN IF NOT EXISTS legal_status text NOT NULL DEFAULT 'NOT_MAPPED';

COMMENT ON COLUMN equipment_assets.legal_status IS '법령매핑상태: NOT_MAPPED | MAPPED';
```

---

## 7. 구현 우선순위

| 단계 | 작업 | 분류 |
|------|------|------|
| P0 | DB 마이그레이션 (3개 테이블 컨럼 추가) | DB |
| P0 | 기존 데이터 백필 (legal_status 초기값 설정) | DB |
| P1 | 시설 목록 UI 법령마크 배지 + 전체법령적용 버튼 | FE |
| P1 | 법령엔진 실행 후 legal_status 자동 갱신 (BE) | BE |
| P2 | 공정/설비 변경 시 legal_status 자동 전환 (BE) | BE |
| P2 | 공정관리/설비관리 UI 매핑마크 | FE |
| P3 | 비활성화 연동 (점검일정 중지/재개) | BE |
| P3 | 대시보드 요약 카드 | FE |
