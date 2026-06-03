# SaaS 정기결제 500 에러 — 근본원인 규명 및 조치 (2026-06-03)

> 관련 핸드오프: `taieng/docs/2026-06-03_handoff.md` (P0: SaaS 결제 500 에러)
> 작업 원칙: Freeze → Delta Audit. 추측 배제, 코드·빌드설정·DB스키마 3중 대조로 확정.

---

## 1. 증상

- **위치:** `POST /payments/inicis/billing/prepare` → 500 Internal Server Error
- **프론트 메시지:** `결제 준비 중 오류: Unexpected token 'I', "Internal S"... is not valid JSON`
- CORS는 이미 해결된 상태(에러 메시지가 "Failed to fetch"에서 변경된 것이 그 증거).

### 에러 메시지 해독
`Unexpected token 'I', "Internal S"...` = 응답 본문이 평문 `Internal Server Error`라는 뜻.
FastAPI의 `HTTPException(500, detail=...)`은 항상 JSON(`{"detail":...}`)을 반환하므로 이 파싱 에러가 발생할 수 없음.
**→ 이 500은 의도적으로 raise한 HTTPException이 아니라, try/except로 잡히지 않고 그대로 전파된 미처리 예외다** (Starlette 기본 500 응답 = 평문).

---

## 2. 근본원인 (확정)

### 결론: 런타임 이미지에 `psycopg2`가 설치돼 있지 않음

정기결제 `prepare`는 `db/direct_sql.py`의 `insert_subscription()`을 호출하는데, 이 함수는 첫 줄에서 psycopg2를 import한다.

```python
# db/direct_sql.py
def insert_subscription(data):
    import psycopg2.extras      # ← psycopg2 미설치 시 ModuleNotFoundError
    conn = _connect()           # _connect() 내부에서도 import psycopg2
```

`billing_prepare()`에서 try/except 밖에 있는 유일한 외부 호출이 `insert_subscription(sub_row)`이므로,
psycopg2가 없으면 진입 즉시 `ModuleNotFoundError: No module named 'psycopg2'` → 미처리 전파 → 평문 500.
증상과 정확히 일치한다.

### 3중 대조 증거
1. `requirements.txt` — `psycopg2` / `psycopg2-binary` **부재** (수정 전).
2. `Dockerfile` — `pip install -r requirements.txt`만 수행. 시스템 패키지에 `libpq-dev` 없음, psycopg2 별도 설치 단계 없음.
3. psycopg2는 fastapi·uvicorn·supabase·requests·pandas 등 기존 의존성의 전이 의존성이 아님 (supabase 파이썬 클라이언트는 PostgREST/HTTP + httpx 사용).

### 왜 정기결제만 깨지고 단건결제는 정상인가
- 단건결제(`payments.py`)는 `supabase.table()`(PostgREST/HTTP) 경로 → psycopg2 불필요 → 정상.
- 정기결제 `prepare`만 `db/direct_sql.py`(psycopg2 직접연결) 경로를 사용.
  이 모듈은 "PostgREST가 `subscriptions.inicis_order_id` 컬럼을 스키마 캐시에서 인식 못하는 문제"를 우회하려고 도입됐으나, 정작 psycopg2를 의존성에 추가하지 않았다.

### 오탐 배제 (점검 완료)
- **스키마 대조:** `sub_row`의 모든 컬럼(user_id·product_type·plan_code·plan_name·amount·supply_amount·vat_amount·billing_cycle·status·inicis_order_id·company_id·created_at·updated_at)이 `subscriptions` 테이블에 전부 존재. `inicis_order_id`도 존재(nullable). → "컬럼 없음/스키마 캐시" 문제는 현재 원인이 아님.
- **이니시스 환경변수 4종:** prepare에서 미설정이면 깔끔한 `HTTPException(503)`(JSON)으로 떨어짐 → 평문 500의 원인이 아님(설정 확인됨).
- **CORS:** 핸드오프대로 이미 해결.

---

## 3. 적용한 조치 (완료)

| 항목 | 내용 | 상태 |
|---|---|---|
| `requirements.txt` | `psycopg2-binary>=2.9.9` 추가 (commit `7e2a48c6`) | ✅ main 푸시 완료 |

- `psycopg2-binary`는 libpq를 정적 링크한 wheel이라 `python:3.11-slim` 환경에서 **시스템 패키지(`libpq-dev`) 추가 불필요**. Dockerfile 수정 없음.
- main 푸시 → Railway 자동 배포 트리거됨.

---

## 4. 잔여 작업

### 4-1. Railway 환경변수 검증 — `DATABASE_URL` (운영자 직접 확인 필수)
psycopg2 설치 후 `insert_subscription`이 실제로 실행되면, `_connect()` → `_get_url()`이 `DATABASE_URL`을 요구한다. 미설정 시 `RuntimeError` → **동일하게 평문 500** 재발.

- 핸드오프의 "확인된 환경변수" 목록(INICIS_* 4종)에 `DATABASE_URL`이 **포함돼 있지 않음.**
- Railway tai-api-prod에 아래 형식으로 등록되어 있는지 확인:
  `postgresql://postgres.[ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres`
  (Supabase Dashboard → Settings → Database → Connection string URI)
- 미설정이면 등록 후 재배포.

### 4-2. `payment_billing.py` 견고화 — Cursor 작업 (파일 33KB > 20KB, MCP 직접편집 금지)
DB 예외가 평문 500으로 새어나가지 않도록 `billing_prepare`에서 `insert_subscription` 호출을 방어한다.

```python
# routers/payment_billing.py — billing_prepare() 내부
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

추가로 `plan_name` NOT NULL 방어(2차 잠복요인, 아래 §5):
```python
# plan_name 최종 폴백 — goodname도 비어있을 때 대비
plan_name = body.plan_name or body.goodname or "TAI Safe"
sub_row["plan_name"] = plan_name
```

### 4-3. 배포 검증 절차
1. Railway 자동 배포 완료 대기.
2. `curl https://api.taieng.co.kr/` 헬스/모듈 카운트 확인 (빌드 성공 여부).
3. SaaS 결제 화면에서 `billing/prepare` 호출 → 응답이 JSON(`status:success` 또는 JSON 형식 에러)인지 확인. 더 이상 평문 `Internal Server Error`가 아니어야 함.
4. (psycopg2 OK & DATABASE_URL OK 시) `subscriptions`에 PENDING 행 생성 확인:
   `SELECT id, status, inicis_order_id, created_at FROM subscriptions ORDER BY created_at DESC LIMIT 5;`

---

## 5. 2차 잠복요인 — `subscriptions.plan_name` NOT NULL

- 스키마상 `plan_name`은 `NOT NULL`인데, `sub_row["plan_name"] = body.plan_name`(Optional)이다.
- `model_validator(normalize_plan_name)`가 `goodname`으로 폴백하지만, 프론트가 `plan_name`·`goodname`을 둘 다 비워 보내면 `psycopg2.errors.NotNullViolation` → 또다시 평문 500.
- 현재는 프론트가 `goodname`을 보내므로 회피되나, §4-2의 방어코드로 근본 차단할 것.

---

## 6. 원인 요약 (한 줄)

> `db/direct_sql.py`가 psycopg2를 import하는데 `requirements.txt`/`Dockerfile`에 psycopg2가 누락 → 정기결제 `billing/prepare`가 `insert_subscription` 진입 즉시 `ModuleNotFoundError`로 미처리 평문 500을 반환했고, 프론트가 이를 JSON 파싱하려다 `Unexpected token 'I'`로 실패한 것.
