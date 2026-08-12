# TBM 팀·그룹 하이브리드 설계서

- 작성일: 2026-08-11
- 상태: **Phase 1·2 구현·배포 완료(2026-08-11)** · Phase 3(리더 모바일·계정 배선)은 별도 모바일 트랙 인계. → 작업지시서: `docs/tbm/hybrid/WORKORDER_phase3-leader-mobile_v1.md`
- 범위: TBM(Tool Box Meeting)을 실무(반장·팀·소그룹 단위)에 맞게 재설계. 안전관리자 세팅 + 현장 리더 모바일 사용(하이브리드).
- 근거: 내부 DB/라우터 직독 + 외부 실무 조사. 아래 사실은 모두 검증됨.

---

## 0. 문제 진단 (왜 꼬였나)

실무 TBM은 **반장(TBM 리더) 주관 · 팀/소그룹 단위 · 현장 모바일**로 돌아가는데, 현재 시스템은:

1. TBM 생성이 **관리자 웹(safe)에만** 있음 — 리더가 자기 팀 TBM을 만드는 경로 없음.
2. TBM이 **시설(factory) 단위**로만 열림.
3. 팀 개념(`teams` 테이블)은 **테이블만 있고(0행) worker·tbm·리더와 미연결**.
4. 계정·인증·권한 인프라(`users`+RBAC)는 완성도 높은데 **worker와 미연결**(user_id 0건).

→ 즉 "팀/소그룹이라는 실무 현실"을 담을 **배선(worker↔team/group, tbm↔group, 리더 역할·권한, worker↔계정)이 설계만 일부 되고 연결이 안 된 상태**. 본 설계의 핵심은 **끊긴 배선을 잇는 것**.

---

## 1. 외부 조사 (실무 TBM 운영)

- TBM = 작업 전 안전점검회의. **작업팀장(반장)/관리감독자 중심**으로 진행.
- **소단위(5~7명) 팀별**로 아침 작업 전 10분 내외. → 큰 팀은 그룹으로 나눠 진행.
- 안전관리자는 **틀(위험성평가·절차·템플릿)** 제공, 반장이 팀 단위로 **운영**.
- 근거: 중대재해 감축 로드맵 → 위험성평가 결과를 TBM으로 반복 전달·교육.

---

## 2. 내부 조사 (검증된 팩트)

### 2-1. TBM 관련 테이블
- `tbm_meetings`: 스코핑 = `factory_id` + `construction_site_id`. **team 참조 없음**. (qr_token/qr_expires_at 있음 — 현장 서명용)
- `tbm_attendees`: 개인 단위(worker_id/user_id/name/서명). team 참조 없음.
- `tbm_templates`: factory_id만(v1.1.1에서 시설 스코핑 적용됨). team 없음.

### 2-2. 팀
- `teams`: {id, **factory_id**, team_name, team_code, description, is_active}. 시설 스코핑. **0행(미사용)**.
- `users.team_id` 있음(계정↔팀). `worker_registry`에는 **team_id 없음**.

### 2-3. 근로자 등록 (`worker_registry`, 10명)
- 수동등록 스키마에 `department`(부서) **있음(선택)**. 그러나:
  - **엑셀 일괄등록엔 부서 칸 없음**(이름·연락선·직종·소속업체·입사일).
  - 실제 DB: 부서 입력 **0명**. 자유텍스트이며 teams와 무관.
- 직종코드에 **WJT016 관리감독자(반장)** 있음 → 리더 식별 수단은 있으나 역할·권한 미연결.
- TBM 생성은 관리자 웹(tbm-setting)에만. 작업자 앱(/app/tbm.html)은 서명만.

### 2-4. 계정·인증·권한 (`users`, 22행) — 인프라 완전 존재
- 조직: company_id · factory_id · **team_id** · department · position · role_id/role_code · sector
- 인증: username/password_hash · **소셜(kakao/naver/google)** · **생체(biometric_*)** · **본인인증(identity_ci/di/PASS)** · email_verified
- 모바일·서명: push_token/platform · **signature_url** · allow_push/sms
- RBAC: `roles` · `role_permissions` · `role_menu_permissions` · `role_site_permissions` · **`role_data_scope`** · `rule_pos_to_role`
- 미배선: `worker_registry.user_id` **0건**, `app_installed` **0건**. worker↔계정 연결·초대→계정생성만 없음(`send_invite`는 invite_sent_at만).

→ **결론**: TBM 리더 모바일은 새 인증을 만들 필요 없이 worker↔users 연결 + role_code + role_data_scope(자기 팀/그룹) + 기존 소셜/생체 로그인으로 성립. **배선만**.

---

## 3. 설계 결정 (사용자 확정)

1. **하이브리드**: 안전관리자=세팅 주체, 리더=주 사용자+자기 팀 세팅도 가능. 둘 다 TBM 생성(스코프 다름).
2. **조직 계층**: 회사 > 시설 > 부서 > 팀 > **그룹** > 근로자.
3. **3섹터 모두**(산업·건물·건설) 지원. "시설"=factory_id(산업·건물) 또는 construction_site_id(건설) XOR.
4. **다중소속**: 1근로자 → N그룹.
5. **팀 리더 1명 강제**. 그룹 조장은 그룹당 1명(옵션).
6. **용어**: 반장 → **"TBM 리더"**.

---

## 4. 조직 계층 모델

```
회사(company)
 └ 시설(factory[산업·건물] | construction_site[건설])
    └ 부서(department)
       └ 팀(team)              ← 팀 리더 1명 강제
          └ 그룹(group)         ← TBM 실제 단위(소단위 5~7명), 조장(옵션)
             └ 근로자(worker)   ← 다중소속(N그룹)
```
· 예: 생산1팀 100명 → 그룹 다수로 분할, 각 그룹이 TBM 단위.

---

## 5. 데이터 모델 델타 (DDL — 적용·검증 완료)

### 신설 `departments`
```
departments(
  id uuid PK,
  company_id uuid NOT NULL,
  factory_id uuid NULL,
  construction_site_id uuid NULL,
  department_name text NOT NULL,
  department_code text,
  is_active bool DEFAULT true,
  created_at, created_by, updated_at, updated_by,
  CHECK (num_nonnulls(factory_id, construction_site_id) = 1)  -- 시설 귀속 XOR
)
```

### 확장 `teams` (기존 0행 활성화)
```
+ department_id uuid FK departments        -- 계층 부모
+ construction_site_id uuid NULL           -- 건설 팀(기존 factory_id와 XOR)
+ lead_worker_id uuid FK worker_registry   -- 팀 리더(TBM 리더) 1명 강제
```

### 신설 `groups`
```
groups(
  id uuid PK,
  company_id uuid,
  team_id uuid NOT NULL FK teams,               -- 그룹은 팀에 소속
  group_name text NOT NULL,
  group_code text,
  lead_worker_id uuid NULL FK worker_registry,  -- 조장(그룹 TBM 진행, 옵션 1명)
  is_active bool DEFAULT true,
  created_at, updated_at
)
```

### 신설 `worker_group` (다중소속 leaf)
```
worker_group(
  id uuid PK,
  worker_id uuid FK worker_registry,
  group_id uuid FK groups,
  is_lead bool DEFAULT false,   -- 이 그룹의 조장
  assigned_at timestamptz,
  UNIQUE(worker_id, group_id)
)
```
· 1근로자 N그룹. 팀/부서/시설/회사는 group→team→dept→facility로 유도.

### 확장 `tbm_meetings`
```
+ group_id uuid NULL FK groups   -- TBM 주 단위
+ team_id  uuid NULL FK teams    -- 부모(유도/비정규화)
```

### 확장 `tbm_templates`
```
+ team_id uuid NULL   -- 팀 템플릿. 스코프 = 전역(null)/시설(factory|site)/팀(team_id)
```

### worker↔계정 (Phase 3)
```
worker_registry.user_id → users.id 활성화 + 초대 시 계정 생성/연결.  (Phase 3 인계)
```

---

## 6. 역할·권한

| 역할 | 식별 | 서피스 | 세팅 | TBM |
|---|---|---|---|---|
| 안전관리자 | 관리자 users 계정 | 웹(safe) | 부서·팀·그룹 편성, 근로자 다중배정, 리더·조장 지정, 템플릿 | 전 팀 생성·조회 |
| **TBM 리더** | worker(WJT016) + teams.lead_worker_id + users 계정 | **모바일**(+웹) | 자기 팀 템플릿 선택+생성 | **자기 팀/그룹** 생성·실행·서명관리 |
| 조장 | worker_group.is_lead + users 계정 | 모바일 | — | 자기 그룹 TBM 진행 |
| 작업자 | worker | 모바일 | — | 서명 |

· 권한 = 기존 RBAC(`roles`/`role_permissions`/**`role_data_scope`**)에 **팀/그룹 스코프** 규칙 추가(리더=자기 team_id/group_id 한정). *(Phase 3)*

---

## 7. TBM 플로우 (팀/그룹 기반)

```
[세팅·안전관리자·웹]
 부서·팀·그룹 편성 → 근로자 다중배정 → 팀리더·조장 지정 (+팀 템플릿)
        │
[실행·TBM 리더/조장·모바일]
 내 그룹 선택 → 템플릿 선택/생성 → 그룹원 자동 소집(default 참석자) → TBM 생성(DRAFT)
        │
[현장·그룹원·모바일]
 QR/푸시 서명 → 리더가 미서명 추적 → 완료
```
· `tbm_meetings.group_id`로 그룹 단위 개설·집계, 참석자 = 그룹원 자동 + 추가.
· 현장 서명은 기존 `qr_token`/푸시(`sign_requested_at`) 재사용.

---

## 8. 단계적 도입 (리스크 낮은 순)

- **Phase 1 — 조직 골격(웹)** ✅ **완료·배포(2026-08-11)**: `departments` 신설 + `teams` 확장 + `groups` 신설 + `worker_group`(다중소속) + 관리자 "조직/팀/그룹 편성 + 다중배정 + 팀리더·조장 지정" UI(org-setting). 근로자 수정 패널에 부서·팀·그룹·재직상태·시설·메모. 건설현장 시설 피커 포함.
- **Phase 2 — TBM 그룹화(웹)** ✅ **완료·배포(2026-08-11)**: `tbm_meetings.group_id/team_id` + 그룹 선택→**그룹원 자동 소집**(worker_id 연결). TBM 목록/상세 팀·그룹 표시. `tbm_templates.team_id` 팀 템플릿 스코핑(전역/시설/팀).
- **Phase 3 — 리더 모바일 + 계정 배선** → **별도 모바일 트랙 인계(작업지시서 발행)**: worker↔users 연결 + 초대→계정생성(MessageMi) + role_data_scope(팀/그룹) + 앱 리더 뷰(내 그룹 TBM 생성·실행·QR서명·미서명추적). → 하이브리드 완성. 지시서: `docs/tbm/hybrid/WORKORDER_phase3-leader-mobile_v1.md`.

---

## 9. 미결정 (확정 필요)

1. **템플릿 스코프에 부서 레벨**도 넣을지 — 전역/시설/**부서**/팀 4단 vs 전역/시설/팀 3단. *(현재 3단으로 구현됨. 부서 레벨은 필요 시 추가.)*
2. ~~Phase 3 계정 배선을 이번 범위에 포함할지~~ → **확정: Phase 1·2 웹 먼저 완료, Phase 3 리더 모바일은 별도 트랙(작업지시서 인계).**

---

## 10. 원칙·제약 (기존 아키텍처 준수)

- INSERT `ON CONFLICT DO NOTHING`, CONFIRMED 레코드 무단 수정 금지.
- 사업장/시설 스코핑 우선, 서버측 인증 바인딩은 role_data_scope로(향후 하드닝).
- 법령엔진 불간섭 — 본 설계는 SaaS 운영 영역(엔진 무관).
- 파일 200줄/20KB+는 Cursor/Claude Code 로컬 편집.

---

## 11. 후속 작업 (2026-08-12) — worker 인물 단일 원장 + worker-list org 배선

Phase 1·2 이후, 팀·그룹 모델을 실제 운영/데이터에 정착시키며 파생된 후속 작업.

### 11-1. worker 인물 단일 원장 확립 (이중 테이블 정리)
- **문제**: 건설 인원이 두 테이블에 병존.
  - `construction_workers` = 건설 전용 로스터(출역·PTW·보건검진·서명·하도급).
  - `worker_registry` = **조직·TBM·알림 인물 원장**. 부서/팀/그룹(`worker_group`)·`teams/groups.lead_worker_id`·`tbm_attendees.worker_id`가 모두 이 테이블을 참조(§5). 그러나 둘 사이 연결 컬럼이 없어 **동일 인물을 이중 관리**.
- **결정**: `worker_registry` = 인물 단일 원장, `construction_workers` = 그 사람의 **건설 확장 속성**(1:1 링크). (조직/TBM/알림 식별은 이미 worker_registry 기준이므로 자연스러운 단일화.)
- **구현(적용·검증 완료)**:
  - `construction_workers.worker_registry_id uuid FK worker_registry(id) ON DELETE SET NULL` + 인덱스.
  - DB 트리거 `public.sync_construction_worker_to_registry()`:
    - `trg_sync_cw_registry_ins` (BEFORE INSERT): 건설 작업자 등록 시 worker_registry 행 자동 생성(company=사이트, job_type=role_code/worker_type, contractor_name=하도급/원청직영) + `NEW.worker_registry_id` 세팅.
    - `trg_sync_cw_registry_upd` (BEFORE UPDATE OF worker_name/worker_phone/role_code/worker_type/subcontractor_id/is_active): 이름·연락처·직종·하도급·재직을 연결된 worker_registry 행에 자동 반영.
  - 이름/연락처 null 또는 회사 null이면 스킵(가드). 테스트 삽입→연결 확인→삭제로 검증.
- **효과**: 입력 1회, 사람 관리는 worker_registry 한 곳. 건설 화면(출역·PTW)은 construction_workers, 조직·TBM·알림은 worker_registry — 같은 사람으로 묶여 화면 충돌 없음.
- **참고**: 트리거(=DB 레벨, 모든 등록 경로 커버, 저위험). 앱 코드(등록 라우터)로 옮길지는 선택(요청 시 전환). §2-4의 worker↔**users 계정** 배선(Phase 3)과는 별개 축 — 이 작업은 worker **인물 식별**의 단일화.

### 11-2. worker-list(작업자관리) org 배선 — Phase 1 확장
Phase 1에서 근로자 수정 패널에만 있던 부서·팀·그룹을, **엑셀 일괄등록과 검색**까지 확장(§2-3의 "엑셀에 부서 칸 없음" 해소).
- **백엔드 `routers/worker_registry.py` v1.4.0**:
  - 목록 `GET /worker-registry`에 `department_id/team_id/group_id` 필터 — `worker_group` 멤버십 기준으로 대상 worker id 산출(그룹→직접, 팀→하위 그룹, 부서→하위 팀의 그룹).
  - `bulk-import`에 부서/팀/그룹 컬럼 파싱 → `_resolve_group_id()`(시설 범위에서 이름 캐스케이드 해석) → `worker_group` 배정(대표 1건 교체). 매칭 실패는 `org_failed[]` 리포트.
  - 엑셀 템플릿(`/template`)에 부서/팀/그룹 컬럼 추가.
  - **버그 수정**: 전화번호 헤더 `연락처`/`연락처(필수)` 인식(프론트 템플릿과 정합 — 종전 `연락선`만 읽어 파일 업로드가 실패하던 문제).
- **프론트(tai-admin, worker-list)**:
  - 검색에 시설→부서→팀→그룹 캐스케이드(`useWorkerList`) + `getQuery` org 파라미터.
  - 엑셀 템플릿/미리보기에 부서·팀·그룹(`useWorkerBulkUpload`), '조직안내' 시트.
  - **업로드 에러 하드닝**: 업로드 예외 try/catch(실패 시 모달 유지·재시도), 부분 실패 시 결과 뷰(등록실패/조직미배정/직종기타 상세 표) 유지, 실패 목록 CSV 다운로드.
- **주의**: 엑셀의 부서/팀/그룹은 자유텍스트가 아니라 **등록된 조직명과 정확히 일치**해야 배정(그룹까지 입력 시 배정). worker-list는 시설(factory) 기준이라 해당 시설에 org가 있어야 셀렉트에 표시.

### 11-3. 건설현장 org 경로 검증 (데모)
- §4~5 계층을 **건설(construction_site_id) 경로**에서 실검증: 데모 건설현장에 부서 2·팀 4·그룹 5 + `worker_group` 배정(12명, 팀장·조장 지정), `departments/teams.construction_site_id` 스코프 동작 확인.
- 하도급(`subcontractors`) 3사 배선도 함께: `construction_works/workers.subcontractor_id`는 **`companies`를 참조**(작업자는 companies+subcontractors 이중 FK)하므로, 동일 UUID를 companies(is_demo)+subcontractors 양쪽에 넣어 연결. org(worker_group)와는 **별개 축**(하도급=계약·소속, org=지휘·TBM 단위).

---

## 변경 이력
- 2026-08-11: 초안. 외부/내부 조사 기반 하이브리드 설계. 계층 회사>시설>부서>팀>그룹>근로자, 다중소속, 팀리더 1명강제, TBM리더 용어, 3섹터 지원. 미결정 2건.
- 2026-08-11: **Phase 1·2 구현·배포 완료.** DDL 적용·검증(departments/groups/worker_group + teams·tbm_meetings·tbm_templates 확장, FK 체인 검증). 백엔드 org.py/worker_org.py/tbm.py(팀·그룹 임베드)/tbm_templates.py(그룹 자동소집·팀 스코핑)/worker_registry.py(factory_id·memo). 프론트 org-setting(건설현장 피커 포함)/worker-list(부서·팀·그룹·재직·시설·메모)/tbm-setting(팀 스코핑·그룹 캐스케이드)/tbm-list(팀·그룹 컬럼). nav '조직 관리' 그룹. Phase 3(리더 모바일·계정 배선)은 별도 트랙으로 작업지시서 발행. 미결정 #2 확정.
- 2026-08-12: **후속 작업(§11).** (1) worker 인물 단일 원장 확립 — `construction_workers.worker_registry_id` FK + 동기화 트리거(등록 시 worker_registry 자동 생성·연결, 수정 자동 반영)로 이중 관리 해소. (2) worker-list org 배선(Phase 1 확장) — `worker_registry.py` v1.4.0: 목록 부서/팀/그룹 필터(worker_group), bulk-import 부서/팀/그룹 이름 해석·배정, 엑셀 템플릿 org 컬럼, `연락처` 헤더 인식(업로드 버그 수정). 프론트 검색 캐스케이드·엑셀 org 컬럼·업로드 에러 하드닝(예외 처리·부분실패 상세·실패 CSV). (3) 건설(construction_site) org 경로 데모 검증 + 하도급 3사 배선(subcontractor_id→companies 이중 FK 확인, org와 별개 축).
