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

## 진행 상태 (2026-07-29 갱신)

| 항목 | 상태 |
|---|---|
| A-1 Gmail 실연동 | ✅ **완료·검증** — 실발송 성공(sent_by=gmail, gmail/kakao 주소 모두 도달) |
| A-3 probe env(API_SELF_URL) | ✅ 완료 |
| A-2 팝빌 | ⏳ 세금계산서 발행 시점 |
| B-1 이니시스 환불 | ⏳ 첫 실결제 시점 |
| C-1 목업 정리 | ⏳ 실운영 개시 직전 |
| D 프론트 연결 | ⏳ P3 |

> ⚠️ **env 등록 함정(중요):** 이 Railway 프로젝트엔 tai-api와 45cminc/marketing 서비스가 공존한다. 환경변수는 반드시 **tai-api-prod 서비스**에 등록해야 tai-api 앱이 읽는다. 다른 서비스에 넣으면 앱은 못 읽고 조용히 fallback/실패한다. A-1 초기 실패 원인이 이것이었음. 앞으로 A-2(팝빌)·기타 env도 전부 tai-api-prod에 넣을 것.

---

## A-1. Gmail 실연동 (최우선 — WO-8·10·12 동시 개통) ✅ 완료

**왜:** 이거 하나로 문의 수신·자동응답·발송·연동관제가 전부 실가동.

### 단계 (완료 기록)
1. GCP 프로젝트 + Gmail API 사용.
2. 서비스 계정(tai-mkt) + JSON 키.
3. 도메인 전체 위임: 클라이언트 **숫자 ID** + 스코프 `gmail.send`,`gmail.readonly` 전체 URL로 승인.
4. Railway **tai-api-prod**: `GMAIL_SA_JSON`(tai-mkt JSON) + `GMAIL_SENDER=tai@taieng.co.kr`.
5. requirements.txt: `google-api-python-client`, `google-auth`(커밋 0b183a9).
6. **검증:** admin 메일발송 화면에서 실발송 → sent_by=gmail, gmail/kakao 도달 확인.

**메일 발송 경로:** Gmail 우선(`_gmail_enabled()` True) → 실패 시 Resend fallback. sent_by에 provider 기록.

---

## A-2. 팝빌 실발행 (세금계산서 — WO-4·15)

1. **가입** — popbill.com 사업자 회원가입.
2. **공동인증서 등록** — 전자세금계산서 발행용 사업자 공동인증서를 팝빌에 등록.
3. **연동 정보 발급** — 팝빌 관리 → 연동회원/API → LinkID, SecretKey 확인.
4. **Railway env (tai-api-prod에!)**:
   - `POPBILL_LINK_ID`, `POPBILL_SECRET_KEY`
   - `POPBILL_IS_TEST` = `true`(테스트) → 검증 후 `false`
   - `POPBILL_USER_ID`(팝빌 아이디)
   - `TAI_CORP_NUM`(사업자번호), `TAI_CORP_NAME`, `TAI_CEO_NAME`, `TAI_ADDR` 등 공급자 정보
5. **검증** — 테스트 모드로 세금계산서 1건 발행 → 국세청 승인번호 확인 → 운영 전환.

---

## A-3. 연동 probe 활성화 (WO-10) ✅ 완료

- Railway env(tai-api-prod): `API_SELF_URL` = `https://api.taieng.co.kr`
- 설정 후 `POST /integrations/probe`가 내부 API 실제 헬스체크 수행.

---

## B-1. 이니시스 환불 실검증 (WO-1)

- 첫 실결제 발생 후, 그 건으로 환불 1회 실행 → 이니시스 취소 API 응답·정산 반영 확인.
- 실결제 전에는 검증 불가(대기).

---

## C-1. 목업 데이터 위생 정리 (실운영 개시 전)

- 관제홈에 목업 미읽음 수신 179·발송실패 246이 잡힘. (+ A-1 검증 중 생긴 실패 목업 1건 포함)
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

~~A-1(Gmail)~~ ✅ → ~~A-3(probe env)~~ ✅ → C-1(목업정리). A-2(팝빌)·B-1(환불)은 실결제·실발행 시점에. D는 프론트 작업(P3)과 함께.
