# Runtime Boundary Redefinition
## 2026-05-13

---

## 핵심 원칙

Runtime는 **운영 Owner가 아니다.**
Runtime은 **deterministic evaluator**이다.

역할: `입력값 → applicable obligation 반환`

## Deterministic 유지 영역 (절대 임의판단 금지)

| 영역 | 예시 |
|------|------|
| obligation 결정 | 적용 법령/의무/대상 여부 |
| requirement completeness | 필수 데이터 충족 여부 |
| mandatory checklist | 필수 점검항목/증빙 |
| filing requirement | 제출 의무/가능 여부 |

## AI/임의판단 허용 영역 (Suggestion Layer만)

| 영역 | 예시 | 제한 |
|------|------|------|
| 검색 보조 | 유사 검색어 | 법적 권한 금지 |
| 사용자 편의 | 담당자 추천 | 필수 여부 결정 금지 |
| 문서 초안 | 점검결과 요약 | Deterministic 침범 금지 |
| checklist 추천 | 자주 쓰는 항목 | 필수 여부 결정 금지 |

## Runtime 테이블 역할 재정의

### 유지 (값어치 높음)
| 테이블 | 역할 |
|--------|------|
| runtime_facility_profile (50건) | 사업장 프로필 |
| runtime_facility_equipment (150건) | 설비 맨스터 |
| runtime_facility_hazard (100건) | 위험물 맨스터 |
| runtime_checklist_item (802건) | 점검항목 |
| runtime_filing_registry (11건) | 법정제출 등록 |

### 축소/재검토 대상
| 테이블 | 이유 |
|--------|------|
| runtime_obligation_registry | orchestration 역할 과다 |
| runtime_operational_work_order | 운영 강제 |
| runtime_notification_event | 과도한 governance |
| runtime_review_decision | 과도한 governance |
| runtime_escalation_queue | 과도한 governance |

**주의:** 이 테이블들은 삭제하는 것이 아니라, SAFE SaaS의 기존 운영 흐름(inspection, schedule, document)을 우선하고, Runtime은 deterministic 평가만 수행하는 구조로 전환.

## 핸드오프 원칙

```
SAFE SaaS: 자유 운영 (CRUD, UX, 작업자 앱)
Runtime: deterministic 평가만 (input → obligation)
Document Engine: requirement completeness 판단
Worker App: 3~5초 내 점검 완료 (확인 → 체크 → 완료)
```
