# D단계 연결 = 법령엔진 어댑터 (생태계 계약 준수) — 2026-06-14, 15차

> 확정: 의미절↔법령엔진 연결은 **별도 진단 서비스**가 아니라 **45cm 생태계 표준 계약을
> 따르는 "법령엔진 어댑터"**로 한다. 엔진이 어떻게 생겼든·무슨 역할이든, 입력은 표준 계약으로
> 넣는다는 것은 정해진 규칙. 어댑터는 도메인 입력 → 표준 계약 변환만 책임진다.
> 근거: 45cminc/development-governance 의 헌법·계약·어댑터 구조 (이 세 가지만 읽음).
> 앞 설계문서(2026-06-14_STAGE_D_*)는 어댑터 방식으로 대체/구체화됨.

---

## 0. 거름 방식 결정 — RASE 추출 (외부 리서치 + 목적 확정, 2026-06-14)

**목적(대표 확정): "빠짐없이".** 추출 방식은 정확도로 전문가 컨설팅을 이기는 게 아니다.
전문가가 닿지 못하는 사업장(소규모·상시·저비용)에 **놓치면 안 될 의무를 빠짐없이 보여주는 것**이
목적. 비교 대상은 전문가가 아니라 "엑셀+과태료 리스크". 정밀이 필요하면 전문가 연결로 넘긴다.

**방식(Claude 결정, 외부 리서치 근거): 거름망(빼기)이 아니라 RASE 추출(담기).**
- 거름망(빼기): 규칙이 다 있어야 작동 → 법령은 binding 2%뿐이라 구멍 남(15,279건 다 통과). ✗
- RASE 추출(담기): 적용대상이 일치하면 담음. 애매하면 안 담을 뿐, 오염 구조적 차단. ✓

**RASE = 건축·소방 코드 자동판정 세계 표준** (SMARTcodes, 싱가포르 CORENET, 영국/노르웨이/
두바이/중국/말레이시아 소방, Beach et al.이 Drools로 구현). 법조문 1건을 4요소로 분해:
- **R**equirement(요건): 충족할 조건 (= 의미절 action_text / condition 수치)
- **A**pplicability(적용대상): **이 규정이 누구에게 적용되는가** (= 의미절 executor_text)
- **S**election(선택): 구체 사례 한정 (= 의미절 condition_text)
- **E**xception(예외): 적용 제외 (= 단서조항)

우리 의미절은 이미 육하원칙 분해라 RASE에 매핑됨. 핵심은 **Applicability(적용대상)를 Requirement
(요건)과 분리**하는 것 — 소방업자 의무 오염은 이 분리를 안 해서 생겼음.

**판정 순서 (Claude 결정):**
1. **적용대상(executor) 먼저** — 사업장이 이 의무의 수범자인가? (=, have / 단위 없음).
   소방업자·관리업자 의무 여기서 탈락. 14번 실패한 수치를 안 거침.
2. **요건(수치) 그 다음** — 적용대상인 것만 규모 비교 (≥,≤ / 단위 필요).
3. **모르는 값은 0/false로 깔지 않는다** (Jason Morris 교훈: 정방향 엔진이 미입력을 0/false로
   처리해 오판). 모르면 통과도 탈락도 아닌 **보류(남김)**.

**"빠짐없이"의 구현 원칙: 적용대상이 명백히 불일치할 때만 버린다. 애매·미상이면 남긴다(추출
후보로). 빠뜨리는 것보다 후보로 남겨 사용자·전문가가 보게 한다.**

**연산자 2묶음:**
- 포함/일치 (=, y/n, have, in): 단위 없음. 적용대상·섹터·설비 유무. → 1차 추출
- 크기 (<, >, ≤, ≥): 단위 필요. 규모 요건. → 2차

**지식 판정 격리:** "executor가 이 사업장 적용대상인가"(공사시공자=건설사업장,
소방시설공사업자≠건설사업장)는 법령 지식 = LLM(Claude) 판정. 단 체크엔진 코어엔 안 넣고
어댑터/별도 검증단계에 격리(오염 금지).

**정·역방향 둘 다 (리서치 결론):** 정방향(법령엔진, 입력→의무도출 = RASE 추출) +
역방향(체크엔진, 결과→룰 역대조). 양자택일 아님.

---

## 1. 왜 어댑터인가 (읽은 사실)

45cm는 런타임엔진들을 연결해 생태계를 만드는 프로젝트이고, 체크엔진이 그 규칙으로 만들어져
있다. 핵심 원칙(evaluation-core/contracts.ts 주석):
**"Pure. Stateless. Domain-agnostic. No DB/network/SDK."** — 엔진 코어는 도메인(법령·sector)을
모른다. 도메인 입력은 반드시 **어댑터**를 거쳐 표준 계약으로 변환되어 들어간다.

= 의미절을 엔진에 "직접 꽂는" 게 아니라, 어댑터가 표준 계약으로 변환해 넣는다.
= 법령엔진은 특화엔진(범용 아님)이지만, 생태계에 붙으려면 같은 계약 형식을 쓴다.
= 엔진 코어 무수정. 도메인 지식(수범자·sector 판정)은 어댑터에 격리.

## 2. 표준 계약 (엔진이 받는 것 — evaluation-core/contracts.ts)

```
EvaluationContext = {
  actor   (누가)    : id, type(human/agent/system/service), identity, roles[], attributes
  action  (무엇을)  : type, operation, targets[], reason, metadata
  scope   (어디까지): namespaces[], resources[], boundaries{maxTargets, crossNamespace}
  environment       : name, frozen, ...
}
  ↓ 엔진 평가(범용)
EvaluationResult = { decision(ALLOW/DENY/REQUIRE_APPROVAL/...), policy, risk, authority,
                     trace[], reasons[], suggestions[] }
```

## 3. 어댑터 구조 (evaluation-core/adapters/contracts.ts + registry.ts)

```
Adapter = {
  id, name, version, supportedActionTypes[], policyNamespace
  contextProviders[] : provide(base) → { environment?, targets?, metadata? }   ← 입력→표준 변환
  policyProvider     : getPolicies() → PolicyDefinition[]                       ← 도메인 판정규칙
  lifecycle?         : onBeforeEvaluate / onAfterEvaluate
}
```
- 어댑터를 `AdapterRegistry.register()` → 엔진이 `collectContext()`로 표준 컨텍스트 완성,
  `collectPolicies()`로 정책 수집. 엔진 코어는 등록된 어댑터를 통해서만 도메인을 받음.

## 4. 법령엔진 어댑터 — 변환 틀 (의미절·사용자입력 → 표준 계약)

### 의미절(semantic_clause) → 표준  [RASE 매핑]
| 의미절 | → 표준 계약 | RASE |
|---|---|---|
| executor_text (수범자, 9,292건 보정) | **actor** (누가) | **A 적용대상** |
| action_text (행위) | **action.operation** | **R 요건** |
| content_type (OBLIGATION/PROHIBITION) | **action.type** | - |
| condition_text (조건) | **scope** (적용 범위/요건) | **S 선택** |
| cycle_text (주기) | action.metadata | - |
| source_article_id (법조문) | **action.targets[]** (법령 출처·연결키) | - |

### 사용자 입력 → 표준
| 입력(예: 건설/30명/50억/건축/하도급20) | → 표준 계약 |
|---|---|
| 섹터·공사종류 | **scope** (사업장 범위) / actor.attributes |
| 인원·금액·하도급 | **actor.attributes** (대조 기준값) |

### 법령 특화 판정 → policyProvider (RASE 적용대상 우선)
- 1차: "이 actor(executor)가 이 사업장의 적용대상인가" (=, have). 사업주 vs 소방업자 구분.
- 2차: "이 scope(요건)이 이 사업장에 해당하는가" (≥,≤ 규모).
- = 도메인 지식. policyProvider에 격리. 엔진 코어엔 안 넣음. LLM 판정은 어댑터/별도 단계.
- "빠짐없이": 적용대상 명백 불일치만 버림. 애매·미상은 남김.

## 5. 범위 (이번 작업 — 좁힘)
- **법령엔진 어댑터를 만들어 입력(의미절+사용자입력)을 표준 계약으로 변환**. 그것만.
- 엔진 코어·체크엔진 코어 무수정. 분해기·판정로직(GPT 영역) 무수정.
- 뒤(엔진이 어떻게 정리·출력하는지)는 이 작업 밖. 표준으로 넣으면 엔진이 함.

## 6. 안 하는 것 (과거 실패 차단)
- 별도 진단 서비스로 전체 재구현 ✗ (앞서 만든 semantic_diagnosis_service는 이 방식 아님 → 폐기/대체)
- 엔진 내부 파고들기 ✗ (표준만 넣으면 됨)
- 뒤를 고려해 멀리 설계 ✗ (어댑터 변환 하나만)
- 수치(단위) 먼저 거르기 ✗ (14번 실패. 적용대상 먼저)
- 모르는 값 0/false로 깔기 ✗ (오판. 보류=남김)
