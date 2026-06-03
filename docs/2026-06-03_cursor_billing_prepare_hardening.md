# [Cursor 작업지시] payment_billing.py — billing_prepare 견고화 (2026-06-03)

> 관련 문서: `taieng/docs/2026-06-03_billing500_rootcause.md` §4-2
> 원칙: **임의판단 금지. 확장 금지. 아래 명시된 2개 수정만 수행.**

---

## 0. 작업 범위 (이 경계를 벗어나면 안 됨)

- **수정 대상 파일: `routers/payment_billing.py` 단 1개.**
- **수정 대상 함수: `billing_prepare()` 함수 내부 단 1곳의 블록.**
- **수정 개수: 정확히 2건의 find-and-replace.** 그 외 어떤 줄도 변경 금지.

### 금지 사항 (명시)
- 다른 파일 수정 금지: `db/direct_sql.py`, Pydantic 모델(`BillingPrepareBody` 등), `_charge_subscription_once`, `billing_return`, `billing_charge`, `cancel_subscription`, `services/*`, 그 외 전부.
- import 추가 금지. `HTTPException`과 `log`는 이미 파일 상단에 존재함
  (`from fastapi import APIRouter, HTTPException, Request`, `log = logging.getLogger(__name__)`).
- `insert_subscription`의 시그니처·동작 변경 금지.
- 주변 코드 리포맷/리팩토링/정렬 변경 금지.
- 새 함수, 새 헬퍼, 새 상수, 새 로깅 라인(아래 명시된 것 외) 추가 금지.
- 동작 로직 변경 금지 — 예외를 JSON HTTPException으로 변환하는 것 외에 흐름을 바꾸지 말 것.

---

## 1. 수정 A — plan_name NOT NULL 폴백

`subscriptions.plan_name`은 NOT NULL. 현재 `body.plan_name`(Optional)이 그대로 들어가 NULL 위반 가능.

**찾을 문자열 (정확히 1회 일치):**
```python
        "plan_name":       body.plan_name,
```

**바꿀 문자열:**
```python
        "plan_name":       body.plan_name or body.goodname or "TAI Safe",
```

---

## 2. 수정 B — insert_subscription 예외를 JSON으로 변환

DB 예외(psycopg2 등)가 미처리 평문 500으로 새는 것을 차단. HTTPException은 그대로 재전파.

**찾을 문자열 (정확히 1회 일치):**
```python
    created_sub = insert_subscription(sub_row)
    if not created_sub:
        raise HTTPException(status_code=500, detail="구독 레코드 생성 실패")
```

**바꿀 문자열:**
```python
    try:
        created_sub = insert_subscription(sub_row)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"[BILLING PREPARE] insert_subscription 실패 oid={oid}: {e}")
        raise HTTPException(status_code=500, detail=f"구독 레코드 생성 실패: {e}")
    if not created_sub:
        raise HTTPException(status_code=500, detail="구독 레코드 생성 실패")
```

---

## 3. 적용 방법

- 로컬 편집 후 git push (파일 33KB > 20KB이므로 MCP 직접편집이 아닌 로컬 edit + push 사용).
- 커밋 메시지:
  ```
  fix(payment): billing_prepare insert_subscription 예외 JSON 변환 + plan_name 폴백

  DB 예외가 미처리 평문 500("Internal Server Error")으로 새는 것을 차단.
  plan_name NOT NULL 폴백(goodname → "TAI Safe") 추가. billing_prepare 내부만 수정.
  ```
- main 푸시 → Railway 자동 배포.

## 4. 완료 기준 (검증)

1. `git diff` 결과가 **위 2건의 교체 외 변경이 전혀 없어야** 함 (diff 라인 수: 추가 약 6줄 / 삭제 약 2줄 + 수정 A 1줄).
2. import 구문, 다른 함수, 다른 파일에 변경 없음.
3. 배포 후 `billing/prepare` 실패 시 응답이 JSON(`{"detail": "..."}`)이어야 하며, 더 이상 평문 `Internal Server Error`가 아니어야 함.
