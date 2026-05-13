# Engine Monitoring Dashboard
## 2026-05-13

---

## 페이지
`/html/admin/engine-monitoring.html`

## 표시 항목

### Summary Cards (6개)
- 총 이벤트 / 미해결 / CRITICAL / HIGH / WARNING / AI 오염

### 6개 Tab
1. **Drift 탐지** — obligation/completeness/mandatory drift
2. **AI 오염** — AI contamination + unsupported inference
3. **Mandatory Drift** — recommended가 mandatory 동작
4. **Checklist 폭증** — fan-out 이상
5. **미지원 추론** — unsupported domain inference
6. **Explainability** — source_trace 누락

## API 연결

| Endpoint | 표시 Tab |
|----------|----------|
| /engine-monitoring/summary | Summary Cards |
| /engine-monitoring/drift-events | Drift |
| /engine-monitoring/ai-contamination | AI |
| /engine-monitoring/mandatory-drift | Mandatory |
| /engine-monitoring/checklist-explosion | Explosion |
| /engine-monitoring/unsupported-domain | Unsupported |
| /engine-monitoring/explainability-audit | Explainability |

## 색상 코드
- CLEAN: 초록
- WARNING: 노란
- HIGH: 주황
- CRITICAL: 빨강

## 작업자 앱 노출 금지
엔진감시는 관리자/엔진관리자 전용.
