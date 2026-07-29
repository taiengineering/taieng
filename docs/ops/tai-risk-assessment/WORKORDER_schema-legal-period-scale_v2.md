---

class: plans
type: WORKORDER
scope: ops
project: tai-risk-assessment
title: 위험성평가 운영 파라미터 스키마 — ra_policy_param·ra_scale (v1 대체)
version: 2
status: PENDING
owner: taiwang
---

# WORKORDER v2 — 위험성평가 운영 파라미터 스키마

- **골**: `G-ms5zwv4v-b88c4a`
- **v1 대체 사유**: v1의 `ra_legal_period.law_text` 컬럼이 **법령 조문 원문을 복제 저장**하는 설계였다. 법령 데이터는 **API 이외 경로로 저장·수정이 금지**되므로 해당 설계를 폐기한다.

---

## 1. 바로잡은 원칙 — 법령 데이터 취급

| 구분 | 소유 | 이 모듈에서의 취급 |
|---|---|---|
| **법령 원문**(조문 텍스트·개정이력·시행일) | 법령엔진(leg-db) | **저장 금지.** 필요 시 **API로 조회만** 한다. 복제·캐시·발췌 저장 모두 금지 |
| **위험성평가 운영 파라미터**(주기 값 등) | 위험성평가 모듈 | 모듈 전용 테이블에 보관. **위험성평가에서만 사용** |
| **참조 포인터**(어느 조문에서 왔는지) | 위험성평가 모듈 | 조문을 **가리키는 키만** 보유. 텍스트는 갖지 않는다 |

**핵심 구분** — "1개월"이라는 **값**은 이 모듈이 판정에 쓰는 운영 파라미터이고, *"사업이 성립된 날로부터 1개월이 되는 날까지…"*라는 **문장**은 법령 데이터다. 전자는 보관하고 **후자는 보관하지 않는다.**

### v1 → v2 변경점
1. **`law_text` 컬럼 삭제** — 조문 원문 발췌 저장 금지
2. **테이블명 변경** `ra_legal_period` → **`ra_policy_param`** — 법령 저장소로 오인될 이름을 제거. 이 테이블은 *위험성평가 모듈의 운영 파라미터*다
3. **`law_ref` 텍스트 → `law_article_ref` jsonb 포인터** — `{law_key, article_no, clause}` 형태로 leg-db 조문을 가리키기만 함
4. 원문이 필요한 화면·검증은 **런타임에 법령 API 조회**로 처리(§4)

---

## 2. 테이블

### 2-1. `ra_policy_param` — 위험성평가 운영 파라미터
```
id, param_code, label
value_num, value_unit          -- 판정에 쓰는 값 (예: 1 / MONTH)
applies_to                     -- 적용 대상 구분(예: CONSTRUCTION)
law_article_ref  jsonb         -- 조문 포인터만. 예: {"law_key":"...","article_no":15,"clause":"1"}
note                           -- 운영 메모(조문 원문 금지)
effective_from, effective_to   -- 개정 시 종전 행을 닫고 신규 행 추가
is_active, created_at, updated_at
```
**용도 한정** — 이 테이블은 위험성평가 모듈 외에서 참조하지 않는다. 다른 도메인이 같은 값을 필요로 하면 법령엔진 API에서 각자 취득한다(값 복제 확산 방지).

### 2-2. `ra_scale` — 척도·판단기준·허용수준
v1과 동일. **법령 데이터가 아니다** — 고시 §9②가 사업주에게 위임한 사업장 자율 설정이며, 프리셋의 판단기준 문구는 KOSHA 안내서 **예시**이지 조문이 아니다.

---

## 3. 적용할 SQL

```sql
-- =====================================================================
-- 위험성평가 운영 파라미터 및 척도 설정
-- Goal : G-ms5zwv4v-b88c4a
--
-- 법령 데이터 취급 원칙:
--   법령 조문 원문은 법령엔진(leg-db)이 API 로만 관리한다.
--   이 스키마는 조문 텍스트를 저장하지 않으며, 조문을 가리키는 포인터만 보유한다.
--   value_num/value_unit 은 위험성평가 판정에 사용하는 운영 파라미터다.
-- =====================================================================

-- ── 1. 위험성평가 운영 파라미터 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS ra_policy_param (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  param_code       text        NOT NULL,
  label            text        NOT NULL,
  value_num        numeric,
  value_unit       text,
  applies_to       text,
  law_article_ref  jsonb,      -- 조문 포인터만 {law_key, article_no, clause}. 원문 저장 금지.
  note             text,
  effective_from   date        NOT NULL,
  effective_to     date,
  is_active        boolean     NOT NULL DEFAULT true,
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ra_policy_param IS
  '위험성평가 모듈 전용 운영 파라미터. 법령 원문은 저장하지 않는다(법령 데이터는 법령엔진 API 소관). 이 테이블은 위험성평가 판정에만 사용한다.';
COMMENT ON COLUMN ra_policy_param.law_article_ref IS
  '근거 조문을 가리키는 포인터만 보유. 조문 텍스트 저장 금지. 원문이 필요하면 런타임에 법령 API 로 조회한다.';
COMMENT ON COLUMN ra_policy_param.effective_to IS
  'NULL 이면 현행. 법 개정 시 종전 행을 닫고 신규 행을 추가한다(과거 판정은 당시 값 유지).';

CREATE UNIQUE INDEX IF NOT EXISTS ux_ra_policy_param_code_from
  ON ra_policy_param (param_code, effective_from);
CREATE INDEX IF NOT EXISTS ix_ra_policy_param_active
  ON ra_policy_param (param_code) WHERE effective_to IS NULL AND is_active;

-- ── 2. 척도·판정표 ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ra_scale (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id        uuid,
  factory_id        uuid,
  method            text        NOT NULL,
  name              text        NOT NULL,
  levels_json       jsonb       NOT NULL DEFAULT '[]'::jsonb,
  matrix_json       jsonb,
  acceptable_max    text,
  acceptable_reason text,
  is_preset         boolean     NOT NULL DEFAULT false,
  is_active         boolean     NOT NULL DEFAULT true,
  version           integer     NOT NULL DEFAULT 1,
  law_article_ref   jsonb,
  created_by        uuid,
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ck_ra_scale_method
    CHECK (method IN ('THREE_STEP','CHECKLIST','OPS','FREQ_SEV'))
);

COMMENT ON TABLE  ra_scale IS
  '위험성 척도·판단기준·허용가능수준. 사업장 자율 설정 영역이며 법령 데이터가 아니다. 프리셋 문구는 KOSHA 안내서 예시이지 조문이 아니다.';
COMMENT ON COLUMN ra_scale.is_preset IS 'true = 시스템 프리셋(company_id NULL). 사업장이 복제해 자기 기준을 만든다.';
COMMENT ON COLUMN ra_scale.version IS '완료된 평가는 당시 version 을 스냅샷 참조한다.';

CREATE INDEX IF NOT EXISTS ix_ra_scale_company ON ra_scale (company_id, is_active);
CREATE INDEX IF NOT EXISTS ix_ra_scale_preset  ON ra_scale (is_preset) WHERE is_preset;

-- ── 3. 운영 파라미터 시드 (값 + 조문 포인터만) ──────────────────────
INSERT INTO ra_policy_param (param_code, label, value_num, value_unit, applies_to, law_article_ref, note, effective_from)
VALUES
 ('INITIAL_DUE', '최초평가 착수기한', 1, 'MONTH', NULL,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":15,"clause":"1"}'::jsonb,
  '건설업은 실착공일 기산. 1개월 미만 작업·공사는 개시 후 지체 없이.', '2025-01-02'),

 ('PERIODIC_CYCLE', '정기평가 주기', 1, 'YEAR', NULL,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":15,"clause":"3"}'::jsonb,
  '전면 재실시가 아니라 적정성 재검토.', '2025-01-02'),

 ('CONTINUOUS_MONTHLY', '상시평가 월간 요건', 1, 'MONTH', NULL,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":15,"clause":"4-1"}'::jsonb,
  '발굴 + 위험성결정 + 감소대책 수립·실행까지 이루어져야 충족.', '2025-01-02'),

 ('CONTINUOUS_WEEKLY', '상시평가 주간 요건', 1, 'WEEK', NULL,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":15,"clause":"4-2"}'::jsonb,
  '참석자 직위 요건 있음. 도급 시 수급사 관리자 포함.', '2025-01-02'),

 ('CONTINUOUS_DAILY', '상시평가 일간 요건', NULL, 'WORKDAY', NULL,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":15,"clause":"4-3"}'::jsonb,
  'TBM 기록으로 충족. tbm_meetings 재사용.', '2025-01-02'),

 ('RETENTION', '기록 보존기간', 3, 'YEAR', NULL,
  '{"law_key":"007364_271485","article_no":37,"clause":"2"}'::jsonb,
  '기산점은 실시 시기별 평가 완료일.', '2025-06-01'),

 ('PREP_EXEMPT_HEADCOUNT', '사전준비 생략 기준(상시근로자)', 5, 'PERSON', NULL,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":8,"clause":"but"}'::jsonb,
  '미만 기준. 5인 이상은 사전준비 필수.', '2025-01-02'),

 ('PREP_EXEMPT_AMOUNT', '사전준비 생략 기준(건설공사 금액)', 100000000, 'KRW', 'CONSTRUCTION',
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":8,"clause":"but"}'::jsonb,
  '1억원 미만.', '2025-01-02'),

 ('MCA_HALFYEAR_CHECK', '중처법 반기 점검 주기', 1, 'HALF_YEAR', NULL,
  '{"law_key":"014159_277417","article_no":4,"clause":"3"}'::jsonb,
  '위험성평가 실시 + 결과 보고 시 갈음 가능.', '2025-10-01')
ON CONFLICT (param_code, effective_from) DO NOTHING;

-- ── 4. 척도 프리셋 시드 (사업장 자율 영역, 법령 데이터 아님) ─────────
INSERT INTO ra_scale (company_id, method, name, levels_json, acceptable_max, acceptable_reason, is_preset, law_article_ref)
VALUES
 (NULL, 'THREE_STEP', '위험성 수준 3단계 판단법 (기본 프리셋)',
  '[{"code":"HIGH","label":"상","order":3,"criteria_text":"사고 발생 시 사망 또는 장애가 남을 수 있는 위험 / 법정 기준을 만족하지 못하는 경우"},
    {"code":"MEDIUM","label":"중","order":2,"criteria_text":"사고 발생 시 요양이 필요한 위험 / 아차사고 사례가 있는 경우"},
    {"code":"LOW","label":"하","order":1,"criteria_text":"작업 수행에 영향을 미치지 않는 경미한 부상 또는 질병이 예상되는 경우"}]'::jsonb,
  'LOW', '사업장 확정 필요 — 프리셋 기본값', true,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":7,"clause":"5-3"}'::jsonb),

 (NULL, 'CHECKLIST', '체크리스트법 (기본 프리셋)',
  '[{"code":"OK","label":"적정","order":1,"criteria_text":"무시할 수 있는 위험 또는 적정하게 안전조치가 되어 있는 경우"},
    {"code":"NEEDS_ACTION","label":"보완","order":2,"criteria_text":"개선이 필요한 유해·위험요인"}]'::jsonb,
  'OK', '사업장 확정 필요 — 프리셋 기본값', true,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":7,"clause":"5-2"}'::jsonb),

 (NULL, 'OPS', '핵심요인 기술법(One Point Sheet) (기본 프리셋)',
  '[{"code":"SUFFICIENT","label":"현행 조치 유지","order":1,"criteria_text":"기존 조치가 근로자를 적절히 보호한다고 판단되는 경우"},
    {"code":"NEEDS_ACTION","label":"추가 조치 필요","order":2,"criteria_text":"추가적인 위험성 감소대책이 필요한 경우"}]'::jsonb,
  'SUFFICIENT', '사업장 확정 필요 — 프리셋 기본값', true,
  '{"source":"NOTICE_RISK_ASSESSMENT","article_no":7,"clause":"5-4"}'::jsonb)
ON CONFLICT DO NOTHING;
```

---

## 4. 조문 원문이 필요할 때 (저장하지 않고 조회)

화면에 근거 조문을 보여주거나 파라미터 정합성을 검증할 때는 **런타임 조회**로 처리한다.

```
ra_policy_param.law_article_ref  →  법령 API 조회  →  화면 표시
                                     (결과를 저장하지 않는다)
```

- `law_key` 가 있는 항목(산안법 시행규칙·중처법 시행령)은 법령엔진에 수집되어 있어 바로 조회 가능
- `source: NOTICE_RISK_ASSESSMENT` 항목(위험성평가 고시)은 **아직 법령엔진에 미수집** → 수집 후 `law_key` 로 교체. 그전까지는 포인터만 유지하고 원문 표시는 보류

---

## 5. 적용 후 검증

```sql
SELECT param_code, value_num, value_unit, law_article_ref
FROM ra_policy_param WHERE effective_to IS NULL ORDER BY param_code;   -- 기대 9행

SELECT method, name, acceptable_max FROM ra_scale WHERE is_preset;      -- 기대 3행

-- 법령 원문이 저장되지 않았는지 확인(기대: 0)
SELECT count(*) FROM information_schema.columns
WHERE table_name='ra_policy_param' AND column_name IN ('law_text','article_text');
```

---

## 6. 다음 작업
1. 설정 API 라우터 `routers/ra_settings.py` — `GET /ra/policy-params`, `GET/POST/PUT /ra/scales`
2. `routers/risk_assessments.py` 상수(`INITIAL_DUE_MONTHS`·`PERIODIC_CYCLE_YEARS`·`RETENTION_YEARS`) → `ra_policy_param` 조회로 치환
3. 위험성평가 고시의 법령엔진 수집(별도 작업) 후 `law_article_ref` 를 `law_key` 기반으로 교체
4. 설계 v2 단계 2 — 평가유형 4종 확장 + `ra_item`

## 7. 참조
- `WORKORDER_schema-legal-period-scale_v1.md` — **본 문서로 대체**
- `PLAN_risk-assessment-design_v2.md` · `RESEARCH_legal-verification_v1.md`
