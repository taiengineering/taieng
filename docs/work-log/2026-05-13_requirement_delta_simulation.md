# Requirement Delta Simulation
## 2026-05-13

## 예시 시나리오

소방시설법 제20조: 5000㎡ → 3000㎡ 변경

1. THRESHOLD_CHANGED 감지
2. 영향 사업장: 3000~5000㎡ 범위 87개
3. 신규 obligation: 412건
4. checklist delta: +1,880
5. severity: CRITICAL

## source_trace 필수
모든 simulation 결과에 "왜 영향이 발생했는가" 설명 가능해야 함.
