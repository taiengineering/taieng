# [Track E] Phase 2.1 정확도 역순검증 PM 보고서

**작성일**: 2026-05-10  
**작성자**: PM 창 (Claude 기획창)  
**선행**: `Track_E_20260510_Phase2_1.md` (Cursor 작업 보고서, commit 49d1eed2)  
**핵심 결론**: 분류율 55.10% (1차 목표 PASS) **그러나** 정확도 ~50%만. **Phase 2.2 정확도 보강 필수**.

---

## 1. 본 보고서의 위치

사용자 PM 결정: "**분류율 % 보다 정확도 우선**. 역순검증으로 문제점 파악 → 개선 → Cursor 작업 진행".

본 보고서는 PM 창에서 DB ground truth 직접 점검 (마스터 §2.7/§2.8) + sample 카테고리화로 도출한 정확도 진단. Cursor의 Phase 2.1 보고서는 분류율 55.10% PASS을 본질로 다루지만, 본 PM 진단은 **분류 정확성**을 본질로 함.

---

## 2. 진단 방법 (마스터 §2.7/§2.8 정합)

1. DB 직접 점검: sub_type 분포, applied_rules 매핑 추적
2. 의심 룰 카테고리화: 룰별 매칭 row의 종결 패턴 정규식 분류
3. Sample 점검: 30+ 건 직접 source_text 본질 검증
4. False Negative 추정: UC 68,130 중 의무/금지 변형 빈도 측정

LLM 미사용 (마스터 §2.1). DB 빈도 분석 + 정규식 카테고리화 + 인간 가독 검증.

---

## 3. 진단 결과 종합

### 3.1 분류 정확성 (DB ground truth)

| 영역 | 매칭 | 정확 | FP | 정확도 |
|---|---|---|---|---|
| Phase 1 단편 5종 | 8,303 | 8,303 | 0 | ✅ 100% |
| HEADER 7종 (TAIL3 정확 매칭) | ~52,000 | ~52,000 | 0 | ✅ ~100% |
| AS_본다_TAIL3 (으로 본다) | 854 | 852 | 2 | ✅ 99.8% |
| **AS_본다 보조 룰 3종** | **3,267** | **0** | **3,267** | ❌ **0%** |
| DELEGATION_ACTIVE_TAIL3 (으로 정한다) | 2,759 | 2,759 | 0 | ✅ 100% |
| **DELEGATION_ETRAHADA (에 따른다)** | 1,188 | ~211 | ~977 | ❌ **18%** |
| OBLIGATION_DETAIL (할 것) | 4,355 | 4,355 | 0 | ✅ 100% |
| **OBLIGATION_DETAIL_GWAN_SAHANG (관한 사항)** | **2,391** | **0** | **2,389** | ❌ **0%** |
| WEAK_JUNYONG_HADA (준용한다) | 1,080 | 1,080 | 0 | ⚠️ sub_type 부정확 |
| ITEM 6 (한 자) | 2,161 | ~2,000+ | <100 | ✅ ~93% |

**FP 합계 추정**: 3,267 + 977 + 2,389 = **6,633건**

**실제 정확 분류율**: 83,621 - 6,633 = **76,988 / 151,751 = 50.7%** (분류율 55.10% - FP 4.4%p)

### 3.2 AS_본다 보조 룰 카테고리화

3,267건 분석 (정규식 카테고리):

| 룰 | ENUMERATION_INTRO | REFERENCE_TO_ATTACHMENT | OTHER 종결 | 의제 |
|---|---|---|---|---|
| WA_GATDA (1,998) | 1,366 (67%) | 562 (28%) | 108 (5%) | 0 |
| GWA_GATDA (948) | 219 (23%) | 111 (11%) | 638 (66%) | 0 |
| TTOHAN_GATDA (321) | 0 | 0 | 329 (99.7%) | 0 |
| **합계 (3,267)** | **1,585 (49%)** | **673 (21%)** | **1,075 (33%)** | **0% 의제** |

→ 모두 의제(deeming)가 아닌 **enumeration 도입** 또는 **별표/별지 참조**.

### 3.3 DELEGATION_ETRAHADA 카테고리화 (1,188건)

| 카테고리 | cnt | 비율 | 본질 |
|---|---|---|---|
| 진짜 위임 (정하는 바 + 령/규칙/고시) | 211 | 17.7% | ✅ DELEGATION_ACTIVE 정합 |
| 명확 FP (별표/별지/각호/기준/방법/예) | 477 | 40.1% | ❌ REFERENCE_TO_ATTACHMENT 본질 |
| OTHER 점검 필요 | 500 | 42.1% | ⚠️ |

### 3.4 OBLIGATION_DETAIL 룰별 정확도

| 룰 | 매칭 | 본질 | 평가 |
|---|---|---|---|
| OBLIGATION_DETAIL_HVV_GEOT (할 것) | 1,949 | ✅ 의무 항목 | 정확 |
| OBLIGATION_DETAIL_ITEM_GEOT (할 것) | 2,406 | ✅ 의무 항목 | 정확 |
| **OBLIGATION_DETAIL_GWAN_SAHANG (관한 사항)** | 2,389 | ❌ 단순 enumeration | **본질 ENUMERATION_ITEM** |

### 3.5 WEAK_JUNYONG_HADA 본질

1,080건 모두 "준용한다" 종결. sub_type=WEAK_한다단순 (fallback)이지만 본질은 **REFERENCE_INVOCATION** (다른 조항 적용).

### 3.6 False Negative 추정 (UC 68,130)

| 카테고리 | 추정 row | 본질 |
|---|---|---|
| **명사 종결 단편** | **59,358 (87.1%)** | **ENUMERATION_ITEM** (이미 enum 존재) |
| 다 종결 OTHER | 8,376 (12.3%) | 변형 룰 보강 필요 |
| PROHIBITION 변형 (안 된다 / 못한다) | 351 + α | 신규 룰 |
| OBLIGATION 변형 (해야/여야 한다) | 38 + α | 신규 룰 (`야/EC` 변형) |
| 의무가 있다 | 6 + α | 신규 룰 |
| 합계 명확 FN | ~60,000 | ENUMERATION_ITEM 도입으로 즉시 처리 가능 |

### 3.7 Kiwi 분해 자체 문제 (사전 보강 트리거)

- "게재" → `게/NNG + 재해/NNG` (잘못 분해)
- "회피" → `회/NNG + 피해/NNG`
→ Track C v1.3 dict_legal_terms 보강 (별도 트랙)

---

## 4. PM 권고 sub_type 구조 (마스터 §3.4)

### 4.1 현재 25 sub_type (DB CHECK)

기존 enum (활용 18 / 미활용 7):
- 활용 (18): UNCLASSIFIED, OBLIGATION_HEADER, AUTHORITY_HEADER, DEFINITION_HEADER, OBLIGATION_DETAIL_ITEM, EXCEPTION_CLAUSE, AS_본다, DELEGATION_ACTIVE, WEAK_한다단순, PENALTY_VIOLATOR_ITEM, PROHIBITION_HEADER, DELETED, EXEMPTION_HEADER, PENALTY_HEADER, WEAK_있다단순, DEFINITION_INTRO, TITLE_HEADER, DATE_EFFECTIVE
- 미활용 (7): **ENUMERATION_ITEM** ★, PARSE_FRAGMENT, DELEGATED_WAIVER, AUTHORITY_TARGET_ITEM, EXEMPTION_TARGET_ITEM, DEFINITION_TARGET_ITEM, PROHIBITION_TARGET_ITEM

→ **ENUMERATION_ITEM이 이미 enum에 존재**. 즉시 활용 가능.

### 4.2 신규 추가 권고 (3종)

| 신규 sub_type | 본질 | 패턴 예시 | 영향 row |
|---|---|---|---|
| **ENUMERATION_LIST_INTRO** | 부모의 enumeration 도입 | "다음 각 호와 같다", "다음과 같다" | ~1,585 (현재 AS_본다 FP) |
| **REFERENCE_TO_ATTACHMENT** | 별표/별지/서식 외부 참조 | "별표 N과 같다", "별표 N에 따른다", "별지에 따른다" | ~1,025 (현재 AS_본다+DELEGATION FP) |
| **REFERENCE_INVOCATION** | 다른 조항 준용/적용 | "준용한다", "적용한다" | 1,080 (현재 WEAK fallback) |

### 4.3 룰 sub_type 재매핑 (FP 정정)

| 룰 | 현재 sub_type | 신규 sub_type | row |
|---|---|---|---|
| AS_본다_WA_GATDA | AS_본다 | **다양**: 1,366 ENUMERATION_LIST_INTRO / 562 REFERENCE_TO_ATTACHMENT / 108 검토 | 1,998 |
| AS_본다_GWA_GATDA | AS_본다 | **다양**: 219 ENUMERATION_LIST_INTRO / 111 REFERENCE_TO_ATTACHMENT / 638 OTHER 검토 | 948 |
| AS_본다_TTOHAN_GATDA | AS_본다 | **폐기** (의제 X) — 또는 PARSE_FRAGMENT | 321 |
| OBLIGATION_DETAIL_GWAN_SAHANG | OBLIGATION_DETAIL_ITEM | **ENUMERATION_ITEM** | 2,389 |
| DELEGATION_ETRAHADA 별표/별지/각호 | DELEGATION_ACTIVE | **REFERENCE_TO_ATTACHMENT** | ~477 |
| DELEGATION_ETRAHADA 정하는 바/령/규칙 | DELEGATION_ACTIVE | DELEGATION_ACTIVE 유지 | ~211 |
| DELEGATION_ETRAHADA 기준/방법/예 | DELEGATION_ACTIVE | **REFERENCE_TO_ATTACHMENT** | ~123 |
| DELEGATION_ETRAHADA OTHER | DELEGATION_ACTIVE | **점검 후 결정** | ~377 |
| WEAK_JUNYONG_HADA | WEAK_한다단순 | **REFERENCE_INVOCATION** | 1,080 |

### 4.4 신규 보강 룰 (FN 매칭)

| 룰 | 패턴 | sub_type | 추정 row |
|---|---|---|---|
| OBLIGATION_HEADER_YA변형 | `야/EC + 하/VX + ᆫ다/EF` | OBLIGATION_HEADER | 38+ |
| PROHIBITION_HEADER_AN_DOEN | `안/MAG + 되/VV + ᆫ다/EF` | PROHIBITION_HEADER | 188+ |
| PROHIBITION_HEADER_MOTHANDA | `못하/VX + ᆫ다/EF` 또는 `못하/VV + ᆫ다/EF` | PROHIBITION_HEADER | 163+ |
| OBLIGATION_HAS_DUTY | `의무/NNG + 가/JKS + 있/VV + 다/EF` | OBLIGATION_HEADER | 6+ |
| EXEMPTION_AESEONEUN_AN_DOEN | `어서/EC + 는/JX + 안/MAG + 되/VV + ᆫ다/EF` | PROHIBITION_HEADER | 별도 추정 |
| **ENUMERATION_ITEM_NOMINAL** | source_text 명사 종결 (NNG/NNB로 끝) + 길이 < 80 + parent enumeration | **ENUMERATION_ITEM** | **~59,000** |
| **ENUMERATION_LIST_INTRO_DAUM** | "다음 각 호와 같다", "다음과 같다" 정확 매칭 | **ENUMERATION_LIST_INTRO** | ~1,585 |
| **REFERENCE_TO_ATTACHMENT_BYPYO** | "별표 N과 같다", "별표 N에 따른다" 정확 매칭 | **REFERENCE_TO_ATTACHMENT** | ~673 + ~123 |
| **REFERENCE_INVOCATION_JUNYONG** | "준용한다" 정확 매칭 | **REFERENCE_INVOCATION** | 1,080 |

### 4.5 효과 추정

- **분류율**: 55.10% → **~85-90%** (ENUMERATION_ITEM 도입 효과 ~59,000건 분류 가능)
- **정확도**: ~50% → **~90%+** (FP 정정 + sub_type 정확 매핑)
- **신뢰 분류율**: ~50% → **~80%+**

---

## 5. Phase 2.2 작업 권고 (Cursor 위탁)

### 5.1 작업 흐름

```
[1] 사전 점검 + 백업
   ↓
[2] DB CHECK enum 확장 (3개 신규 sub_type 추가) — 마이그레이션
   ↓
[3] 룰 sub_type 재매핑 (FP 정정)
   - AS_본다_WA/GWA/TTOHAN 룰 분할 또는 sub_type 변경
   - OBLIGATION_DETAIL_GWAN_SAHANG sub_type → ENUMERATION_ITEM
   - DELEGATION_ETRAHADA 분할 (별표/별지 → REFERENCE_TO_ATTACHMENT)
   - WEAK_JUNYONG_HADA sub_type → REFERENCE_INVOCATION
   ↓
[4] 신규 룰 INSERT (FN 보강)
   - OBLIGATION/PROHIBITION 변형 룰
   - ENUMERATION_LIST_INTRO/REFERENCE_TO_ATTACHMENT/REFERENCE_INVOCATION 정확 룰
   - ENUMERATION_ITEM_NOMINAL (단편 분류 룰, 우선순위 낮음)
   ↓
[5] Phase 2 재실행 (UC + 재매핑 대상 row)
   ↓
[6] 정확도 검증 (sample 100+ 카테고리)
   ↓
[7] 보고서 + commit + push
```

### 5.2 검증 임계 (정확도 우선)

| check | 임계 (1차) | 임계 (이상적) |
|---|---|---|
| 분류율 | ≥ 70% | ≥ 90% |
| **정확도** (sample 100건 cross-check) | **≥ 80%** | ≥ 95% |
| AS_본다 FP | 0 (모두 재매핑) | 0 |
| DELEGATION_ETRAHADA FP | 0 (별표/별지 모두 재매핑) | 0 |
| OBLIGATION_DETAIL FP | 0 (관한 사항 재매핑) | 0 |

### 5.3 본 명세 외 작업 절대 X

- Stage 3 진입
- v3.0 마스터 객체 테이블 마이그레이션
- Tier 2 본법 수집
- Phase 1 결과 변경
- Kiwi 사전 보강 (Track C v1.3 별도)

---

## 6. 절대 원칙 정합 (마스터 §2)

| 원칙 | 본 진단 적용 |
|---|---|
| ① LLM 미사용 | ✅ DB 빈도 분석 + 정규식 카테고리화 |
| ② 법령 보전 | ✅ source_text 변경 X |
| ③ 누락 0건 | ✅ FN 명확 식별 (UC 68,130 분석) |
| ④ 100% 매핑 | ✅ row 수 변동 X |
| ⑤ 오염 = 폐기 | ⚠️ FP ~6,633건은 룰 sub_type 재매핑으로 정정 (마스터 §2.5 정합 검토 필요) |
| ⑥ 검증 부담 0 | ✅ Sample 점검은 PM 자체 진행 |
| ⑦ Ground Truth 우선 | ✅ DB 직접 점검 |

### 마스터 §2.5 정합성 검토

본 FP ~6,633건은 "오염 데이터"로 판단할 수 있으나:
- row 수는 정합 (151,751)
- source_text 보전 (변경 X)
- sub_type 분류 정확성만 부정확

→ **데이터셋 단위 폐기 X, 룰 + sub_type 정정으로 처리** (Phase 2.2). 마스터 §2.5 폐기 트리거 (재현 X / 분포 이상)에는 해당 X.

---

## 7. 다음 단계 (사용자 결정 영역)

1. **DB CHECK enum 확장** (옵션 A): 본 PM 창에서 SQL 즉시 적용 또는 Cursor 위탁
2. **Cursor Phase 2.2** 위탁 명세 적용
3. **마스터 §3.4 업데이트** (사용자 결정): 신규 3 sub_type 정의 본문 추가

---

**END — Phase 2.1 정확도 ~50% → Phase 2.2 ~90%+ 도달 목표.**
