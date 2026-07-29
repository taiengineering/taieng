---

class: plans
type: PLAN
scope: ops
project: tai-risk-assessment
title: safe SaaS 위험성평가 모듈 설계 — 데이터모델·상태기계·판정로직
version: 1
status: PENDING
owner: taiwang
---

# 위험성평가 모듈 설계 (v1)

- **골**: `G-ms5zwv4v-b88c4a`
- **근거 법령**: 산업안전보건법 §36, 시행규칙 §37, 고용노동부고시 「사업장 위험성평가에 관한 지침」 제2023-19호 → **제2024-76호(2025.1.2 시행)**
- **구현 대상**
  - 프론트: `taiengineering/tai-admin` · branch `main` · dir **`vue3/`** (Pages 프로젝트 `taieng-tadmin` → safe.taieng.co.kr)
  - 백엔드: `taiengineering/tai-api` · branch `main`

> ⚠️ **법률 수치는 원문 대조 전까지 확정 아님.** law.go.kr 본문이 JS 렌더링이라 직접 조회 실패, 2차 출처(KOSHA 안내서·고용노동부 고시 공고·전재 텍스트) 기반. 구현 착수 전 국가법령정보센터 원문 대조 필요. 특히 5×4 판정구간표·중대성 4단계 문언은 **부분 확인**.

---

## 1. 설계의 핵심 판단

**위험성평가는 "점수 계산 로직"이 아니다.**

2023년 개정에서 **「위험성 추정」 단계가 절차에서 삭제**되었다. 빈도×강도 계산은 이제 독립 단계가 아니라 "위험성 결정" 내부의 **선택 가능한 계산 방식 중 하나**다. 따라서 구현해야 할 것은 공식이 아니라 다음 세 가지다.

1. **파이프라인** — 사전준비 → 요인 파악 → 위험성 결정 → 감소대책 → 공유 → 기록
2. **테넌트별 판정표** — 척도·판단기준·허용수준을 사업장이 사전에 정한다(고시 §9②)
3. **재판정 루프** — 허용 가능해질 때까지 반복(고시 §12②③)

### 1-1. 하드코딩 금지 — 가장 중요한 제약

KOSHA 자료 **안에서만** 다음이 공존한다:
- 3단계 판단기준 **3가지 변형**(안내서 중소규모용 / 건설 실시규정 예시 / Part III 예시)
- 5단계 변형(제조업 실시규정 예시)
- 빈도·강도 척도 **3×3** 및 **5×4**
- 조합 연산 **곱셈 / 덧셈 / 행렬**

즉 "표준 척도"는 존재하지 않는다. **척도 정의 자체를 테넌트 설정 테이블로 분리하지 않으면 재작성이 불가피하다.**

### 1-2. 허용수준에는 하한이 있다
고시 §9②2호 — 허용 가능한 위험성 수준은 **법에서 정한 기준 이상**이어야 한다. 사업장이 임의로 낮출 수 없다. 또한 사업주는 **그렇게 정한 이유를 설명할 수 있어야** 한다 → 설정 화면에 근거 입력란 필요.

---

## 2. 데이터 모델

### 2-1. `ra_scale` — 척도·판정표 (테넌트 설정) ★
```
id                uuid
company_id        uuid        -- 테넌트
factory_id        uuid null   -- 사업장별 상이 허용
method            text        -- THREE_STEP | CHECKLIST | OPS | FREQ_SEV
name              text        -- "3단계(중소규모)" 등
levels_json       jsonb       -- 수준 정의 [{code, label, order, criteria_text}]
matrix_json       jsonb null  -- FREQ_SEV 전용: {op: MULTIPLY|ADD|MATRIX,
                              --   freq_levels:[{v,label,desc}], sev_levels:[...],
                              --   bands:[{min,max,level_code,action_text}]}
acceptable_max    text        -- 허용 가능한 최고 수준 code
acceptable_reason text        -- 그렇게 정한 이유(고시 §9② 설명책임)
is_active         bool
version           int         -- 개정 시 증가, 과거 평가는 당시 버전 참조
```
**설계 이유** — 평가 레코드는 `scale_id`(+version)를 **스냅샷 참조**해야 한다. 척도를 바꾸면 과거 평가의 판정이 소급 변경되어 기록 무결성이 깨진다.

### 2-2. `ra_assessment` — 평가 1회
```
id                uuid
company_id, factory_id
type              text  -- INITIAL | AD_HOC | PERIODIC | CONTINUOUS
trigger_reason    text  -- AD_HOC일 때 고시 §15② 1~6호 중 어느 것
scale_id          uuid
scale_version     int
status            text  -- DRAFT | IN_PROGRESS | COMPLETED
prep_json         jsonb -- 사전조사 안전보건정보 7종(고시 §9③) — 기록 필수항목
started_at        timestamptz
completed_at      timestamptz null
retention_until   date null      -- completed_at + 3년 (평가유형별 개별 산정)
participants_json jsonb          -- 참여자(근로자 참여 §36②)
created_by, approved_by
```
**보존 기산점** — 고시 §14②: "제15조에 따른 **실시 시기별** 위험성평가를 **완료한 날**부터" 기산. 최초/수시/정기/상시가 **각각 별도 카운트**되므로 레코드마다 `completed_at` + `retention_until`을 따로 가진다.

### 2-3. `ra_item` — 유해·위험요인 1건
```
id                uuid
assessment_id     uuid
work_process      text   -- 공정/단위작업
hazard            text   -- 유해·위험요인
situation_result  text   -- 위험한 상황 및 결과
exposed_count     int    -- 노출 근로자 수 (고시 §12① 대책 수립 시 고려요소)
legal_basis       text   -- 관련근거(법적기준)
current_controls  text   -- 현재의 안전보건조치
discovery_method  text   -- PATROL | SUGGESTION | INTERVIEW | DATA | CHECKLIST | ETC
raw_input_json    jsonb  -- 기법별 원입력 (freq/sev, 상중하, ○×, OPS 6문항)
level             text   -- 판정된 위험성 수준 code
acceptable        bool   -- 허용 가능 여부
escalation_json   jsonb  -- 자동 승급이 걸렸다면 사유 배열
near_miss_id      uuid null  -- 아차사고에서 유래한 경우
```

### 2-4. `ra_control` — 감소대책
```
id, item_id
hierarchy         int    -- 0 LEGAL | 1 ELIMINATE | 2 ENGINEERING | 3 ADMIN | 4 PPE
content           text
owner_user_id     uuid   -- 담당자 (고시 §12 필수)
due_date          date   -- 이행기한 (필수, 과도하게 길면 경고)
done_at           timestamptz null
evidence_json     jsonb  -- 사진·문서
is_interim        bool   -- §12④ 잠정 조치 여부
```

### 2-5. `ra_item_revision` — 재판정 이력 ★루프의 핵심
```
id, item_id
seq               int         -- 1차 판정, 2차(대책 후) ...
level, acceptable
evaluated_at, evaluated_by
note
```
**설계 이유** — `ra_item`에 `residual_level` 컬럼 하나만 두면 3차 이상 반복을 표현할 수 없다. 고시 §12③은 **허용 가능해질 때까지 반복**을 요구하므로 이력 테이블이 맞다.

### 2-6. `ra_near_miss` — 아차사고 (별도 엔티티 필수)
```
id, company_id, factory_id
occurred_at, reported_by(익명 허용), location, description
linked_item_id  uuid null
```
**두 곳에서 참조된다** — ① 평가 대상 편입 의무(고시 §5의2②) ② 상시평가 월 요건(§15④1호). 사고 모듈에 종속시키면 안 된다.

### 2-7. `ra_activity_log` — 상시평가 활동 원장
```
id, company_id, factory_id
kind         text  -- MONTHLY_DISCOVERY | WEEKLY_REVIEW | DAILY_TBM
occurred_on  date
participants_json jsonb  -- WEEKLY는 직위 검증용
ref_json     jsonb       -- 연결된 item/near_miss/회의록
```

---

## 3. 상태기계

```
DRAFT ──(사전준비 확정: scale 선택 + prep_json 입력)──▶ IN_PROGRESS
IN_PROGRESS ──(모든 item이 acceptable=true)──▶ COMPLETED
                                              └─ completed_at, retention_until 산출

item 내부 루프:
  판정(seq=1) ─ acceptable? ─ Y ─▶ 확정
                  │
                  N ─▶ 대책 수립(ra_control) ─▶ 실행(done_at) ─▶ 재판정(seq+1) ↺
```

**전이 가드**
- `DRAFT → IN_PROGRESS`: `scale_id` 필수, `prep_json` 필수(5인 미만은 면제 — 고시 §8 단서)
- `IN_PROGRESS → COMPLETED`: acceptable=false인 item이 남아 있으면 **차단**. 단 §12④ 잠정조치(`is_interim=true`)가 있으면 사유 기재 후 허용.

---

## 4. 판정 로직

### 4-1. 4기법 = 하나의 인터페이스
```python
def decide(item, scale) -> (level: str, acceptable: bool):
    if scale.method == "THREE_STEP":
        level = item.raw_input["level"]          # 사용자가 상/중/하 직접 선택
    elif scale.method == "FREQ_SEV":
        level = band_of(combine(f, s, scale), scale)
    elif scale.method == "CHECKLIST":
        level = "보완" if item.raw_input["mark"] == "X" else "적정"
    elif scale.method == "OPS":
        level = "추가조치필요" if not item.raw_input["is_sufficient"] else "현행유지"

    level = apply_escalation(level, item, scale)     # §4-2
    acceptable = order_of(level) <= order_of(scale.acceptable_max)
    return level, acceptable

def combine(f, s, scale):
    op = scale.matrix["op"]
    return f * s if op == "MULTIPLY" else f + s if op == "ADD" else scale.matrix["cells"][f][s]
```
네 기법 모두 최종 산출은 **`acceptable` 이진값**이다. 이후 워크플로는 공통.

### 4-2. 자동 승급 규칙 (고시 §11 해설 — 제품의 값어치)
```python
def apply_escalation(level, item, scale):
    reasons = []
    if item.legal_noncompliance:      reasons.append("법정기준 미충족")   # → 최고수준 강제
    if item.severe_expected:          reasons.append("중대재해 명확히 예상")
    if item.exposed_count >= 임계:     reasons.append("다수 근로자 노출")
    if item.industry_precedent:       reasons.append("동종업계 중대재해 연관")
    if reasons:
        item.escalation_json = reasons
        return raise_level(level, scale, to_max="법정기준 미충족" in reasons)
    return level
```

### 4-3. 역방향 검증 (사고 발생 시)
"허용 가능"으로 판정한 요인에서 실제 사고·아차사고가 나면 **허용수준을 잘못 정한 것**으로 본다(안내서 명시). 사고·아차사고 등록 시 과거 `ra_item`을 역추적해 경고를 띄운다.
```python
on near_miss/accident created:
    hits = ra_item.where(hazard≈발생요인, acceptable=True, assessment.status=COMPLETED)
    if hits: raise_alert("허용수준 재검토 필요", hits)
```

### 4-4. 감소대책 우선순위 검증 (고시 §12① + 안내서 0순위)
```
[0] 법령에 규정된 조치        ← 안내서가 명시한 최우선. 대부분 누락됨
[1] 제거·대체·설계단계 저감
[2] 공학적 대책 (연동장치·환기장치)
[3] 관리적 대책 (작업절차서)
[4] 개인보호구
```
**UI 가드** — hierarchy=4(PPE)만 등록하고 0~3 검토 기록이 없으면 경고. PPE는 근본대책이 아니며 보충적 수단이다.

### 4-5. 요인 파악 방법 가드
고시 §10 — 6가지 방법 중 1개 이상, 단 **특별한 사정이 없으면 1호(사업장 순회점검) 필수 포함**. `discovery_method`에 PATROL이 하나도 없으면 경고 + 사유 입력 요구.

---

## 5. 상시평가 간주 판정 ★차별화

고시 §15④ — 3요건 **AND**. 하나라도 깨지면 수시·정기평가를 별도 실시해야 한다.

```python
def continuous_verdict(factory_id, year_month) -> dict:
    # 1호: 매월 1회 이상 — 발굴 + 위험성결정 + 감소대책 수립·실행
    monthly = exists(ra_activity_log, kind=MONTHLY_DISCOVERY, month=ym) \
              and exists(ra_item created in ym with level decided) \
              and exists(ra_control created in ym)

    # 2호: 매주 — 관리책임자/안전관리자/보건관리자/관리감독자 중심 논의·공유 + 이행점검
    weeks = iso_weeks_of(ym)
    weekly = all(
        exists(ra_activity_log, kind=WEEKLY_REVIEW, week=w,
               participants ⊇ 필수직위_1개이상)
        for w in weeks)

    # 3호: 매 작업일마다 TBM
    workdays = 사업장_작업일_달력(factory_id, ym)   # 휴무일 제외
    daily = all(exists(ra_activity_log, kind=DAILY_TBM, date=d) for d in workdays)

    return {"성립": monthly and weekly and daily,
            "월": monthly, "주": weekly, "일": daily,
            "결손": 미충족_주차_및_일자_목록}
```

**대시보드 문구 예시** — "이번 달 간주 **불성립 위험** — 3주차 논의 기록 없음 / TBM 2일 누락".
경쟁 제품에서 확인되지 않은 기능이며, 요건이 깨지는 순간 고객이 법적으로 노출되므로 가치가 크다.

**주의** — 상시평가는 **수시·정기만 면제**한다. **최초평가는 면제되지 않는다.**

---

## 6. 실시 시기 로직 (고시 §15)

| 유형 | 시기 규칙 | 자동화 |
|---|---|---|
| **최초(INITIAL)** | 사업 성립일(건설=실착공일)부터 **1개월이 되는 날까지 착수**. 1개월 미만 공사는 지체 없이 | 사업장 등록 시 D+30 태스크 자동 생성 |
| **수시(AD_HOC)** | §15② 1~6호 사유 발생 시 **계획 실행 착수 전**(5호 재해는 **작업 재개 전**) | 설비도입·작업변경·재해등록 이벤트에서 발화 |
| **정기(PERIODIC)** | **1년마다** 최초평가 결과의 **적정성 재검토**(기간 내 수시 결과 포함) | 연 1회 스케줄 |
| **상시(CONTINUOUS)** | §15④ 3요건 이행 시 수시·정기 갈음 | §5 판정기 |

**수시평가 6호 사유**: ①건설물 설치·이전·변경·해체 ②기계·기구·설비·원재료 신규도입/변경 ③정비·보수(주기적·반복적으로 이미 평가한 경우 제외) ④작업방법·절차 신규도입/변경 ⑤**중대산업사고 또는 산업재해(휴업 이상)** 발생 ⑥사업주 판단

---

## 7. 기록 필수항목 (시행규칙 §37 + 고시 §14)

| # | 항목 | 저장 위치 |
|---|---|---|
| 1 | 위험성평가 **대상의 유해·위험요인** | `ra_item.hazard` |
| 2 | **위험성 결정의 내용** | `ra_item.level`, `acceptable`, `ra_item_revision` |
| 3 | 위험성 결정에 따른 **조치의 내용** | `ra_control` |
| 4-1 | 사전조사 한 **안전보건정보** | `ra_assessment.prep_json` |
| 4-2 | 그 밖에 사업장에서 필요하다고 정한 사항 | 확장 필드 |

**보존 3년** — `retention_until = completed_at + 3년`, 평가유형별 개별 산정.

---

## 8. API 초안 (tai-api)

```
GET/PUT  /ra/scales                       척도 설정 (테넌트)
POST     /ra/assessments                  평가 생성(type, trigger_reason)
PATCH    /ra/assessments/{id}/prep        사전준비 확정 → IN_PROGRESS
POST     /ra/assessments/{id}/items       요인 등록(자동 판정 수행)
POST     /ra/items/{id}/controls          대책 등록
PATCH    /ra/controls/{id}/complete       대책 실행 완료
POST     /ra/items/{id}/reevaluate        재판정 (revision seq+1)
POST     /ra/assessments/{id}/complete    완료(가드 검사 → retention_until 산출)
GET      /ra/assessments/{id}/report      결과표(서식 11 컬럼)
POST     /ra/near-misses                  아차사고 등록
POST     /ra/activity-logs                상시평가 활동 기록(월/주/일)
GET      /ra/continuous/verdict           간주 성립 판정
```

---

## 9. 서식 컬럼 (KOSHA 〈서식 11〉 매핑)

```
세부 작업내용 → work_process
유해·위험요인 파악
  위험분류 / 위험발생 상황 및 결과 → hazard / situation_result
관련근거(법적기준) → legal_basis
현재의 안전보건조치 → current_controls
위험성  가능성(빈도) / 중대성(강도) / 위험성 → raw_input_json / level
위험성 감소대책 → ra_control.content
개선 후 위험성 → ra_item_revision(최신)
개선 예정일 / 완료일 / 담당자 → due_date / done_at / owner_user_id
```

---

## 10. 구현 순서

| 단계 | 내용 | 난이도 |
|---|---|---|
| **1** | `ra_scale` 설정 화면 + 3단계 기본 프리셋 3종 시드 | 중 |
| **2** | `ra_assessment` + `ra_item` CRUD, **3단계 판단법 + 체크리스트법** 판정 | 중 |
| **3** | `ra_control` + 재판정 루프 + 완료 가드 | 중 |
| **4** | 기록·보존(서식 11 출력, retention_until) | 하 |
| **5** | `ra_near_miss` + 역방향 검증 | 중 |
| **6** | **상시평가 활동 로그 + 간주 판정 대시보드** | 중 |
| **7** | 빈도·강도법(3×3 / 5×4) 척도 추가 | 중 |
| **8** | 중대재해처벌법 §4 3호 반기점검 증적 연결 | 하 |

1차 범위는 **3단계 판단법 + 체크리스트법**(중소규모 대상, 고시 FAQ Q8이 권장). 빈도·강도법은 척도 설정으로 확장.

---

## 11. 구현 시 함정 (조사에서 확인)

1. **척도 하드코딩 금지** — KOSHA 자료 내에서만 3단계 3변형·5단계·3×3·5×4 공존
2. **재판정 루프 없이 단일 패스로 만들면 §12②③ 위반**
3. **순회점검은 사실상 필수** — 미포함 시 경고
4. **아차사고는 별도 엔티티** — 두 조문에서 참조
5. **상시평가는 최초평가를 대체하지 않음**
6. **"위험성 추정"은 절차에서 삭제됨** — 빈도·강도는 결정 내부 계산일 뿐
7. **보존 기산점이 평가유형별로 각각**
8. **허용수준에 하한 존재** — 법정 기준 이상

---

## 12. 미확인 — 구현 전 원문 대조 필요

- 5×4 판정구간표(16~20 매우높음 등)의 KOSHA 원문 페이지 직접 확인
- 중대성 4단계 각 등급의 문언 정의
- 3단계/체크리스트/OPS 전용 결과서의 정확한 셀 라벨
- 고시 2024-76호 신구조문대비표(hwpx) — §7~15 자구 변경 여부
- 기록 미보존 과태료 근거 조항

---

## 13. 참조
- `RESEARCH_feature-catalog_v1.md` — 기능 후보 카탈로그(위험성평가는 A-2/A-3)
- KOSHA 「새로운 위험성평가 안내서」(2023.5)
- 고시 제2024-76호: https://www.moel.go.kr/info/lawinfo/instruction/view.do?bbs_seq=20241201150
- KRAS 서식 11 / KOSHA 서식자료실
