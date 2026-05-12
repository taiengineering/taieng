# TAI API 백엔드 작업내역 및 이슈 기록
> 레포: `taiengineering/tai-api` | 스택: FastAPI + Python 3.13 + Supabase + Railway

---

## 📦 커밋 히스토리 요약

| 버전 | 커밋 | 작업 내용 |
|---|---|---|
| v5.12.0 | `db238bb` | 본인인증(이니시스 간편인증) 라우터 신규 생성 |
| v5.12.1 | `64e57d6` | 전문가 등록 DB/API 수정 (entity_type, work_types) |
| v5.13.0 | `488fc55` | 전문가 등록 전체 데이터 적재 재설계 (v2.0.0) |
| v5.13.1 | `3bb5d4e` | 전문가 서류 업로드 Storage 연동 |
| v5.13.2 | `015f12d` | 전문가 통합 목록 + 활성 토글 엔드포인트 |
| v5.14.0 | `81515c3` | 전문가 매칭 라우터 신규 생성 |
| v5.15.0 | `127e9db` | VBANK(가상계좌) 결제 구조 완성 |
| v5.15.1 | `87c3ca5` | 제안서 시스템 전체 구현 (7개 엔드포인트) |
| v5.16.0 | `c9c6d9f` | 계약서 엔진 (Claude API + Storage + 이니시스 서명) |
| v5.17.0 | `19a9969` | 정산 시스템 (9개 엔드포인트) |
| v5.18.0 | `667392b` | 대시보드 + 파이프라인 + price-commission CRUD |
| fix | `7387c7d` | `/experts/admin/list` select 필드 누락 보완 |

---

## ✅ 작업 상세

### 1. 본인인증 — `routers/identity.py` (v5.12.0)

**신규 파일 생성**

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/identity/status` | 본인인증 상태 조회 |
| POST | `/identity/prepare` | 이니시스 팝업 파라미터 생성 (플레이스홀더) |
| POST | `/identity/callback` | 이니시스 콜백 처리 / CI·DI 저장 |
| GET | `/identity/admin/list` | 어드민 인증 현황 목록 |

**DB 마이그레이션** (`sql/identity_verification.sql`)
- `users` 테이블: `identity_ci`, `identity_di`, `identity_name`, `identity_birth`, `identity_gender`, `identity_nation`, `identity_phone`, `identity_carrier`, `identity_method`, `identity_verified`, `identity_verified_at` 컬럼 추가
- `identity_logs` 테이블 신규 생성
- `system_codes`: `identity_method` (PHONE/KAKAO/PASS), `identity_carrier` (SKT/KT/LGU+ 등) 등록

**⚠️ 이슈 / 미완료**
- 이니시스 간편인증 API 키 미수령 → `/prepare` 엔드포인트 현재 503 반환
- Railway 환경변수 등록 필요: `INICIS_VERIFY_MID`, `INICIS_VERIFY_SITE_CD`, `INICIS_VERIFY_SITE_KEY`

---

### 2. 전문가 등록 — `routers/experts.py` (v5.12.1 → v5.13.2)

**expert_type 체계 전환**
```
기존: safety / fix / consult
변경: EXPERT(선임대행) / CONSULTING(컨설팅) / REPAIR(수선중개)
```

**허용 매트릭스 (확정)**
| expert_type | INDIVIDUAL | SOLE_PROPRIETOR | SIMPLIFIED_TAX | CORPORATION |
|---|:---:|:---:|:---:|:---:|
| EXPERT | ✅ | ✅ | ✅ | ✅ |
| CONSULTING | ✅ | ✅ | ✅ | ✅ |
| REPAIR | ❌ | ✅ | ✅ | ✅ |

**엔드포인트 목록**
| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/experts/verify-biz` | 국세청 사업자번호 검증 |
| POST | `/experts/apply` | 신청 접수 (전체 필드) |
| GET | `/experts/my-status` | 내 신청 현황 |
| GET | `/experts/admin/list` | 어드민 목록 |
| GET | `/experts/admin/expert-list` | 승인된 전문가 통합 목록 (v_expert_list 뷰) |
| PATCH | `/experts/admin/{id}/approve` | 승인 + 활성 테이블 자동 적재 |
| PATCH | `/experts/admin/{id}/reject` | 반려 |
| POST | `/experts/upload-url` | 서류 Signed Upload URL 발급 |
| POST | `/experts/attach` | 서류 attachments 등록 |
| GET | `/experts/admin/{id}/documents` | 서류 목록 + Signed 뷰 URL |
| PATCH | `/experts/admin/expert/{source_table}/{id}/toggle` | 활성/비활성 토글 |

**활성 테이블 자동 적재 (_activate_expert)**
```
EXPERT/CONSULTING + CORPORATION → safety_agencies
EXPERT/CONSULTING + 그 외       → safety_personnel
REPAIR                          → repair_companies
```

**DB 마이그레이션** (`sql/20260412_expert_full_migration.sql`)
- `expert_applications`: 36개 컬럼 추가 (사업자·자격증·인허가·검토·동의)
- `safety_personnel`, `safety_agencies`, `repair_companies`: `user_id`, `application_id` 연결 컬럼 + 인덱스
- `system_codes` 6개 카테고리 등록 (expert_type, entity_type, work_type, employment_type, safety_license_type, repair_license_type)
- Storage 버킷: `expert-documents` (비공개, 20MB)

**⚠️ 이슈 / 미완료**
- 국세청 API 키 미등록 → `/verify-biz` 현재 503 반환
- Railway 환경변수 등록 필요: `NTS_API_KEY`
- `v_expert_list` 뷰: Supabase에서 직접 생성 완료 (SQL 별도 실행)

---

### 3. 매칭 시스템 — `routers/matching.py` (v5.14.0 → v1.2.0)

**상태 파이프라인**
```
RECEIVED → MATCHING → PROPOSED → SELECTED
→ CONTRACTING → CONTRACTED → IN_PROGRESS
→ CONFIRMING → SETTLED → CLOSED
예외: CANCELLED / FAILED / DROPPED
```

**엔드포인트 목록 (총 15개)**
| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/matching/requests` | 매칭 신청 접수 |
| GET | `/matching/requests` | 어드민 신청 목록 |
| GET | `/matching/requests/my` | 내 신청 목록 |
| GET | `/matching/requests/{id}` | 신청 상세 + results + contract |
| PATCH | `/matching/requests/{id}/status` | 상태 변경 (전이 규칙 검증) |
| GET | `/matching/admin/stats` | 기본 통계 |
| GET | `/matching/admin/dashboard` | 전체 대시보드 통계 |
| GET | `/matching/admin/pipeline` | 진행 중 파이프라인 목록 |
| POST | `/matching/results/match` | 어드민 전문가 배정 |
| POST | `/matching/results/{id}/notify` | 전문가 알림 발송 |
| POST | `/matching/results/{id}/view` | 신청 열람 처리 |
| POST | `/matching/results/{id}/propose` | 제안서 발송 |
| GET | `/matching/requests/{id}/proposals` | 제안서 목록 |
| POST | `/matching/results/{id}/select` | 전문가 선택 확정 |
| GET | `/matching/my-proposals` | 전문가 내 제안서 목록 |

---

### 4. VBANK 결제 — `routers/payment.py` (v3.1.0 → v3.2.0)

**신규 엔드포인트 3개**
| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/payments/vbank/prepare` | 가상계좌 발급 |
| POST | `/payments/vbank/noti` | 이니시스 입금 확인 웹훅 |
| GET | `/payments/{id}/vbank-status` | 입금 대기 현황 조회 |

**자동 처리 흐름 (입금 확인 시)**
```
이니시스 → POST /vbank/noti
  ├─ payments            PENDING → SUCCESS
  ├─ matching_contracts  paid_confirmed_at / status: ACTIVE
  ├─ matching_requests   CONTRACTED → IN_PROGRESS (자동 전이)
  └─ notifications       신청자 알림 발송
```

**⚠️ 이슈 / 미완료**
- 이니시스 카드심사 완료 후 실제 가동 예정
- 이니시스 설정에 노티 URL 등록 필요
  - 카드: `https://api.taieng.co.kr/payments/inicis/noti`
  - VBANK: `https://api.taieng.co.kr/payments/vbank/noti` ← **신규 등록 필요**

---

### 5. 계약서 엔진 — `routers/contracts_engine.py` (v5.16.0)

**신규 파일 생성** | prefix: `/matching/contracts`

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/matching/contracts/generate` | Claude API로 계약서 HTML 생성 |
| GET | `/matching/contracts/{id}/view` | 계약서 웹뷰 (인쇄→PDF 버튼 포함) |
| PATCH | `/matching/contracts/{id}/revise` | 수정 요청 (최대 3회) |
| POST | `/matching/contracts/{id}/sign/prepare` | 이니시스 서명 준비 |
| POST | `/matching/contracts/{id}/sign/complete` | 서명 완료 콜백 |
| GET | `/matching/contracts/{id}` | 메타 정보 조회 |

**Claude API 호출 패턴**
- `httpx` 직접 호출 (기존 법령엔진과 동일, `anthropic` SDK 불사용)
- 모델: `claude-sonnet-4-20250514`
- API 키 미설정 시 `_default_sections()` 기본 조항 반환
- Storage 버킷: `contracts` (비공개, 50MB)

**서명 완료 → 자동 처리**
```
양측 서명 완료
  → matching_contracts: SIGNED
  → matching_requests:  CONTRACTED
  → 양측 🎉 알림
```

**수정 횟수 초과 처리**
- 3회 이내: Claude API로 수정 반영 후 새 버전 Storage 저장
- 4회 이상: `status = ADMIN_HOLD` → 어드민 개입 필요

**⚠️ 이슈 / 미완료**
- 이니시스 간편인증 서명 (sign/prepare) → API 키 수령 후 실제 구현
- Railway 환경변수: `ANTHROPIC_API_KEY` (기존 법령엔진용 키 재사용 가능)

---

### 6. 정산 시스템 — `routers/settlements.py` (v5.17.0 → v1.1.0)

**신규 파일 생성** | prefix: `/settlements`

| 메서드 | 경로 | 설명 | 권한 |
|---|---|---|---|
| POST | `/settlements/final-report` | 최종 리포트 등록 | 전문가 본인 |
| POST | `/settlements/final-report-url` | Signed Upload URL 발급 | 전문가 본인 |
| GET | `/settlements/final-report/{id}/view` | Signed 뷰 URL (24h) | 당사자/어드민 |
| POST | `/settlements/client-confirm` | 서비스 완료 최종 확인 | 신청자 본인 |
| GET | `/settlements` | 정산 목록 | 어드민 |
| GET | `/settlements/{id}` | 정산 상세 | 어드민 |
| PATCH | `/settlements/{id}/process` | 계좌 입력 → PROCESSING | 어드민 |
| PATCH | `/settlements/{id}/complete` | 이체 완료 → PAID | 어드민 |
| PATCH | `/settlements/{id}/hold` | 보류 처리 | 어드민 |
| GET | `/settlements/withholding` | 원천세 신고 목록 | 어드민 |
| PATCH | `/settlements/withholding/mark-reported` | 신고 완료 일괄 처리 | 어드민 |

**entity_type별 세금 처리**
```
INDIVIDUAL      → WITHHOLDING  (원천세 3.3% 공제)
SIMPLIFIED_TAX  → CASH_RECEIPT (현금영수증)
SOLE_PROPRIETOR → INVOICE      (세금계산서)
CORPORATION     → INVOICE      (세금계산서)
```

**전체 파이프라인 종결**
```
IN_PROGRESS
  →(전문가) /final-report-url + /final-report → CONFIRMING
  →(신청자) /client-confirm                  → SETTLED + settlements 자동 생성
  →(어드민) /{id}/process                    → PROCESSING
  →(어드민) /{id}/complete                   → PAID
                                              → matching_requests CLOSED ← 종결
```

---

### 7. 수수료 설정 — `commission_router` in `matching.py` (v5.18.0)

**prefix: `/price-commission`**

| 메서드 | 경로 | 설명 | 인증 |
|---|---|---|---|
| GET | `/price-commission` | 수수료율 목록 | 어드민 |
| POST | `/price-commission` | 수수료율 등록 | 어드민 |
| POST | `/price-commission/calculate` | 수수료 미리 계산 | **불필요** |
| PATCH | `/price-commission/{id}` | 수수료율 수정 | 어드민 |
| DELETE | `/price-commission/{id}` | 비활성화 (소프트 삭제) | 어드민 |

---

## 🗄️ 생성된 SQL 마이그레이션 파일

| 파일명 | 내용 |
|---|---|
| `sql/identity_verification.sql` | users 컬럼 추가, identity_logs 생성, system_codes 등록 |
| `sql/20260412_expert_work_types.sql` | employment_type, work_type system_codes (중간 단계) |
| `sql/20260412_expert_full_migration.sql` | expert_applications 전체 컬럼 + 활성 테이블 + system_codes |

---

## ⚠️ 미완료 항목 (이니시스 키 수령 후)

| 항목 | 파일 | 상태 |
|---|---|---|
| 이니시스 본인인증 `/identity/prepare` | `routers/identity.py` | 구조만 완성, 실제 서명 로직 미구현 |
| 이니시스 계약서 서명 `/contracts/{id}/sign/prepare` | `routers/contracts_engine.py` | 구조만 완성 |
| 이니시스 VBANK 실가동 | `routers/payment.py` | 카드심사 완료 후 가동 |
| 이니시스 VBANK 노티 URL 등록 | 이니시스 설정 | `https://api.taieng.co.kr/payments/vbank/noti` |

---

## ⚠️ Railway 환경변수 등록 필요

| 변수명 | 용도 | 상태 |
|---|---|---|
| `INICIS_VERIFY_MID` | 본인인증 MID | 🔜 이니시스 수령 후 |
| `INICIS_VERIFY_SITE_CD` | 본인인증 사이트코드 | 🔜 이니시스 수령 후 |
| `INICIS_VERIFY_SITE_KEY` | 본인인증 사이트키 | 🔜 이니시스 수령 후 |
| `NTS_API_KEY` | 국세청 사업자번호 검증 | 🔜 data.go.kr 신청 후 |
| `ANTHROPIC_API_KEY` | 계약서 생성 Claude API | ✅ 기존 법령엔진용 재사용 |

---

## 📌 절대 규칙 (전 파일 공통 적용)

```
1. prefix 이중 등록 금지 → router에 prefix 없음, main.py에서만 지정
2. 환경변수 하드코딩 금지 → os.getenv() 사용
3. DB 직접 수정 금지 → supabase-py 클라이언트 사용
```

**API 응답 표준 구조**
```python
# 목록
{"status": "success", "data": {"items": [...], "total": 100, "page": 1, "size": 20}}
# 단건
{"status": "success", "data": {...}}
# 에러
raise HTTPException(status_code=400, detail="오류 메시지")
```
