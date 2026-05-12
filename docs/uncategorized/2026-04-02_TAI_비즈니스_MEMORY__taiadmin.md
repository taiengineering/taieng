# TAI Safe 개발 세션 메모리 — 2026-04-02

## 오늘 완료된 작업

### 1. 엔진QA 점수체계 변경 (engine_qa.py v1.2.0)
- **변경 전**: 테스트 70점 + DB품질 30점
- **변경 후**: 전체 커버 시 100점, DB이슈 감점 (HIGH -5점, MEDIUM -2점)
- 공식: `total = max(0, test_score - db_deduct)`
- SPF(특수시설) 테스트 케이스 제거
- 현재 테스트 케이스: 3개 섹터(건물·제조·건설) × 정방향·역방향 = 15개

### 2. 선임 의무 중복 제거 (legal_engine.py v5.5.2)
- `_classify_rules_db` 함수에 `seen_appoint_targets` set 추가
- `appointment_target_code` 기준 중복 스킵
- 효과: energy_manager(4→1), fire_safety_manager(3→1) 등

### 3. 특수시설(SPECIAL_FACILITY) 전면 제외 결정
**이유**: 특수시설은 용도(병원·연구실·학교)에 따라 법령이 완전히 다름  
**계획**: 나라장터 등록 후 용도별 법령 체계 구축 시 추가

**DB 처리**:
- `master_building_legal_rules` SPECIAL_FACILITY 49개 → `is_active = false`
- `law_rule_drafts` 전체 삭제 (827개 리셋)
- 법령·조문 데이터(law_master, law_version, law_article)는 보존

**프론트 처리 (engine-legal-ai.html)**:
- `SEC_KR`에서 SPECIAL_FACILITY 및 관련 섹터 전부 제거
- `fSector` 필터에서 특수시설 옵션 제거
- `loadDrafts()`에서 SPECIAL_FACILITY 초안 자동 필터링

**백엔드 처리 (engine_qa.py)**:
- SPF 테스트 케이스 제거
- DB 품질 체크에서 SPECIAL_FACILITY 제외

### 4. AI 룰 생성기 섹터 정리
현재 SEC_KR (특수시설 제외):
```
BUILDING: 건물시설
MANUFACTURING: 제조공장
CONSTRUCTION: 건설현장
COMMON: 공통
CONSTRUCTION_MANUFACTURING: 건설+제조
```

---

## 현재 파일 SHA

| 파일 | 저장소 | SHA |
|------|--------|-----|
| engine-legal-ai.html | tai-admin | e3607615 |
| engine-qa.html | tai-admin | 4518ca45 |
| engine_qa.py | tai-api | 70b8cd0e (HEAD) |
| legal_engine.py | tai-api | 5c068f2c |

---

## 잔여 작업 (다음 세션)

1. **law_rule_generator.py SYSTEM_PROMPT에서 SPECIAL_FACILITY 제거**
   - AI가 파싱 시 특수시설 섹터로 분류하지 않도록
   - 파일: `routers/law_rule_generator.py`

2. **전체 법령 파싱 재실행**
   - 특수시설 빠진 상태에서 AI 파싱 새로 시작
   - 건물·제조·건설 섹터만 대상

3. **engine_qa.py 점수체계 변경 + 중복 제거 관련 엔진관리 페이지 설명 업데이트**
   - 이미 engine-qa.html 수정 완료 (DB이슈 감점 표시)

---

## 핵심 결정 사항

- **특수시설**: 용도별 법령 다름 → 나라장터 등록 전까지 제외, 데이터는 보존
- **선임 중복**: appointment_target_code 기준 dedup → 진단 결과 품질 향상
- **점수체계**: 전체 커버 100점이 더 직관적, DB이슈는 감점 방식
- **Claude Max 사용량**: Project knowledge 파일 전체 삭제로 60~70% 절감
- **Cursor 속도 문제**: Max 한도 공유가 원인 → Cursor에 별도 API 키 연결 필요
