# Trans Engine Final Architecture

**Version**: v1.0.0 FREEZE  
**Date**: 2026-05-19  
**Status**: Architecture Freeze

---

## 1. Trans Engine이란

Trans Engine은 **Operational Translation Engine**이다.  
Runtime이 생성하는 기계 이벤트를 **인간 운영자가 이해할 수 있는 운영 언어**로 변환한다.

Trans Engine은:
- ❌ Truth Owner가 아님
- ❌ Severity 결정자가 아님
- ❌ Incident Owner가 아님
- ❌ Runtime Controller가 아님

Trans Engine은:
- ✅ **Human Operational Meaning Layer**

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────┐
│              Runtime Foundation               │
│     Event Bus · Control · Validation          │
│         (절대 변경 금지 영역)                   │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│          Intelligence Runtime                │
│     분석 · 패턴 감지 · 위험 판단               │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│            Trans Engine (이 문서)             │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Situation │→│ Snapshot │→│Evolution │  │
│  │Builder   │  │ Store    │  │ Delta    │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│       ↓              ↓              ↓       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Attention │→│Guidance  │→│Learning  │  │
│  │Engine    │  │Builder   │  │Registry  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                      ↓                      │
│              ┌──────────────┐               │
│              │Human Closure │               │
│              │  Workflow    │               │
│              └──────────────┘               │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│         Human Operator (최종 판단)            │
└─────────────────────────────────────────────┘
```

---

## 3. 전체 흐름

```
Event (Runtime)
  → Situation (T-01/T-02: 이벤트 → 운영 상황 변환)
    → Surface (T-03/T-04: 운영자 접근 가능한 화면)
      → Snapshot (T-05: DB 저장, 시간 흐름 추적)
        → Evolution (T-06: 이전 대비 변화 해석)
          → Attention (T-07/T-08: 우선순위화, 집중 대상 선정)
            → Guidance (T-09: 대응 방향 안내)
              → Learning (T-10: 운영 경험 학습)
                → Human Closure (T-11: 운영자 최종 판단)
```

---

## 4. Layer 정의

| Layer | 역할 | 소유자 |
|-------|------|--------|
| Runtime | Event 발생, 상태 관리 | Runtime Foundation |
| Intelligence | 분석, 패턴 감지 | Intelligence Runtime |
| **Situation** | 이벤트 → 운영 상황 변환 | Trans Engine |
| **Snapshot** | 상황 저장, 시간 흐름 | Trans Engine |
| **Evolution** | 상황 변화 해석 (delta) | Trans Engine |
| **Attention** | 운영 우선순위화 | Trans Engine |
| **Guidance** | 대응 방향 안내 | Trans Engine |
| **Learning** | 운영 경험 학습 | Trans Engine |
| **Closure** | 인간 최종 판단 | Trans Engine → 운영자 |

---

## 5. Situation Lifecycle

| 상태 | 운영 표현 | 의미 |
|------|----------|------|
| emerging | 이상 감지 | 이상 징후 감지됨 |
| active | 운영 영향 중 | 실제 운영에 영향 |
| escalating | 위험 증가 중 | 심각도 상승 |
| stabilizing | 안정화 중 | 상황 회복 중 |
| resolved | 해결됨 | 문제 해결 완료 |

```
emerging → active → escalating
                 ↓
              stabilizing → resolved
```

---

## 6. Delta Types

| Delta | 운영 표현 | Badge |
|-------|----------|-------|
| new | 신규 발생 | 🆕 |
| worsening | 상황 악화 | 🔺 |
| stabilizing | 안정화 중 | 🔻 |
| resolved | 해결됨 | ✅ |
| recurring | 재발 | 🔁 |
| unchanged | 변화 없음 | ➖ |

---

## 7. Attention Engine

**6요소 가중치 점수 (0.0~1.0)**:

| 요소 | 비율 |
|------|------|
| priority | 30% |
| worsening/escalating | 20% |
| recurrence | 15% |
| tenant spread | 15% |
| customer impact | 10% |
| event acceleration | 10% |

**Attention Level**: critical(≥0.75) → high(≥0.50) → medium(≥0.25) → low

**Immediate Attention 조건**: P1+worsening, recurring+escalating, accelerating+P1/P2, score≥0.80

---

## 8. Response Guidance

**8종 Playbook**: worsening, recurring, escalating, stabilizing, payment, document, timeout, default

각 playbook 포함:
- recommended_actions (운영 행동)
- recommended_checks (확인 항목)
- recommended_order (확인 순서)

**절대 금지**: 자동 대응, 시스템 변경, kubectl/restart 명령

---

## 9. Operational Learning

- **Feedback**: 운영자 대응 기록 (operator_action + outcome)
- **Effectiveness**: 대응 효과 분석 (improved/unchanged/worsened/recurring)
- **Recurrence Memory**: 재발 패턴 추적
- **Learning Registry**: 효과적 대응 패턴 축적
- **Operational Memory**: 상황별 과거 경험 기억

---

## 10. Human Closure Workflow

**Resolution Types**: resolved(해결) | accepted(위험 허용) | monitoring(관찰) | false_alarm(오탐)

**절대 원칙**: AI 자동 종료 금지. 운영자 최종 승인 필수.

**추적**: operator_activities, requires_followup, recurrence_after_closure

---

## 11. Dashboard 구조

### Situation Dashboard (18 섹션)

| 섹션 | 이름 | Task |
|------|------|------|
| S26 | KPI Row (전체/활성/악화/재발/안정화/P1) | T-07 |
| S27 | Active Situation Board | T-07 |
| S28 | Worsening Radar | T-07 |
| S29 | Recurring Monitor | T-07 |
| S30 | Tenant Risk Distribution | T-07 |
| S31 | Domain Stability | T-07 |
| S32 | Lifecycle Bar | T-07 |
| S33 | Immediate Attention | T-08 |
| S34 | Focus Queue | T-08 |
| S35 | Attention Heatmap | T-08 |
| S36 | Response Guidance | T-09 |
| S37 | Check Order | T-09 |
| S39 | Situation Playbook | T-09 |
| S40 | Operational Memory | T-10 |
| S41 | Effective Response | T-10 |
| S42 | Recurrence Risk | T-10 |
| S44 | Resolution Queue | T-11 |
| S45 | Follow-up | T-11 |
| S47 | Closure History | T-11 |

### Situation Detail (8 섹션)

| 섹션 | 이름 |
|------|------|
| D1 | Situation Header |
| D2 | Lifecycle Timeline |
| D3 | Delta Evolution |
| D4 | Attention Changes |
| D5 | Guidance History |
| D6 | Operator Activities |
| D7 | Learning Memory |
| D8 | Closure History |

### Operational Awareness Center (6 섹션)

| 섹션 | 이름 |
|------|------|
| S20 | Situation Board |
| S21 | Storyline |
| S22 | Recommended Focus |
| S23 | Risk Trend |
| S24 | Human Timeline |
| S25 | Situation History |

---

## 12. Telegram Operational Workflow

```
Attention (critical/high)
  → Telegram 알림 (상황 + guidance 요약 + 상세 링크)
    → Operator 확인
      → 대응 실행
        → Feedback 기록 (POST /learning/feedback)
          → Closure (POST /closure/resolve)
```

---

## 13. DB 구조

| 테이블 | 역할 |
|--------|------|
| operational_situation_snapshot | 상황 스냅샷 (~30 컬럼) |
| operational_response_feedback | 대응 결과 기록 |
| operational_situation_closure | 운영자 종료 판단 |

---

## 14. Scheduler

| Job | 주기 | 역할 |
|-----|------|------|
| SITUATION_SNAPSHOT_GENERATE | 5분 | Snapshot → Delta → Attention → Guidance → Learning → Closure |
| SITUATION_RETENTION_POLICY | 매일 03:00 | 오래된 데이터 정리 보고 |

---

## 15. API Endpoints (40+)

**Trans**: /trans/translate, translate-batch, summary, build-situation, build-storyline, explain-risk, examples  
**Situation**: /situation/recent, timeline, detail, history, evolution, recurring, worsening, stabilizing  
**Dashboard**: /situation/dashboard/overview, worsening, recurring, tenant-risk, domain-stability, lifecycle-map  
**Detail**: /situation/detail-full, lifecycle, guidance-history, activity, learning-detail  
**Attention**: /attention/top, critical, queue, summary  
**Guidance**: /response/top-guidance, situation, checklist, playbook, playbooks  
**Learning**: /learning/feedback, effective-actions, recurring-patterns, situation, memory  
**Closure**: /closure/resolve, history, open, followup, operator

---

## 16. Code Structure

```
watch_engine/trans_engine/
├── __init__.py
├── event_translator.py          # T-01
├── summary_builder.py           # T-01
├── situation_builder.py         # T-02
├── storyline_builder.py         # T-02
├── risk_explainer.py            # T-01
├── situation_snapshot_builder.py # T-05
├── situation_snapshot_store.py   # T-05
├── situation_delta.py           # T-06
├── lifecycle_transition.py      # T-06
├── delta_explainer.py           # T-06
├── situation_evolution.py       # T-06
├── recurrence_detector.py       # T-06
├── attention_score.py           # T-08
├── attention_ranker.py          # T-08
├── focus_queue.py               # T-08
├── attention_explainer.py       # T-08
├── attention_engine.py          # T-08
├── response_playbook.py         # T-09
├── response_priority.py         # T-09
├── response_explainer.py        # T-09
├── guidance_builder.py          # T-09
├── response_guidance.py         # T-09
├── response_feedback.py         # T-10
├── feedback_tracker.py          # T-10
├── effectiveness_analyzer.py    # T-10
├── learning_registry.py         # T-10
├── operational_memory.py        # T-10
├── operational_closure.py       # T-11
├── closure_workflow.py          # T-11
├── operator_activity.py         # T-11
├── resolution_tracker.py        # T-11
├── closure_summary.py           # T-11
├── utils/                       # R-01
│   ├── snapshot_utils.py
│   ├── aggregation_utils.py
│   └── environment_utils.py
├── enrichment/                  # R-01
│   ├── delta_enrichment.py
│   ├── attention_enrichment.py
│   ├── guidance_enrichment.py
│   ├── learning_enrichment.py
│   └── closure_enrichment.py
├── services/                    # R-02
│   ├── situation_query_service.py
│   ├── dashboard_aggregation_service.py
│   ├── attention_service.py
│   ├── guidance_service.py
│   ├── learning_service.py
│   └── closure_service.py
└── retention/                   # R-02
    ├── archive_policy.py
    ├── snapshot_retention.py
    ├── feedback_retention.py
    └── closure_retention.py
```

---

## 17. Operational Philosophy

### 핵심 원칙

TAI Trans Engine의 목표는 **"더 많은 로그"**가 아니다.  
목표는 **"더 나은 운영 판단"**이다.

### Human-Centered 원칙

1. **설명**: 기계 이벤트를 운영 언어로 변환
2. **우선순위화**: 지금 반드시 봐야 하는 것을 끌어올림
3. **기억**: 과거 운영 경험을 축적
4. **학습**: 효과적인 대응 패턴을 학습
5. **추천**: 대응 방향을 안내
6. **최종 판단은 인간**: AI는 대체하지 않고 보조함

### 운영 UX 원칙

- 개발자 화면이 아닌 **운영자 화면**
- 3초 안에 이해 가능해야 함
- 기술 용어 대신 **운영 언어** 사용
- P1→"즉시 확인 필요", workflow.failed→"흐름이 중단되었습니다"

### PROD/SYN 분리 원칙

- 모든 데이터에 environment 필드
- PROD(운영) / SYN(합성) 명확 분리
- 운영 혼동 방지

---

## 18. Runtime Boundary

Trans Engine이 **절대 하지 않는 것**:

- ❌ Truth 생성/수정
- ❌ Severity 결정
- ❌ Incident 생성
- ❌ 시스템 직접 변경
- ❌ 자동 restart/recovery
- ❌ 운영자 우회
- ❌ Runtime Foundation 변경
- ❌ Event Bus 변경
- ❌ Validation 변경
- ❌ Sovereignty 변경

Trans Engine이 **하는 것**:

- ✅ 이벤트 → 상황 변환
- ✅ 상황 저장/추적
- ✅ 변화 해석
- ✅ 우선순위화
- ✅ 대응 가이드
- ✅ 운영 경험 학습
- ✅ 인간 종료 워크플로우

---

## 19. Trans Engine Architecture Freeze v1

**선언일**: 2026-05-19  
**버전**: v1.0.0

이 문서로 Trans Engine의 다음 사항이 **고정**됩니다:

1. **Layer 구조 고정**: Event → Situation → Snapshot → Evolution → Attention → Guidance → Learning → Human Closure
2. **Runtime Boundary 고정**: Trans Engine은 Projection Layer만 — Truth/Severity/Incident 생성 금지
3. **Human-Centered 원칙 고정**: 최종 판단은 인간 운영자 — AI 자동 종료/대응 금지
4. **Dashboard 구조 고정**: S20~S47 + D1~D8
5. **DB 구조 고정**: 3 테이블 (snapshot, feedback, closure)
6. **Scheduler 구조 고정**: 6단계 enrichment pipeline

향후 기능 추가는 이 Architecture Freeze 위에서만 수행됩니다.

---

*이 문서는 향후 모든 엔진 연결(Notification, Marketing, Command, Workflow, Mobile Runtime)의 기준이 됩니다.*
