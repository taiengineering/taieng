# USER VISIBLE FINAL VERIFY REPORT V1
# WO-USER-VISIBLE-FINAL-VERIFY-001

**작성일**: 2026-06-19
**성격**: 배포 환경 실 HTTP 최종 검증 시도 + 도구 한계 정직 보고.
**검증 대상**: 화성 제2공장 (factory_id=e9c56af6)

---

## 최종 판정: USER_VISIBLE = 조건부 YES (데이터·경로 검증), 실 HTTP 왕복은 사장님 확인 필요

```
제(Claude) 도구 환경에서 검증 가능한 범위: 전부 PASS
제 도구 환경에서 수행 불가한 범위: 실 HTTP 호출 / 실 화면 렌더링
  → 이 부분은 사장님 또는 인증 클라이언트가 직접 확인해야 함 (아래 절차 제공)
```

---

## 도구 한계 (정직 보고)

```
이번 WO는 "실 HTTP 호출 + 실 화면 확인"을 요구하나,
제 도구 환경에서는 다음이 불가능:

1. bash 네트워크 비활성화 → curl 등 직접 호출 불가
2. web_fetch는 사전 검색/fetch 결과 URL만 허용 → 임의 API 호출 차단
   (api.taieng.co.kr/health 호출 시도 → PERMISSIONS_ERROR)
3. web_fetch는 GET 위주 → POST /persist 호출 불가
4. GET /diagnosis/transform/latest/{factory_id}는 인증 필요
   (get_current_user Depends) → 토큰 없이 호출 불가

→ FV-01(persist 실호출) / FV-02(transform 실호출) / FV-04(실화면)는
  제가 대신 수행할 수 없음. 추정으로 "성공"이라 쓰지 않음.
```

---

## 제 환경에서 검증 가능한 범위 (전부 PASS)

### FV-03: MUST 8건 존재 ✅ (DB 실측)
```
factory_diagnosis_results 화성 제2공장 최신 레코드:
  diagnosis_id=216fd7b0-be39-40e2-95f9-b5cc30b3c419
  is_latest=true, rule_count=8
  result_data.obligations 길이=8
```

### FV-05: 법령명 누락 0건 ✅ (DB 실측)
```
law_name_missing = 0 (8건 전부 법령명 보유)
```

### FV-06: 조치문 누락 0건 ✅ (DB 실측)
```
action_text_missing = 0 (8건 전부 description=action_text 보유)
```

---

## 중요 구분: 현재 DB 레코드의 출처

```
현재 factory_diagnosis_results의 화성 레코드(216fd7b0)는
WO-IMPL-002에서 SQL로 직접 INSERT한 것이다.
  = persist 엔드포인트의 "결과물과 동일한 구조"이지만
    persist 엔드포인트를 "실제 호출한 결과"는 아니다.

즉:
  데이터 구조·내용은 검증됨 (persist가 만들 것과 동일)
  persist 엔드포인트의 실 실행은 미검증 (배포+인증 필요)
```

---

## 배포 환경 최종 확인 절차 (사장님 또는 인증 클라이언트)

```
전제: Railway 배포 반영 확인 (main 푸시 후 자동배포)
  관련 커밋: 7896fb4(서비스 v1.1.0) / d20cbca(라우터 v1.1.1)

[1] persist 실 호출 (FV-01)
  POST https://api.taieng.co.kr/obligation-adapter/e9c56af6-5de7-487d-bd2e-0d452291a562/persist
  기대 응답:
    {status:"success", obligation_count:8, verdict:"REQUIRED",
     is_latest:true, diagnosis_id:"...",
     next:"GET /diagnosis/transform/latest/e9c56af6..."}

[2] transform_latest 실 호출 (FV-02) — 인증 토큰 필요
  GET https://api.taieng.co.kr/diagnosis/transform/latest/e9c56af6-5de7-487d-bd2e-0d452291a562
  Header: Authorization: Bearer <화성 사업장 소유 계정 토큰>
  기대 응답:
    obligations 배열 8건
    (단 _fetch_latest_row가 user_id 일치 확인 →
     화성 factory를 소유한 계정 토큰이어야 함. 주의사항 아래 참조)

[3] 실 화면 (FV-04)
  해당 사업장 진단 결과 화면에서 MUST 8건 표시 확인:
    선임: 안전관리자 선임 / 관리감독자 지정
    교육: 정기교육 / 채용교육 / 작업변경교육
    점검: 일반건강진단
    서류: 위험성평가 / 경보설비
```

---

## 발견한 잠재 이슈 (배포 호출 전 점검 권장, 추정 아님 — 코드 사실)

```
이슈 A: transform_latest의 user_id 권한 체크
  diagnosis_transform._fetch_latest_row:
    row.user_id != current_user.id → 403
  그러나 persist가 INSERT하는 row에는 created_by만 있고
  user_id를 명시 안 함 (factory_diagnosis_results 컬럼은 created_by).
  → transform_transform이 select하는 컬럼은 "user_id"인데
    테이블 컬럼은 created_by → 실 호출 시 권한/컬럼 불일치 가능.
  → 배포 전/후 이 지점 확인 필요. (이번 WO 범위 밖이라 수정 안 함, 관찰만)

이슈 B: persist는 현재 인증 없음 (누구나 호출 가능)
  보안상 추후 인증 추가 검토 대상. (이번 범위 밖)
```

---

## 원칙 준수

```
추정으로 "USER_VISIBLE=YES" 단정하지 않음 ✅
  (실 HTTP/화면은 내 환경서 불가 → 정직 보고)
DB로 검증 가능한 FV-03/05/06은 실측 PASS ✅
새 설계/Trace/Verify 없음 ✅
Construction/Building/Equipment/Boolean 안 건드림 ✅
이슈 A/B는 관찰만, 수정 안 함 ✅
```

---

## 결론

```
제 환경 검증분 (DB 기준):
  FV-03 MUST 8건 존재      → ✅
  FV-05 법령명 누락 0건    → ✅
  FV-06 조치문 누락 0건    → ✅

제 환경서 수행 불가 (사장님/인증 클라이언트 확인 필요):
  FV-01 persist 실 호출    → 절차 제공
  FV-02 transform 실 호출  → 절차 제공 (이슈 A 점검 포함)
  FV-04 실 화면 렌더링     → 절차 제공

최종 판정:
  데이터·경로·스키마는 USER_VISIBLE 준비 완료.
  실 HTTP 왕복 + 실 화면은 배포 환경에서 사장님 확인으로 종결.
  그 확인이 PASS면 USER_VISIBLE = YES 최종 확정.

  단, 배포 호출 전 이슈 A(user_id vs created_by 컬럼 불일치)를
  먼저 점검할 것을 권장. 이게 걸리면 transform_latest가 403/오류 가능.
```
