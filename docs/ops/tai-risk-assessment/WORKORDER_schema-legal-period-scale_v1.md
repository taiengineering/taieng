---

class: plans
type: WORKORDER
scope: ops
project: tai-risk-assessment
title: 위험성평가 스키마 워크오더 — ra_legal_period·ra_scale (적용 대기)
version: 1
status: PENDING
owner: taiwang
---

# WORKORDER — 위험성평가 설정 스키마 (ra_legal_period · ra_scale)

- **골**: `G-ms5zwv4v-b88c4a`
- **상태**: **적용 대기** — `supabase/migrations/` 는 R-005 보호 경로라 AI가 쓸 수 없다. 아래 SQL을 오퍼레이터가 정식 마이그레이션으로 옮겨 적용한다.
- **적용 방법**: 아래 §3 SQL을 `supabase/migrations/20260729120000_ra_legal_period_and_scale.sql` 로 저장 후 적용.
- **선행 완료**: F1~F4 긴급 정정 (tai-api `5fd3cd9`)

---

## 1. 왜 설정 테이블인가 (설계 근거)

**산업안전보건법 제36조제4항**이 *"평가의 방법, 절차 및 시기, 그 밖에 필요한 사항"*을 **전부 고시에 위임**한다. 그리고 고시(제2024-76호) **제28조**는 *"2025년 1월 1일 기준으로 매 3년이 되는 시점마다 그 타당성을 검토"* — **주기적 개정이 예고**되어 있다.

또한 **고시 원문 어디에도 위험성 척도 수치(3×3, 5×4, 상/중/하)가 없다.** 제9조제2항이 *"위험성의 수준과 그 수준을 판단하는 기준"* 및 *"허용 가능한 위험성의 수준"*을 사업주가 사전 확정하도록 위임한다. KOSHA 안내서의 척도표는 **예시일 뿐 법적 기준이 아니다.**

→ 주기·기한·척도를 코드 상수로 두면 법 개정 시 전면 재작업이 발생한다.

**실제 사고 사례** — `routers/risk_assessments.py`가 최초평가 기한을 "1년 이내"로 안내하고 있었다(2014년 구 고시 부칙 잔재). 현행 고시 제15조제1항은 **"1개월이 되는 날까지 착수"**다. 그대로 두면 고객이 법정기한을 11개월 초과한다. F1에서 정정했으나, 애초에 상수로 박은 구조가 원인이었다.

---

## 2. 테이블 요약

| 테이블 | 목적 | 핵심 |
|---|---|---|
| `ra_legal_period` | 법정 주기·기한을 조문 원문과 함께 데이터로 | `effective_from/to` 로 개정 이력 관리. 과거 판정은 당시 값 유지 |
| `ra_scale` | 척도·판단기준·허용가능수준 | `is_preset` 프리셋을 사업장이 복제해 사용. `version` 으로 스냅샷 |

**시드 내용**
- 법정 주기 **9종**: 최초평가 1개월 / 정기 1년 / 상시 월·주·작업일 / 보존 3년 / 사전준비 생략기준(5인·1억원) / 중처법 반기점검
- 척도 프리셋 **3종**: 3단계 판단법 / 체크리스트법 / 핵심요인기술법(OPS)
- 각 행에 **근거 조문 + 원문 발췌**를 함께 저장 → 개정 시 diff 대조 가능

---

## 3. 적용할 SQL

```sql
-- =====================================================================
-- 위험성평가 모듈 — 법정 주기 및 척도 설정 테이블
-- Goal    : G-ms5zwv4v-b88c4a
-- 설계    : docs/ops/tai-risk-assessment/PLAN_risk-assessment-design_v2.md
-- 법령검증: docs/ops/tai-risk-assessment/RESEARCH_legal-verification_v1.md
-- =====================================================================

-- ── 1. 법정 주기·기한 ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ra_legal_period (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code            text        NOT NULL,
  label           text        NOT NULL,
  value_num       numeric,
  value_unit      text,
  applies_to      text,
  law_ref         text        NOT NULL,
  law_text        text,
  note            text,
  effective_from  date        NOT NULL,
  effective_to    date,
  is_active       boolean     NOT NULL DEFAULT true,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ra_legal_period IS '위험성평가 법정 주기·기한. 법 개정 시 종전 행의 effective_to 를 닫고 신규 행을 추가한다(과거 판정은 당시 값을 유지).';
COMMENT ON COLUMN ra_legal_period.law_text IS '근거 조문 원문 발췌. 개정 시 diff 대조용.';
COMMENT ON COLUMN ra_legal_period.effective_to IS 'NULL 이면 현행. 개정 시 신규 시행일 전날로 닫는다.';

CREATE UNIQUE INDEX IF NOT EXISTS ux_ra_legal_period_code_from
  ON ra_legal_period (code, effective_from);
CREATE INDEX IF NOT EXISTS ix_ra_legal_period_active
  ON ra_legal_period (code) WHERE effective_to IS NULL AND is_active;

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
  law_ref           text,
  created_by        uuid,
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ck_ra_scale_method
    CHECK (method IN ('THREE_STEP','CHECKLIST','OPS','FREQ_SEV'))
);

COMMENT ON TABLE  ra_scale IS '위험성 척도·판단기준·허용가능수준. 고시에 척도 수치 규정이 없고 제9조제2항이 사업주에게 위임하므로 설정 데이터로 관리한다.';
COMMENT ON COLUMN ra_scale.is_preset IS 'true = 시스템 제공 프리셋(company_id NULL). 사업장은 이를 복제해 자기 기준을 만든다.';
COMMENT ON COLUMN ra_scale.acceptable_max IS '고시 제9조제2항제2호. 법에서 정한 기준 이상으로 정하여야 한다(하한 제약).';
COMMENT ON COLUMN ra_scale.version IS '완료된 평가는 당시 version 을 스냅샷 참조한다. 척도 변경이 과거 판정을 소급 변경하지 않도록 한다.';

CREATE INDEX IF NOT EXISTS ix_ra_scale_company ON ra_scale (company_id, is_active);
CREATE INDEX IF NOT EXISTS ix_ra_scale_preset  ON ra_scale (is_preset) WHERE is_preset;

-- ── 3. 법정 주기 시드 (고시 제2024-76호 / 시행규칙 제37조 원문 기준) ──
INSERT INTO ra_legal_period (code, label, value_num, value_unit, applies_to, law_ref, law_text, note, effective_from)
VALUES
 ('INITIAL_DUE', '최초평가 착수기한', 1, 'MONTH', NULL,
  '고시 제2024-76호 제15조제1항',
  '사업이 성립된 날(사업 개시일을 말하며, 건설업의 경우 실착공일을 말한다)로부터 1개월이 되는 날까지 (중략) 최초 위험성평가의 실시에 착수하여야 한다.',
  '건설업은 실착공일 기산. 1개월 미만 작업·공사는 개시 후 지체 없이 실시.', '2025-01-02'),

 ('PERIODIC_CYCLE', '정기평가 주기', 1, 'YEAR', NULL,
  '고시 제2024-76호 제15조제3항',
  '(중략) 제1항에 따라 실시한 위험성평가의 결과에 대한 적정성을 1년마다 정기적으로 재검토(중략)하여야 한다.',
  '전면 재실시가 아니라 적정성 재검토.', '2025-01-02'),

 ('CONTINUOUS_MONTHLY', '상시평가 월간 요건', 1, 'MONTH', NULL,
  '고시 제2024-76호 제15조제4항제1호',
  '매월 1회 이상 근로자 제안제도 활용, 아차사고 확인, 작업과 관련된 근로자를 포함한 사업장 순회점검 등을 통해 사업장 내 유해ㆍ위험요인을 발굴하여 제11조의 위험성결정 및 제12조의 위험성 감소대책 수립ㆍ실행을 할 것',
  '발굴 + 위험성결정 + 감소대책 수립·실행까지 이루어져야 충족.', '2025-01-02'),

 ('CONTINUOUS_WEEKLY', '상시평가 주간 요건', 1, 'WEEK', NULL,
  '고시 제2024-76호 제15조제4항제2호',
  '매주 안전보건관리책임자, 안전관리자, 보건관리자, 관리감독자 등(도급사업주의 경우 수급사업장의 안전ㆍ보건 관련 관리자 등을 포함한다)을 중심으로 제1호의 결과 등을 논의ㆍ공유하고 이행상황을 점검할 것',
  '참석자 직위 요건 있음. 도급 시 수급사 관리자 포함.', '2025-01-02'),

 ('CONTINUOUS_DAILY', '상시평가 일간 요건', NULL, 'WORKDAY', NULL,
  '고시 제2024-76호 제15조제4항제3호',
  '매 작업일마다 제1호와 제2호의 실시결과에 따라 근로자가 준수하여야 할 사항 및 주의하여야 할 사항을 작업 전 안전점검회의 등을 통해 공유ㆍ주지할 것',
  'TBM(작업 전 안전점검회의) 기록으로 충족. tbm_meetings 재사용.', '2025-01-02'),

 ('RETENTION', '기록 보존기간', 3, 'YEAR', NULL,
  '산업안전보건법 시행규칙 제37조제2항',
  '사업주는 제1항에 따른 자료를 3년간 보존해야 한다.',
  '기산점은 고시 제14조제2항 — 실시 시기별 위험성평가를 완료한 날부터.', '2025-06-01'),

 ('PREP_EXEMPT_HEADCOUNT', '사전준비 생략 기준(상시근로자)', 5, 'PERSON', NULL,
  '고시 제2024-76호 제8조 단서',
  '다만, 상시근로자 5인 미만 사업장(건설공사의 경우 1억원 미만)의 경우 제1호의 절차를 생략할 수 있다.',
  '미만 기준. 5인 이상은 사전준비 필수.', '2025-01-02'),

 ('PREP_EXEMPT_AMOUNT', '사전준비 생략 기준(건설공사 금액)', 100000000, 'KRW', 'CONSTRUCTION',
  '고시 제2024-76호 제8조 단서',
  '다만, 상시근로자 5인 미만 사업장(건설공사의 경우 1억원 미만)의 경우 제1호의 절차를 생략할 수 있다.',
  '1억원 미만.', '2025-01-02'),

 ('MCA_HALFYEAR_CHECK', '중처법 반기 점검 주기', 1, 'HALF_YEAR', NULL,
  '중대재해처벌법 시행령 제4조제3호·제5호나목·제7호·제8호·제9호, 제5조제2항제1호·제3호',
  '(중략) 반기 1회 이상 점검한 후 필요한 조치를 할 것',
  '제4조제3호는 산안법 제36조 위험성평가 실시 + 결과 보고받은 경우 점검한 것으로 갈음.', '2025-10-01')
ON CONFLICT (code, effective_from) DO NOTHING;

-- ── 4. 척도 프리셋 시드 ─────────────────────────────────────────────
-- 주의: 아래 값은 KOSHA 안내서의 예시이며 법령이 규정한 수치가 아니다.
--       사업장은 이를 복제해 자기 기준으로 수정하고, 그 이유를 acceptable_reason 에 남긴다.
INSERT INTO ra_scale (company_id, method, name, levels_json, acceptable_max, acceptable_reason, is_preset, law_ref)
VALUES
 (NULL, 'THREE_STEP', '위험성 수준 3단계 판단법 (기본 프리셋)',
  '[{"code":"HIGH","label":"상","order":3,"criteria_text":"사고 발생 시 사망 또는 장애가 남을 수 있는 위험 / 산업안전보건법에 따른 기준을 만족하지 못하는 경우"},
    {"code":"MEDIUM","label":"중","order":2,"criteria_text":"사고 발생 시 요양이 필요한 위험 / 아차사고 사례가 있는 경우"},
    {"code":"LOW","label":"하","order":1,"criteria_text":"작업 수행에 영향을 미치지 않는 경미한 부상 또는 질병이 예상되는 경우"}]'::jsonb,
  'LOW', '사업장 확정 필요 — 프리셋 기본값', true,
  '고시 제2024-76호 제7조제5항제3호 / 제9조제2항'),

 (NULL, 'CHECKLIST', '체크리스트법 (기본 프리셋)',
  '[{"code":"OK","label":"적정","order":1,"criteria_text":"무시할 수 있는 위험 또는 적정하게 안전조치가 되어 있는 경우"},
    {"code":"NEEDS_ACTION","label":"보완","order":2,"criteria_text":"개선이 필요한 유해·위험요인"}]'::jsonb,
  'OK', '사업장 확정 필요 — 프리셋 기본값', true,
  '고시 제2024-76호 제7조제5항제2호'),

 (NULL, 'OPS', '핵심요인 기술법(One Point Sheet) (기본 프리셋)',
  '[{"code":"SUFFICIENT","label":"현행 조치 유지","order":1,"criteria_text":"기존 조치가 근로자를 적절히 보호한다고 판단되는 경우"},
    {"code":"NEEDS_ACTION","label":"추가 조치 필요","order":2,"criteria_text":"추가적인 위험성 감소대책이 필요한 경우"}]'::jsonb,
  'SUFFICIENT', '사업장 확정 필요 — 프리셋 기본값', true,
  '고시 제2024-76호 제7조제5항제4호')
ON CONFLICT DO NOTHING;
```

---

## 4. 적용 후 검증 쿼리

```sql
SELECT code, label, value_num, value_unit, law_ref
FROM ra_legal_period WHERE effective_to IS NULL ORDER BY code;
-- 기대: 9행

SELECT method, name, acceptable_max FROM ra_scale WHERE is_preset;
-- 기대: 3행
```

---

## 5. 적용 후 다음 작업

1. **설정 API 라우터** `routers/ra_settings.py` 신설 — `GET /ra/legal-periods`, `GET/POST/PUT /ra/scales`, registry 등록
2. `routers/risk_assessments.py` 의 상수(`INITIAL_DUE_MONTHS`, `PERIODIC_CYCLE_YEARS`, `RETENTION_YEARS`)를 `ra_legal_period` 조회로 **치환** — 이번 F1 사고의 재발 방지
3. 설계 v2 단계 2(평가유형 4종 확장 + `ra_item`) 착수

---

## 6. 참조
- `PLAN_risk-assessment-design_v2.md` — 설계
- `RESEARCH_legal-verification_v1.md` — 법령 원문 대조 검증서
