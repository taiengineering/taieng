# SAFE Runtime Recovery Analysis
## 2026-05-13

---

## 분석 결과

### 기존 SAFE SaaS 상태

| 영역 | 상태 | 비고 |
|------|------|------|
| 사업장 구조 | ✅ 27회사, 30사업장 | 실 데이터 존재 |
| 설비/공정 | ✅ 85설비, 9공정 | 실 데이터 |
| 표준코드 | ✅ 업종/설비/공정 체계 | 활성 |
| 점검 UX | ✅ 기존 구조 존재 | inspection_sets 324 |
| 작업자 앱 | ✅ 기존 구조 존재 | worker-home, my-inspection |
| 문서 생성 | ✅ form_templates 11 | report_forms 구조 |
| checklist 구조 | ✅ 802 후보 | candidate 단계 |
| 매핑 자산 | ✅ 68K+ candidates | 대규모 |

### 문제 진단

**문제는 "법령엔진 오염"이었음.**

Runtime을 "운영 orchestration 시스템"으로 확장하면서:
- 과도한 governance 테이블 34개 생성
- 과도한 lifecycle 강제
- 작업자 앱의 간결한 UX 훼손 위험

### 복구 방향

1. Runtime = deterministic evaluator로 제한
2. SAFE SaaS 기존 운영 구조 유지
3. Mapping Graph 연결 복구 (inspection_set_items GAP 해결)
4. Document Completeness Engine 연결
5. Worker App 3~5초 UX 보호

## 운영 데이터 현황 (Runtime Stress 테스트 데이터)

| 항목 | 건수 | 용도 |
|------|------|------|
| runtime_facility_profile | 50 | 시뮬레이션 |
| runtime_operational_work_order | 129 | 시뮬레이션 |
| runtime_inspection_session | 100 | 시뮬레이션 |
| runtime_compliance_evidence | 300 | 시뮬레이션 |
| runtime_notification_event | 500 | 시뮬레이션 |
| runtime_review_decision | 100 | 시뮬레이션 |
| runtime_submission | 50 | 시뮬레이션 |

**이 데이터들은 시뮬레이션 데이터이며, 실 운영 데이터가 아님.**
