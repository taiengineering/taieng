# Mock Operational Dataset Spec
## 2026-05-13

## 생성 규칙

### 회사 (100개)
- company_code: MOCK-C-0001 ~ MOCK-C-0100
- 10종 업종 로테이션
- 규모: 5~800명

### 사업장 (300개)
- factories_code: MOCK-F-00001 ~ MOCK-F-00300
- 회사당 3개
- sector: INDUSTRIAL/BUILDING/CONSTRUCTION

### 설비 (1,200개)
- asset_code: MOCK-EQ-000001 ~ MOCK-EQ-001200
- 사업장당 4개
- 8종 설비 타입

### 점검항목 (5,184개)
- 324 점검세트 × 16항목
- 필수 10 + 선택 6
- source: CANDIDATE_ACTIVATION

### 운영 데이터
- work_orders: 20K (8종 상태 로테이션)
- evidence: 50K (5종 타입, 6종 상태)
- notifications: 30K (7종 이벤트)
- reviews: 5K (5종 액션)
- escalations: 933

## 식별자

source_trace = 'MOCK_POPULATION' 또는 code LIKE 'MOCK-%'
