# HANDOFF — 작업자앱/safe 서버 결함 75·76·77·79 처리 결과 (→ 헬프센터 창)

> 작성 2026-08-18 · 수신 **헬프센터 창**(LEDGER `tai-helpcenter_LEDGER_safe-defects.md` 소유)
> 근거 이관 `tai-helpcenter_HANDOFF_app-defects-75-76-77_2026-08-18.md`
> 성격 **처리 결과 통지** — 이 문서로 LEDGER 갱신(danger 삭제) 판단을 요청한다.
> ⚠ LEDGER 규칙: **배포 SUCCESS(코드) + 라이브 확인** 둘 다 있어야 danger 삭제. 현재 **코드 병합까지** 완료, 라이브 확인은 미완(아래 항목 확인 후 갱신).

---

## 0. 한눈에

| 결함 | 내용 | PR | 병합 | 소유 |
|---|---|---|---|---|
| 75 | 앱 교육 화면 `GET /education/{edu_id}` 부재 → 신설 | tai-api #154 | ✅ | 작업자앱 |
| 76 (서버) | 앱 이력 `GET /worker-check/history` 부재 → 신설 | tai-api #153 | ✅ | 작업자앱 |
| 76 (앱) | `history.html` 빈 `catch(e){}` 오류 삼킴 → 오류 표시 | tai-admin #29 | 🔵 대기 | 작업자앱 |
| 77 | 교육이수 저장에 소속(company_id·factory_id) 누락 → 저장 | tai-api #153 | ✅ | 작업자앱 |
| 79 | 건설사 교육이력 조회 불가(factory_id 필수) → 회사 스코프 | tai-api #155 | ✅ | **safe 대장** |

main 최종(tai-api): `ffe6644` · 세 번 병합으로 Railway 자동배포 트리거됨.

---

## 1. 결함별 처리 상세

### 75 — 교육 단건 조회 (tai-api #154, 병합)
- `routers/education_assign.py` 맨 끝에 `GET /education/{edu_id}` 신설. `edu_id`=education_code(worker-complete 와 동일 키)로 `education_master` 단건 조회.
- **라우트 충돌 회피(실측)**: construction 그룹 로드 순서 `education → education_assign` 확인. 동적 `/{edu_id}` 를 education_assign 맨 끝(모든 정적 경로 뒤)에 둬서 `/education/master`·`/company-settings`·`/assignments`·`/company-effective-link` 가 먼저 매칭. 이중 안전으로 예약어는 404.
- 응답 봉투에 `status`·`success` 두 키 병기(앱 파싱 형식 미확정 대비).

### 76 서버 — 이력 조회 (tai-api #153, 병합)
- `routers/worker_check.py` 에 `GET /worker-check/history` 신설. worker_id(=users.id) 우선, 없으면 phone 으로 users→worker_registry 조회 후 `safety_inspections` 이력 반환. `/recent` 와 동일 패턴.

### 76 앱 — 오류 표시 (tai-admin #29, 병합 대기)
- `vue3/public/app/history.html`: `res.ok` 아니면 throw, `catch` 에서 오류 플래그+`console.error`(삼킴 제거). 오류 시 ⚠️ 문구 + 재시도 버튼. `t()` 키 유무와 무관한 한국어 fallback.
- **범위 최소**: 완료율 하드코딩·통계 필터달·PDF WIP 버튼·건설 유형 필터는 AUDIT §5 결정거리라 미포함.

### 77 — 교육이수 소속 저장 (tai-api #153, 병합)
- `routers/worker_assets.py` `worker_complete_education()`: user_id 로 users 조회해 company_id(항상)·factory_id(있으면)를 `education_history` insert row 에 추가. 건설사는 factory_id NULL 이므로 company_id 로 회사 축 조회 가능.

### 79 — 건설사 교육이력 조회 (tai-api #155, 병합) ⚠ safe 대장 소유
- `routers/education.py` `get_education_history()`: factory_id 없으면 P13 회사 스코프(`_forced_company_id`, 토큰 company_id 강제)로 `education_history.company_id` 필터. 건설사(factory 0개)도 자기 회사 이력 조회 가능, 타사 격리 유지.
- **목록만 수정.** 요약(`summary`)은 `status`/`status_code` 어휘 불일치(**LEDGER §2**)와 얽혀 미수정.

---

## 2. 라이브 확인 항목 (헬프센터 창이 danger 삭제 전 확인)

- [ ] `/health` 200 유지(배포 성공)
- [ ] **75**: 앱 교육 화면에서 교육 본문 표시 + `GET /education/master`·`/company-settings`·`/assignments` 가 여전히 정상(가로채이지 않음)
- [ ] **76**: 앱 이력 화면에 이력 표시 + (tai-admin #29 병합 후) 오프라인 시 ⚠️ 오류 문구·재시도 버튼 표시
- [ ] **77**: 작업자앱 교육 이수 완료 → 관리자 화면에 이수 기록 표시(건설사 계정 포함)
- [ ] **79**: 건설사 계정(factory_id 없음)으로 교육이력 조회 시 자기 회사 이력 표시 + **⚠️ 타사 이력이 안 보이는지(격리 회귀 없음)**

---

## 3. 검증 한계 (정직 고지)

- 모든 PR: `ast.parse`/`node --check` 문법 + DB 스키마 실측 + 로컬 재현 **바이트 크기 검증**까지 완료.
- **pytest/HTTP E2E·라우트 매칭 실동작·브라우저 동작은 이 환경(네트워크 차단)에서 미실행.** 위 §2 라이브 확인이 반드시 선행되어야 danger 삭제 가능.

---

## 4. 후속/미포함 (기록)

- **79는 safe 대장 §79 소유** — 운영자 승인으로 작업자앱 창이 처리했으나, LEDGER §79 갱신은 헬프센터 창이 라이브 확인 후 수행.
- **LEDGER §2**(교육이수 status vs status_code 어휘 불일치): 79 요약(summary)이 이와 얽혀 있어 미수정. 별도 처리 필요.
- 76 앱측 부수(완료율 계산·통계 필터·PDF WIP·건설 유형 필터): AUDIT §5 결정거리, 운영자 결정 대기.
- 라이브 확인 완료 시 발행 예정 문서: `GUIDE-app-education`, 앱 이력 문서, `education-list`.
