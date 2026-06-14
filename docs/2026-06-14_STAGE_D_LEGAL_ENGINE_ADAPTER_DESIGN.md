# D단계 연결 = 법령엔진 어댑터 (생태계 계약 준수) — 2026-06-14, 15차

> 확정: 의미절↔법령엔진 연결은 **별도 진단 서비스**가 아니라 **45cm 생태계 표준 계약을
> 따르는 "법령엔진 어댑터"**로 한다. 엔진이 어떻게 생겼든·무슨 역할이든, 입력은 표준 계약으로
> 넣는다는 것은 정해진 규칙. 어댑터는 도메인 입력 → 표준 계약 변환만 책임진다.
> 근거: 45cminc/development-governance 의 헌법·계약·어댑터 구조 (이 세 가지만 읽음).
> 앞 설계문서(2026-06-14_STAGE_D_*)는 어댑터 방식으로 대체/구체화됨.

---

## 1. 왜 어댑터인가 (읽은 사실)

45cm는 런타임엔진들을 연결해 생태계를 만드는 프로젝트이고, 체크엔진(Generic Evaluation
Engine)이 그 규칙으로 만들어져 있다. 핵심 원칙(evaluation-core/contracts.ts 주석):
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

### 의미절(semantic_clause) → 표준
| 의미절 | → 표준 계약 |
|---|---|
| executor_text (수범자, 오늘 9,292건 보정) | **actor** (누가) |
| action_text (행위) | **action.operation** |
| content_type (OBLIGATION/PROHIBITION) | **action.type** |
| condition_text (조건) | **scope** (적용 범위/요건) |
| cycle_text (주기) | action.metadata |
| source_article_id (법조문) | **action.targets[]** (법령 출처·연결키) |

### 사용자 입력 → 표준
| 입력(예: 건설/30명/50억/건축/하도급20) | → 표준 계약 |
|---|---|
| 섹터·공사종류 | **scope** (사업장 범위) |
| 인원·금액·하도급 | **actor.attributes** 또는 scope 대조 기준값 |

### 법령 특화 판정 → policyProvider
- "이 수범자(executor)가 이 사업장의 주체인가" (사업주 vs 소방업자 vs 관리업자 구분)
- "이 조건(condition)이 이 사업장에 해당하는가" (규모·설비 요건)
- = 도메인 지식. 어댑터의 policyProvider에 격리. 엔진 코어엔 안 넣음.
- 지식 판정에 LLM이 필요하면 어댑터/별도 검증단계에서(코어 오염 금지).

## 5. 범위 (이번 작업 — 좁힘)
- **법령엔진 어댑터를 만들어 입력(의미절+사용자입력)을 표준 계약으로 변환**. 그것만.
- 엔진 코어·체크엔진 코어 무수정. 분해기·판정로직(GPT 영역) 무수정.
- 뒤(엔진이 어떻게 정리·출력하는지)는 이 작업 밖. 표준으로 넣으면 엔진이 함.

## 6. 안 하는 것 (과거 실패 차단)
- 별도 진단 서비스로 전체 재구현 ✗ (앞서 만든 semantic_diagnosis_service는 이 방식 아님 → 폐기/대체)
- 엔진 내부 파고들기 ✗ (표준만 넣으면 됨)
- 뒤를 고려해 멀리 설계 ✗ (어댑터 변환 하나만)
