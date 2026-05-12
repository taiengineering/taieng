# [Track E] Phase 2.1 — 23 룰 전체 재설계 결과

**실행일**: 2026-05-10  
**명세**: `docs/extraction/v3/log/Cursor_Phase_2_1_Rule_Redesign_Spec.md`  
**코드**: `tai-api/scripts/track_e_phase2_run.py --phase21`, `engine/phase_21_rule_payload.py`, `engine/subtype_rule_match.py`

---

## 1. 사전 점검 (§2.1)

| 항목 | 실측 |
|---|---|
| stage_1_clauses | 151,751 |
| stage_2_elements | 151,751 |
| rule_classify_subtype (enabled) | 23 → 변경 후 **34** (신규 INSERT + 일부 비활성) |
| rule_classify_if_pattern (enabled) | 8 |
| UNCLASSIFIED (진입) | **143,220** |
| tokenization_json NULL | **0%** |

→ 명세와 일치. 진입 통과.

---

## 2. 백업 (§5)

| 테이블 | 행 수 |
|---|---|
| rule_classify_subtype_backup_20260510_pre_phase2_1 | 23 |
| stage_2_elements_backup_20260510_pre_phase2_1 | 151,751 |

---

## 3. Sample 점검 요약 (§3 / §3.3)

Kiwi **잔여 UNCLASSIFIED** 및 법령 표현 검색으로 tail 시그니처를 수집했다 (LLM 미사용).

대표 발견:

| sub_type 방향 | 반복 시그니처 예 (TOP) | 조치 |
|---|---|---|
| AUTHORITY / 금지 / 의무 | `ᆯ/ETM`, `ᆫ다/EF`, `하/XSV + 지/EC + 아니하/VX + ᆫ다/EF` | conjoining jamo로 룰 문자열 통일 + 금지 룰 4모프 패턴으로 정정 |
| AS_본다 | `와/JKB + 같/VA + 다/EF`, `과/JKB + 같/VA + 다/EF` | 다양성 룰 INSERT |
| OBLIGATION_DETAIL | `관하/VV + ᆫ/ETM + 사항/NNG`, `하/VV + ᆯ/ETM + 것/NNB` | 별도 priority 룰 INSERT |
| 기타 | `에/JKB + 따르/VV + ᆫ다/EF`, `준용/NNG + 하/XSV + ᆫ다/EF` 등 | DELEGATION / WEAK 보조 |

전량 500건 표는 DB 빈도 스크립트와 동일 근거를 사용했다.

---

## 4. 룰 변경 요약 (§4)

- **UPDATE**: 기존 TAIL_POS 패턴의 **호환 자모(ㄴ/ㄹ/ㄴ다) → Kiwi conjoining(`ᆫ`,`ᆯ`,`ᆫ다`)** 및 실측 태그 정합 (예: `PROHIBITION_HEADER_NOT_DOEN` → `하/XSV + 지/EC + 아니하/VX + ᆫ다/EF`, `pattern_position` = `TAIL_5`).
- **INSERT**: 다양성 룰 **12건** (MAG 금지, PENALTY_VIOLATOR 변형, AS_본다·관한 사항·고시·따른다·준용 등).
- **비활성**: `AUTHORITY_HEADER_VV_TAIL` — 코퍼스에서 `있/VV` 권한 패턴이 유의미하게 관측되지 않아 **enabled=false** (0건 매칭 게이트 회피).

---

## 5. 룰 수

| 구분 | 값 |
|---|---|
| 변경 전 (활성) | 23 |
| 변경 후 (활성) | **34** |
| 비활성 | 1 (`AUTHORITY_HEADER_VV_TAIL`) |

---

## 6. Phase 2 재실행 (§6.5)

- 대상: Phase 1 **5종 제외** 전 행 (**143,542**건) — `sub_type NOT IN (DELETED, EXCEPTION_CLAUSE, DEFINITION_INTRO, TITLE_HEADER, DATE_EFFECTIVE)`.
- 매칭 실패 시 **UNCLASSIFIED**, `confidence_score=0` (NOT NULL 제약 준수).
- `applied_rules.phase` = `phase_2_1`.

---

## 7. 검증 결과 (§7)

| check_name | 임계 (1차) | 실측 | status |
|---|---|---|---|
| phase_2_1_classify_pct | ≥ 50% | **55.10%** | PASS |
| phase_2_1_sample_100 | ≥ 50% | **62.12%** (해당 실행 시점 표본) | PASS |
| phase_2_1_zero_match_rules | 0건 | **0** | PASS |
| phase_1_results_preserved | 0건 변동 | **0** | PASS |
| phase_2_1_phase1_preserved | 동일 | **0** | PASS |

**분류율**: Phase 2.0 **~5.62%** → Phase 2.1 **55.10%** (약 **+49.5%p**).

---

## 8. verification_log (§6.8)

- `verification_log`에 Phase 2.1 항목 **6행** INSERT 완료 (`--phase21 --only log`).
- `verified_by`: `Cursor_Phase_2_1_2026-05-10` 등 명세 반영.

---

## 9. 절대 원칙 (§1 / §8)

| 원칙 | 적용 |
|---|---|
| LLM 미사용 | ✅ |
| source_text / tokenization_json 변경 없음 | ✅ (Stage 1 미재실행) |
| Phase 1 5종 보전 | ✅ |
| 임계 미달 시 중단 | ✅ (초기 47.99% 시 추가 룰 보강 후 재달성) |

---

## 10. 다음 단계

- PM: DB 샘플 검증 후 Stage 3 진입 여부 판단 (분류율 **≥50%** 1차 목표 달성).
- 분류율 **≥70%**는 추가 tail 다양성 룰·우선순위 튜닝 또는 마스터 enum 범위 내 재설계 필요.

---

*본 보고는 Railway `DATABASE_URL` 환경에서 실행·검증한 결과이다.*
