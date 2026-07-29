---

class: plans
type: PLAN
scope: ops
project: tai-risk-assessment
title: safe SaaS 위험성평가 모듈 설계 v2 — 법령 원문 대조 및 기존 자산 재설계
version: 2
status: PENDING
owner: taiwang
---

# 위험성평가 모듈 설계 (v2)

- **골**: `G-ms5zwv4v-b88c4a`
- **v1 대체**: `PLAN_risk-assessment-design_v1.md`는 ① 법령을 2차 출처로 인용 ② 기존 구현 자산을 모르고 신규 설계로 작성 — 두 결함이 있어 **본 문서로 대체**한다.
- **법령 정본**: 국가법령정보센터 **원문 직접 확인** (2026-07-29)
  - 「사업장 위험성평가에 관한 지침」 **고용노동부고시 제2024-76호, 시행 2025-01-02** — 제1~28조·부칙 전문 확인
  - 상위법: 산업안전보건법 §36, 시행규칙 §37 (leg-db 보유 최신본으로 재대조 필요 — §9)

---

## 0. v1에서 바로잡은 것

| v1 오류 | v2 정정 |
|---|---|
| 법령을 2차 출처(casenote·lbox·블로그)로 인용 | **law.go.kr 원문 전문 확인**. 조문 인용은 모두 원문 기준 |
| 신규 구축으로 설계 | **기존 자산 존재** — 라우터 7개 엔드포인트, 테이블 22컬럼, 프론트 목록화면이 이미 있고 가동 중 |
| leg-db에 위험성평가를 연결하려 함 | leg-db는 **법령엔진 시스템**. 위험성평가는 safe SaaS 도메인. 연결 지점은 §9에 한정 |
| 5×4 판정구간표를 설계에 포함 | **고시에 척도 수치가 전혀 없음을 원문으로 확인**. 척도는 100% 사업장 자율 → 설계에서 제외하고 설정으로만 |

---

## 1. 현재 자산 실측 (2026-07-29)

### 1-1. 이미 있는 것
| 계층 | 자산 | 상태 |
|---|---|---|
| BE | `routers/risk_assessments.py` v1.1.0 — 엔드포인트 7개 | `router_registry/construction.py`에 **등록·가동 중** |
| DB | `risk_assessments` 22컬럼 | **행 0건** |
| FE | `vue3/src/pages/risk-assessment-list/` | 목록 **조회 전용**, '기타' 메뉴 노출 |
| 부수 | `tbm_templates`(25건), `tbm_meetings`, `tbm_attendees` | **실사용 중** — `risk_items` jsonb에 위험요인+대책+PPE 구조 보유 |
| 부수 | `runtime_facility_hazard`(100건) | 시설별 유해위험물질 인벤토리 |

**데이터가 0건이므로 스키마를 자유롭게 재설계할 수 있다**(마이그레이션 부담 없음). 이것이 지금 착수해야 할 이유다.

### 1-2. 법정 요건 대비 결손
- 척도·판단기준·허용가능수준 설정 **전무** (고시 §9② 위반 소지)
- `assessment_type` **3종**(`INITIAL|REGULAR|SPECIAL`) — **상시평가 없음** (고시 §15④ 미대응)
- 파악→결정→감소대책→**재판정 루프 전체 부재** (고시 §12②③ 미충족)
- 사전조사 안전보건정보 필드 없음 (고시 §9③ + §14① 기록 필수항목)
- 보존만료일 미산출 — `retention_years=3` 상수만 존재 (고시 §14②)
- 유해위험요인·결정내용·조치내용이 `items_json` 비정형 jsonb에 뭉쳐 있음 (시행규칙 §37① 1~3호를 개별 항목으로 입증 불가)

### 1-3. ★ 원문 대조로 발견한 추가 결함 — 최초평가 시기 오류
`routers/risk_assessments.py` 상단 주석:
```
INITIAL   최초평가 (사업 개시 후 1년 이내)
```
**고시 §15① 원문**: *"사업이 성립된 날(사업 개시일을 말하며, 건설업의 경우 실착공일을 말한다)로부터 **1개월이 되는 날까지** … 최초 위험성평가의 **실시에 착수**하여야 한다."*

→ **1년이 아니라 1개월**이다. 2023년 개정 전 구 고시(부칙 제2014-48호 "설립일로부터 1년 이내")의 잔재로 보인다. 현재 주석대로 안내하면 **고객이 법정기한을 11개월 초과**하게 된다. 즉시 수정 대상.

### 1-4. 기존 버그 3건 (앞선 실측)
1. FE가 `date_from`/`date_to`를 보내나 BE는 `year`만 지원 → 기간 필터 무력
2. FE가 `risk_grade||grade||risk_level`을 읽으나 BE 목록 응답에 해당 필드 부재 → 등급 배지 항상 빈값
3. `assessment_type` 기본값 불일치 — DB default `REGULAR` vs 라우터 default `SPECIAL`

---

## 2. 설계 원칙 — 법령 변화에 유연한 구조

법령은 바뀐다. 실제로 고시 **§28(재검토기한)**은 *"2025년 1월 1일 기준으로 매 3년이 되는 시점마다 그 타당성을 검토"*라고 **주기적 개정을 예고**하고 있다. 따라서 다음을 원칙으로 한다.

| 원칙 | 내용 |
|---|---|
| **P1. 척도는 코드가 아니라 데이터** | 고시는 척도 수치를 **전혀 규정하지 않는다**(원문 확인). §7⑤는 기법 5종만 열거하고, §9②는 "사업주가 확정"하도록 위임. KOSHA 안내서의 3×3·5×4·상중하는 **예시일 뿐 법적 기준이 아니다**. 하드코딩하면 오류이자 재작성 대상 |
| **P2. 주기·기한은 설정 테이블** | "1개월", "1년마다", "매월/매주/매작업일"을 상수로 박지 않는다. §1-3 사고가 재발한다 |
| **P3. 평가는 조문을 참조** | 각 평가·항목이 근거 조문 코드를 보유. 개정 시 영향 범위를 역추적 가능 |
| **P4. 판정은 규칙 데이터** | 자동 승급·대책 우선순위를 코드 분기 대신 규칙 레코드로 |
| **P5. 스냅샷 불변** | 완료된 평가는 당시 척도·조문 버전을 스냅샷 보관. 설정을 바꿔도 과거 판정이 소급 변경되지 않는다 |

---

## 3. 데이터 모델 (재설계)

기존 `risk_assessments`(행 0)를 **헤더 테이블로 재정의**하고, 법정 요건을 만족하는 하위 테이블을 신설한다.

### 3-1. `ra_scale` — 척도·판정표 (신설) ★P1
```
id, company_id, factory_id(null 허용)
method            THREE_STEP | CHECKLIST | OPS | FREQ_SEV     -- 고시 §7⑤
name, levels_json                                             -- [{code,label,order,criteria_text}]
matrix_json       null 허용 -- FREQ_SEV 전용 {op:MULTIPLY|ADD|MATRIX, freq[], sev[], bands[]}
acceptable_max    허용 가능한 최고 수준 code                    -- 고시 §9②2호
acceptable_reason 그렇게 정한 이유                              -- 설명책임
version, is_active
```
**하한 제약**: §9②2호 *"이 경우 법에서 정한 기준 이상으로 위험성의 수준을 정하여야 한다"* → 저장 시 검증.

### 3-2. `risk_assessments` — 헤더 (기존 확장)
```
[유지] id, company_id, factory_id, construction_site_id, title,
       assessment_date, department, process_name, assessor_name,
       summary_text, files_json, status_code, created_by, created_at, updated_at
[변경] assessment_type   INITIAL | AD_HOC | PERIODIC | CONTINUOUS   -- 4종으로 확장
[신설] scale_id, scale_version                                     -- P5 스냅샷
       trigger_reason      AD_HOC일 때 §15② 1~6호 중 어느 것
       prep_json           사전조사 안전보건정보 §9③ 7종           -- 기록 필수항목
       participants_json   근로자 참여 §6
       completed_at, retention_until(date)                         -- §14② 완료일 기산
       law_ref_json        근거 조문·버전 스냅샷                    -- P3
[정리] items_json → 하위 테이블로 이관(레거시 호환 기간 후 제거)
       retention_years → retention_until로 대체
```

### 3-3. `ra_item` — 유해·위험요인 (신설)
```
id, assessment_id
work_process, hazard, situation_result       -- 시행규칙 §37① 1호
exposed_count                                 -- §12① 대책 수립 고려요소
legal_basis, current_controls
discovery_method  PATROL|SUGGESTION|INTERVIEW|DATA|CHECKLIST|ETC   -- §10 6종
raw_input_json                                -- 기법별 원입력
level, acceptable                             -- §37① 2호
escalation_json                               -- 자동 승급 사유
near_miss_id(null)                            -- §5의2②
```

### 3-4. `ra_control` — 감소대책 (신설)
```
id, item_id
hierarchy   0 LEGAL | 1 ELIMINATE | 2 ENGINEERING | 3 ADMIN | 4 PPE   -- §12①
content, owner_user_id, due_date, done_at, evidence_json
is_interim                                    -- §12④ 잠정조치
```
**hierarchy 0(법령 규정 조치)** — §12① 후단 *"법령에서 정하는 사항과 그 밖에 근로자의 위험 또는 건강장해를 방지하기 위하여 필요한 조치를 반영하여야 한다"*.

### 3-5. `ra_item_revision` — 재판정 이력 (신설) ★§12②③
```
id, item_id, seq, level, acceptable, evaluated_at, evaluated_by, note
```
단일 `residual_level` 컬럼으로는 3차 이상 반복을 표현할 수 없다. 고시가 *"허용 가능한 위험성 수준이 될 때까지 추가의 감소대책을 수립·실행"*을 요구하므로 이력 테이블이 정답.

### 3-6. `ra_near_miss` — 아차사고 (신설)
§5의2②가 아차사고 유발 요인의 평가 대상 편입을 **의무화**하고, §15④1호가 상시평가 월 요건으로 참조 → 독립 엔티티.

### 3-7. `ra_activity_log` — 상시평가 활동 (신설)
```
id, company_id, factory_id
kind         MONTHLY_DISCOVERY | WEEKLY_REVIEW | DAILY_TBM
occurred_on, participants_json, ref_json
```
**DAILY_TBM은 기존 `tbm_meetings`를 소스로 재사용한다**(신규 입력 요구 없음). 이미 25종 템플릿과 실데이터가 있어 상시평가 3요건 중 하나는 사실상 확보된 상태.

### 3-8. `ra_legal_period` — 법정 주기 설정 (신설) ★P2
```
code            INITIAL_DUE | PERIODIC_CYCLE | CONTINUOUS_MONTHLY |
                CONTINUOUS_WEEKLY | CONTINUOUS_DAILY | RETENTION
value_num, value_unit  (MONTH|YEAR|WEEK|DAY)
law_ref         근거 조문
effective_from, effective_to     -- 개정 시 신규 행 추가, 과거 판정은 당시 값 사용
```
초기 시드(고시 원문):
| code | 값 | 근거 |
|---|---|---|
| INITIAL_DUE | 1 MONTH | §15① |
| PERIODIC_CYCLE | 1 YEAR | §15③ |
| CONTINUOUS_MONTHLY | 1/MONTH | §15④1호 |
| CONTINUOUS_WEEKLY | 1/WEEK | §15④2호 |
| CONTINUOUS_DAILY | 매 작업일 | §15④3호 |
| RETENTION | 3 YEAR | 시행규칙 §37② |

---

## 4. 상태기계

```
DRAFT ──(scale 선택 + prep_json 입력)──▶ IN_PROGRESS
   └ 5인 미만(건설 1억원 미만)은 사전준비 생략 가능 — 고시 §8 단서

IN_PROGRESS ──(모든 item acceptable=true)──▶ COMPLETED
                                             └ completed_at, retention_until 산출

item 루프:  판정(seq=1) → acceptable? ─N→ 대책 → 실행 → 재판정(seq+1) ↺
                              └Y→ 확정
```
**완료 가드**: acceptable=false가 남아 있으면 차단. 단 §12④ 잠정조치(`is_interim`)가 있으면 사유 기재 후 허용.

---

## 5. 판정 로직

### 5-1. 4기법 단일 인터페이스
```python
def decide(item, scale) -> (level, acceptable):
    if   scale.method == "THREE_STEP": level = item.raw["level"]          # 직접 선택
    elif scale.method == "FREQ_SEV":   level = band(combine(f, s, scale), scale)
    elif scale.method == "CHECKLIST":  level = "보완" if item.raw["mark"]=="X" else "적정"
    elif scale.method == "OPS":        level = "추가조치필요" if not item.raw["sufficient"] else "현행유지"
    level = escalate(level, item, scale)
    return level, order(level) <= order(scale.acceptable_max)
```
네 기법 모두 산출은 **`acceptable` 이진값**. 이후 워크플로 공통.

### 5-2. 자동 승급
법정기준 미충족 / 중대재해 명확 예상 / 다수 노출 / 동종업계 중대재해 연관 → 수준 상향. 규칙은 `ra_rule` 데이터로 관리(P4).

### 5-3. 역방향 검증
"허용 가능"으로 판정한 요인에서 사고·아차사고 발생 시 해당 평가를 역추적해 **허용수준 재검토 경고**. §5의2②·③과 연결.

### 5-4. 가드
- `discovery_method`에 PATROL이 하나도 없으면 경고 — §10 *"특별한 사정이 없으면 제1호에 의한 방법을 포함하여야 한다"*
- hierarchy=4(PPE)만 있고 0~3 검토 기록이 없으면 경고 — §12①

---

## 6. 상시평가 간주 판정 (§15④)

3요건 **AND**. 주기 값은 `ra_legal_period`에서 읽는다(P2).
```python
월 = 발굴(제안·아차사고·순회점검) ≥ N/월 and 위험성결정 and 감소대책_수립·실행
주 = 모든 주에 논의·공유 + 이행점검 (참석자에 안전보건관리책임자/안전관리자/
                                    보건관리자/관리감독자 중 1 이상, 도급 시 수급사 관리자 포함)
일 = 모든 작업일 TBM (tbm_meetings 소스 재사용)
성립 = 월 and 주 and 일
```
**주의** — §15④는 *"제2항과 제3항의 수시평가와 정기평가를 실시한 것으로 본다"*. **최초평가는 면제되지 않는다.**

---

## 7. 갈음 처리 (§7④) — v1에서 누락한 조항

다음 제도를 이행하면 **그 부분에 대해 위험성평가를 실시한 것으로 본다**:
1. 위험성평가 방법을 적용한 안전·보건진단(법 §47)
2. 공정안전보고서(법 §44) — 단 **공정위험성 평가서가 최대 4년 범위 이내에서 정기적으로 작성된 경우에 한정**
3. 근골격계부담작업 유해요인조사(안전보건규칙 §657~662)
4. 그 밖에 법령이 정하는 위험성평가 관련 제도

→ `ra_substitution` 테이블로 "무엇을 무엇으로 갈음했는지" 기록. 고객이 이미 공정안전보고서를 갖고 있으면 중복 작업을 면제해 주는 것이므로 **영업 가치가 큰 기능**이다.

---

## 8. 즉시 수정 대상 (설계와 별개로 선행)

| # | 내용 | 근거 |
|---|---|---|
| F1 | 라우터 주석 "최초평가(사업 개시 후 1년 이내)" → **"1개월이 되는 날까지 착수"** | 고시 §15① |
| F2 | `date_from`/`date_to` 쿼리 지원 추가 | FE-BE 불일치 |
| F3 | 목록 응답에 등급 필드 추가 또는 FE 수정 | FE-BE 불일치 |
| F4 | `assessment_type` 기본값 통일(DB `REGULAR` vs 라우터 `SPECIAL`) | 정합성 |

---

## 9. leg-db 연결 (한정)

leg-db는 **법령엔진 시스템**이며 위험성평가 모듈의 저장소가 아니다. 연결은 다음으로 한정한다.
- 상위법(산안법 §36, 시행규칙 §37) **원문 대조** — leg-db 보유본이 최신(산안법 2025-10-01 / 시행규칙 2025-06-01)
- `ra_legal_period.law_ref`, `risk_assessments.law_ref_json`이 조문 코드를 참조
- **위험성평가 고시는 leg-db 미수집** — 별도 수집 필요(고시 계열 자체가 거의 미수집)

---

## 10. 구현 순서

| 단계 | 내용 | 비고 |
|---|---|---|
| **0** | F1~F4 즉시 수정 | 설계 무관, 오류 |
| **1** | `ra_legal_period` + `ra_scale` 스키마·API·설정화면 | P1·P2 기반 |
| **2** | `risk_assessments` 확장 + `ra_item` + 3단계·체크리스트 판정 | 1차 기법 |
| **3** | `ra_control` + `ra_item_revision` 재판정 루프 + 완료 가드 | §12 |
| **4** | 기록·보존(서식 출력, `retention_until`) | §14 |
| **5** | `ra_near_miss` + 역방향 검증 | §5의2 |
| **6** | `ra_activity_log` + 상시평가 간주 판정(TBM 재사용) | §15④ |
| **7** | FREQ_SEV 척도 추가 | 확장 |
| **8** | `ra_substitution` 갈음 처리 | §7④ |

---

## 11. 미확인 — 착수 전 확인

- 산안법 §36·시행규칙 §37 **원문**을 leg-db 최신본으로 재대조(본 문서는 고시 원문만 직접 확인)
- 중대재해처벌법 시행령 §4 3호 갈음 관계 — leg-db 2025-10-01 시행본 기준 재확인 (v1은 2021 제정본 기준이었음)
- 위험성평가 고시의 leg-db 수집 방안(45cminc/leg · leg-runtime 파이프라인 조사 필요)

---

## 12. 참조
- 고시 원문: 국가법령정보센터 행정규칙 「사업장 위험성평가에 관한 지침」 제2024-76호
- `RESEARCH_feature-catalog_v1.md` — 기능 후보 카탈로그(A-2/A-3)
- `PLAN_risk-assessment-design_v1.md` — **본 문서로 대체됨**
