---

class: plans
type: RUNBOOK
scope: ops
project: tai-admin-ops
title: 사람 게이트 실행 런북 (P1·P2 누적)
version: 1
status: ACTIVE
owner: taiwang
---

# 사람 게이트 실행 런북 — P1·P2 누적

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **대상:** 코드는 전부 배포됨. 아래는 외부 계정·인증서·env 설정 등 사람만 할 수 있는 작업.
- **우선순위:** A(개통 필수) → B(첫 결제 시) → C(데이터 위생) → D(프론트 연결)

---

## A-1. Gmail 실연동 (최우선 — WO-8·10·12 동시 개통)

**왜:** 이거 하나로 문의 수신·자동응답·발송·연동관제가 전부 실가동.

### 단계
1. **GCP 프로젝트** — console.cloud.google.com → 프로젝트 생성(또는 기존 선택).
2. **Gmail API 켜기** — API 및 서비스 → 라이브러리 → "Gmail API" → 사용.
3. **서비스 계정 생성** — IAM 및 관리자 → 서비스 계정 → 만들기. 이름 예: `tai-mail-sender`. 역할 없이 생성 가능.
4. **JSON 키 발급** — 만든 서비스 계정 → 키 → 키 추가 → JSON → 다운로드(안전 보관).
5. **도메인 전체 위임 켜기** — 서비스 계정 상세 → "Google Workspace 도메인 전체 위임 사용 설정" 체크 → **클라이언트 ID** 복사.
6. **Workspace 관리자 승인** — admin.google.com(슈퍼관리자) → 보안 → API 제어 → 도메인 전체 위임 → 새로 추가:
   - 클라이언트 ID: 위 5번 값
   - 범위: `https://www.googleapis.com/auth/gmail.send`, `https://www.googleapis.com/auth/gmail.readonly`
   - 승인. (반영 최대 ~60분)
7. **Railway 환경변수** — tai-api-prod 서비스 → Variables:
   - `GMAIL_SA_JSON_B64` = (JSON 파일을 base64 인코딩한 값)
   - `GMAIL_SENDER` = `tai@taieng.co.kr`
8. **의존성** — requirements.txt에 `google-api-python-client`, `google-auth` 추가(없으면). Cursor로 편집→push.
9. **검증** — 배포 후 `POST /notify/send`(MAIL)로 자기 메일 발송 테스트, `POST /mail/pull`로 수신 폴링 테스트.

**base64 인코딩 방법:** 터미널에서 `base64 -i 서비스계정.json | tr -d '\n'` (Mac) 또는 온라인 base64 인코더.

---

## A-2. 팝빌 실발행 (세금계산서 — WO-4·15)

1. **가입** — popbill.com 사업자 회원가입.
2. **공동인증서 등록** — 전자세금계산서 발행용 사업자 공동인증서를 팝빌에 등록.
3. **연동 정보 발급** — 팝빌 관리 → 연동회원/API → LinkID, SecretKey 확인.
4. **Railway env**:
   - `POPBILL_LINK_ID`, `POPBILL_SECRET_KEY`
   - `POPBILL_IS_TEST` = `true`(테스트) → 검증 후 `false`
   - `POPBILL_USER_ID`(팝빌 아이디)
   - `TAI_CORP_NUM`(사업자번호), `TAI_CORP_NAME`, `TAI_CEO_NAME`, `TAI_ADDR` 등 공급자 정보
5. **검증** — 테스트 모드로 세금계산서 1건 발행 → 국세청 승인번호 확인 → 운영 전환.

---

## A-3. 연동 probe 활성화 (WO-10)

- Railway env: `API_SELF_URL` = `https://api.taieng.co.kr`
- 설정 후 `POST /integrations/probe`가 내부 API 실제 헬스체크 수행.

---

## B-1. 이니시스 환불 실검증 (WO-1)

- 첫 실결제 발생 후, 그 건으로 환불 1회 실행 → 이니시스 취소 API 응답·정산 반영 확인.
- 실결제 전에는 검증 불가(대기).

---

## C-1. 목업 데이터 위생 정리 (실운영 개시 전)

- 관제홈에 목업 미읽음 수신 179·발송실패 246이 잡힘.
- 실운영 시작 직전, Claude에게 요청 → mail_logs 목업 정리 SQL 실행(read 처리 또는 삭제). 실데이터와 섞이기 전에.

---

## D-1. 공지배너 프론트 연결 (WO-16)

- 마케팅(taieng.co.kr): `GET /notices/active?channel=MARKETING` 호출 → 배너 렌더.
- SaaS(safe.taieng.co.kr): `GET /notices/active?channel=SAFE` 호출 → 배너 렌더.
- 어드민 화면: `/notices` CRUD 연결.

## D-2. 어드민 화면 연결

- 관제홈 `/ops/home`, 경영지표 `/stats/business`, 세무 `/tax/ops`·`/tax/unissued`, 온보딩 `/companies/{id}/onboarding`을 admin 프론트에 연결.

---

## 순서 권고

A-1(Gmail) → A-3(probe env) → C-1(목업정리) 를 먼저. A-2(팝빌)·B-1(환불)은 실결제·실발행 시점에. D는 프론트 작업(P3)과 함께.
