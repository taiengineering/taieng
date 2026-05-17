# Push Runtime Readiness v2

작성일: 2026-05-17
범위: Push 채널 운영 준비도 재평가 (029 Discovery + 030 분석 반영)

---

## 평가

| 항목 | v1 | v2 | 변화 |
|---|---|---|---|
| Infra | 8/10 | 8/10 | — (firebase-admin + fcm_utils 존재) |
| Token Mapping | 6/10 | 7/10 | ↑ actor mapping 분석 완료 |
| Runtime Compatibility | 5/10 | 8/10 | ↑ compat layer 설계 + adapter contract 정의 |
| Actor Convergence | —/10 | 7/10 | 신규 (audience_resolver 연결 방법 확인) |
| Delivery Integration | —/10 | 8/10 | 신규 (audit gap 분석, Runtime으로 전부 해결) |
| Operational Usage | 4/10 | 5/10 | ↑ 7개 호출처 전수 + 우선순위 매트릭스 |
| Migration Plan | —/10 | 9/10 | 신규 (3단계 점진적 수렴) |

---

## Push Runtime Readiness v2

**52/70 = 74% — B 등급**

(v1 51% C → v2 74% B, +23%p)

---

## 남은 작업

1. push.py mock → fcm_utils.send_push() 실연동 (Phase A 즉시)
2. channel_registry PUSH enabled=true
3. audience_resolver에 push_token 조회 추가
4. 6개 호출처 점진적 wire_and_emit 전환 (Phase B)
5. Token refresh/invalidation 로직 (Phase C)
