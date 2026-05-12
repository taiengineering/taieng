# 의무 추출 방법론 — Iterative SET (v3)

**작성일**: 2026-05-04
**기반**: 대표님 5월 4일 9단계 방법론
**목적**: 752 법령 14,000+ article에서 의무 추출 — 검증된 알고리즘으로 안전하게

## 핵심 원칙

1. **batch 묶음 처리 안 함** — 검증되지 않은 알고리즘으로 대량 처리 = 오류 누적
2. **20 article = 1 SET** — 1건씩 보기 어렵지만 batch는 위험. 20건이 검증 가능한 단위
3. **SET마다 정순+역순 검증** — 통과까지 반복 (cycle 1, 2, 3...)
4. **PROMPT는 cycle마다 진화** — v3.0 → v3.1 → v3.2... 누적 학습
5. **더 이상 발견 안 될 때까지 반복** — 그 후에야 batch 적용

## 9단계 사이클

```
1. 752 법령에서 1건씩 추출 → 20 article 세트 만듦. 마킹.
2. 추출 프로그램 실행 (현재 PROMPT_v3.x)
3. 정순 검증 (article → drafts) + 역순 검증 (drafts → article)
4. 문제 파악 후 PROMPT/프로그램 고도화
5. 20개 데이터 삭제 후 재추출 (cycle=2)
6. 다시 정순+역순 검증
7. 이상 있으면 반복 (cycle=3, 4, ...)
8. 패스되면 다른 법령에서 SET-002 만들고 반복
9. 더 이상 발견 안 될 때까지 → 그 후 전체 batch
```

## SET 선정 기준 (옵션 A — 다양성)

각 SET = 20 법령 / 1 article씩:
- LAW (법률) 4건
- ENFORCEMENT_DECREE (시행령) 4건
- ENFORCEMENT_RULE (시행규칙) 4건
- NOTICE (고시) 4건
- STANDARD (기준) 3건
- OTHER 1건

SET-001은 비즈니스 핵심 5 명시 + 다양성 무작위 15.
SET-002 이후 점진적으로 복잡한 패턴 (단서/별표/조건부) 포함.

## 마킹 시스템 (별도 컬럼 X, ai_flags 활용)

```json
ai_flags: {
  "extraction_set": "SET-001",
  "extraction_cycle": 1,
  "prompt_version": "v3.0",
  "extracted_at": "2026-05-04T13:30:00Z",
  "validation_pass": true,
  "validation_issues": [],
  "from_pipeline": "v3_iterative"
}
```

## 자동 검증 기준 (정순 + 역순)

**정순 (article → drafts)**:
1. drafts.appointment_target NOT NULL
2. drafts.obligation_type 8종 중 하나
3. drafts.obligation_summary 30~150자
4. condition 키워드 있는데 condition_code 채움 여부
5. 한 article당 추출 drafts 수 (over/under-extraction)

**역순 (drafts → article)**:
6. obligation_summary 핵심 명사구가 article_text에 실제 존재 (환각 방지)
7. condition_value 숫자가 article_text에 있음
8. drafts.law_name = article의 law_name
9. 동일 article에서 추출된 drafts들 서로 중복 아님
10. drafts.article_id가 살아있는 article 가리킴

10개 다 통과하면 status='APPROVED', 1+ fail이면 'REJECTED' + 이유 ai_flags에 기록.

## 진화 과정 (예시)

```
SET-001 cycle 1 (v3.0): 12/20 통과. 패턴 8건 발견 (단서/위임/별표 등) → v3.1
SET-001 cycle 2 (v3.1): 18/20 통과. 패턴 2건 발견 → v3.2
SET-001 cycle 3 (v3.2): 20/20 통과 ✅ PASS

SET-002 cycle 1 (v3.2): 17/20 통과. 새 패턴 3건 (소급/특례) → v3.3
SET-002 cycle 2 (v3.3): 20/20 통과 ✅ PASS

SET-003 cycle 1 (v3.3): 19/20 통과. 1건만 새 패턴 → v3.4
SET-003 cycle 2 (v3.4): 20/20 통과 ✅ PASS

SET-004 cycle 1 (v3.4): 20/20 통과 ✅ 첫 시도 통과
SET-005 cycle 1 (v3.4): 20/20 통과 ✅ 첫 시도 통과
... 5 SET 연속 첫 시도 통과 = 알고리즘 안정 → batch 모드 전환
```

## 산출물

- `PROMPT_v3_x.md` — cycle마다 진화
- `ERROR_PATTERNS.md` — 발견된 오류 패턴 카탈로그 (누적)
- `SET_LOG.md` — 각 SET 결과 기록
- `extract_iterative.py` — 추출 프로그램 (Cursor 작성)
- `audit_set.sql` — 정순/역순 검증 SQL
- DB drafts (ai_flags에 메타)

## 4월 적재 2,583건 처리

그대로 두고 SET-XXX는 신규 INSERT. 5 SET 검증 후 4월 데이터와 비교 → 폐기/보존 결정.
