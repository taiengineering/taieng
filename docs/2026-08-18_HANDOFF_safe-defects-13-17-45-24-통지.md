# HANDOFF — safe 결함 §13·§17·§45·§24 + 스토리지 경고 통지 (→ 헬프센터 창)

> 작성 2026-08-18 · 수신 **헬프센터 창**(LEDGER `tai-helpcenter_LEDGER_safe-defects.md` 소유)
> 성격 **통지** — 이 세션에서 처리/발견한 서버 결함. 이 문서로 LEDGER 갱신을 요청한다.
> ⚠ LEDGER 규칙: **danger·warn 은 배포 SUCCESS(코드) + 라이브 확인** 둘 다일 때만 지운다. §2 확인 후 반영.
> 앞선 통지 2건과 별개: `2026-08-18_HANDOFF_worker-app-defects-75-76-77-79-처리결과.md`(75~79),
> `2026-08-18_HANDOFF_safe-defects-32-66-67-통지.md`(§32·§66·§67). 그 건들은 각 문서 참조.

---

## 0. 한눈에

| 결함 | 상태 | main | 조치 |
|---|---|---|---|
| **§17** 서식 목록 항상 빈칸 | **병합·배포** | `7b99a57` | 라이브 확인 후 danger 삭제 |
| **§45** 교육설정 조회 500 | **병합·배포** | `215ee2e` | 라이브 확인 후 danger 삭제(§2 별건) |
| **§13** 사업자등록증 거짓 성공 | **병합·배포** + 버킷 신설 | `ea534b7` | 라이브 확인 후 danger 삭제 |
| **§24** 담당자 목록 422 | **이미 해소(재점검 발견)** | users v2.3.0 | 라이브 확인 후 삭제 |
| **스토리지 경고** `tai-files` 버킷 부재 | **신규 발견 · 별건** | — | education 업로드 영향, 조치 필요 |

---

## 1. 결함별 상세

### §17 — 서식 목록이 언제나 비어 있다 【병합 `7b99a57`】
- `GET /document-forms`(`list_forms`)가 `list_document_forms()` 결과(`{items,total,page,per_page}`)를 **봉투 없이** 반환 → 화면 `unwrapFormList`가 `resp.data.items`를 못 찾아 항상 `[]` → "등록된 서식이 없습니다"(서식 건수 무관).
- 수정: 목록 라우터를 `{"status":"success","data": …}` 로 감쌈(다른 라우터 관례와 통일). stats·detail은 화면 계약 미확인이라 범위 밖.
- **라이브 확인**: 서식 목록에 실제 서식이 뜨는지.

### §45 — 교육설정 조회가 500, 화면은 "없음"으로 오표시 【병합 `215ee2e`】
- `education.py`가 `education_master...order("sort_order")` 3곳 호출 — **DB에 `sort_order` 컬럼이 없다**(실측 26컬럼 확인) → 쿼리 실패 500 → ①(res.ok 미검사)로 빈 배열 → "등록된 교육이 없습니다".
- 수정: `order("sort_order")` → `order("education_code")`(존재 안정 키). 대상: `/education-master`, `/education/company-settings`, `/education-settings/{factory_id}`.
- **⚠ §2 별건 미해소**: 같은 파일이 읽는 `min_hours`·`cycle_trigger_code`·`cycle_unit_code`·`cycle_status_code`도 실제 컬럼명과 다르다(→ `required_hours`·`trigger_event`·`hours_unit`·`hours_status`). **500은 사라져 목록은 뜨지만 시간·주기 열은 여전히 공백**이다. 교육 계열 계약(§2) 범위라 별도 처리 필요.
- **라이브 확인**: 교육설정 화면이 500 없이 마스터 목록을 표시하는지(시간·주기 열 공백은 §2로 남김).

### §13 — 사업자등록증 업로드 거짓 성공 【병합 `ea534b7` + 버킷 신설】
- 화면이 `POST /companies/{id}/upload-file`(multipart)을 부르는데 서버에 없어 404 → `res.ok` 미검사로 `'uploaded'` 폴백 → "업로드됐습니다" 거짓 성공, **파일은 없었다.**
- 수정: `POST /companies/{id}/upload-file` 신설(UploadFile, 10MB·PDF/JPG/PNG 검증). **비공개 버킷 `company-files` 신규 생성**(사업자등록증=민감문서). 비공개라 public URL 대신 **signed URL(1년)** 발급, `data.url` 반환. `company_files` 실측 컬럼에 메타 저장.
- **한계**: signed URL 1년 만료(장기 재발급용 다운로드 엔드포인트는 별건). 인증 게이팅 미적용(companies 라우터 관례).
- **라이브 확인(중요·파일 저장이라 필수)**: 실제 업로드 시 200인지, 목록/미리보기에서 파일에 접근되는지(signed URL 실동작), company_files 에 행이 남는지.

### §24 — 담당자 목록이 비어 배정이 막힌다 【이미 해소 · 재점검 발견】
- LEDGER 스냅샷은 미해결이나, **users.py v2.3.0에서 이미 목록 size 상한을 `le=100`→`le=500`으로 올렸다**(헤더에 "LEDGER §68" 명시). 화면 `GET /users?size=200`이 통과 → 담당자 열·배정 셀렉트가 찬다.
- **라이브 확인**: 대시보드 담당자 배정에서 사람 목록이 뜨는지.

---

## 2. ⚠ 스토리지 경고 (신규 발견 · 별건)

§13 처리 중 실측: **`tai-files` 버킷이 존재하지 않는다.** 그런데 `routers/education.py`의 증빙 업로드(`upload_education_file`)가 `supabase.storage.from_("tai-files")...`를 호출한다. → **교육 증빙서류 업로드도 런타임에 실패할 가능성이 높다**(교육 이수증 첨부 화면).

- 현재 버킷 목록(실측): 45cm, app, company-docs, company-logo, company-files(신설), contracts, diagrams, expert-documents, facility-drawings, final-reports, form-originals, form-outputs, form-templates, help-media, inspection-images, inspections, law-attachments, mail-attachments, proposals, site-assets.
- **조치 필요(별건)**: education 업로드 버킷을 실재하는 것(예: `expert-documents` 또는 신규)으로 교체하거나 `tai-files` 버킷을 생성. LEDGER에 신규 항목으로 추가 권장(등급: 교육 증빙 첨부가 막히면 높음).

---

## 3. 라이브 확인 체크리스트 (danger/warn 삭제 전제)

- [ ] **§17**: 서식 목록에 실제 서식 표시
- [ ] **§45**: 교육설정 화면이 500 없이 마스터 목록 표시(시간·주기 열 공백은 §2로 남김)
- [ ] **§13**: 사업자등록증 업로드 200 + 파일 접근(signed URL) + company_files 행 생성
- [ ] **§24**: 담당자 배정 셀렉트에 인원 표시
- [ ] **스토리지 경고**: 교육 증빙 업로드가 실제로 되는지(별건 확인)

---

## 4. 검증 한계 (정직 고지)

- §17·§45·§24: 라우터·서비스·DB 실측. HTTP 실동작 미확인(네트워크 차단 환경).
- §13: `ast.parse` 통과. signed URL 반환 형태는 supabase-py 버전차 대비 폴백 처리했으나 **실제 발급·접근은 라이브 확인 필요**. 버킷 `company-files`는 생성 확인.
- 모든 건 §3 체크가 통과되어야 LEDGER 반영 가능.

---

## 5. 요청

1. §3 체크리스트대로 라이브 확인.
2. 확인된 건만 LEDGER 갱신(§17·§45·§13 danger, §24).
3. **§2**(교육 계열 값 불일치)와 **스토리지 경고**(tai-files 부재)는 **신규/잔여 항목으로 LEDGER에 남길 것** — 이번 세션에서 해소되지 않았다.
