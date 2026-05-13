# SAFE Input → Runtime Mapping Analysis
## 2026-05-13

---

## SAFE 입력 Inventory

| 테이블 | 건수 | 역할 | Runtime 연결 |
|--------|------|------|-------------|
| companies | 27 | 회사 기본정보 | factory → diagnosis_session |
| factories | 30 | 사업장 (업종/규모/주소) | legal_context 진입점 |
| buildings | 1 | 건물 (연면적/용도) | 소방 의무 판단 |
| equipment_assets | 85 | 설비자산 | 안전검사/정기점검 의무 |
| factory_process | 9 | 공정 | 위험성평가 의무 |
| construction_sites | 0 | 공사장 | 건설 의무 |
| worker_registry | 0 | 근로자 | 안전교육 의무 |

## SAFE → Runtime Context 연결 구조

```
factories.업종(ksic_code)
└─ legal_context.py → 업종별 적용법령 결정

factories.규모(worker_count, area_sqm)
└─ diagnosis_integrated_svc.py → 규모별 의무 필터

equipment_assets.equipment_type
└─ 설비별 점검 의무 매칭

factory_process.process_code
└─ 위험공정 → 위험성평가 의무
```

## 핵심 연결 파일

| 파일 | 크기 | 역할 |
|------|------|------|
| services/legal_context.py | 10.9KB | 사업장 입력 → 법령 컨텍스트 빌드 |
| services/legal_evaluator.py | 7.5KB | 컨텍스트 → 의무 평가 |
| services/legal_runtime.py | 14.6KB | Runtime 평가 실행 |
| services/diagnosis_integrated_svc.py | 15.5KB | 통합진단 서비스 |
| routers/diagnosis_integrated.py | 9.8KB | 통합진단 API |

## GAP 식별

- worker_registry: 0건 → 안전교육 의무 판단 불가
- construction_sites: 0건 → 건설 의무 판단 불가
- buildings: 1건 → 소방 의무 최소 데이터
