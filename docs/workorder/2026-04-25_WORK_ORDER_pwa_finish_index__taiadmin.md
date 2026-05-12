# PWA 마무리 작업 통합 인덱스 (2026-04-25)

**상황**: 2026-04-24 PWA 1차 보강(`69d030e`) 완료 후 잔여 작업 + 미푸시 레포 정리 + 백엔드 P0 동시 진행

---

## 3개 트랙 구분

| 트랙 | 레포 | 담당 | 작업지시서 |
|---|---|---|---|
| **T1** PWA 프론트 마무리 | tai-admin / main | Cursor | `docs/WORK_ORDER_20260425_pwa_frontend_finish.md` |
| **T2** 미푸시 레포 정리 | tai-api, taieng | Cursor | `docs/WORK_ORDER_20260425_unpushed_repos_cleanup.md` |
| **T3** PWA 백엔드 P0 | tai-api / dev | Claude Code | `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md` |

---

## ⚠️ 실행 순서 (충돌 방지)

```
Step 1: T2 보고 단계 먼저 실행
   └─ Cursor가 tai-api/taieng 미푸시 변경 보고
   └─ 심태왕이 분류 A/B/C/D 결정
   
Step 2: T2 푸시 (승인된 분류 A만)
   └─ tai-api dev 브랜치에 정리해서 푸시
   └─ taieng main 푸시
   
Step 3: T1 작업 시작 (tai-admin)
   └─ Cursor가 inspect.html 사진 분리 등 잔여 P0/P1
   └─ main에 직접 커밋
   
Step 4: T3 시작 (Claude Code, tai-api)
   └─ T2 정리가 끝난 dev 브랜치에서 백엔드 P0 작업
   └─ /uploads/inspection-photo 등 신규 엔드포인트
   └─ dev → main merge → Railway 자동 배포
   
Step 5: 통합 검증
   └─ 프론트: 모바일 실기기로 사진 첨부 점검
   └─ 백엔드: /health 200 + 신규 엔드포인트 정상 응답
```

### 왜 이 순서인가

- **T2가 먼저인 이유**: tai-api 로컬에 미푸시분이 있는 상태에서 T3(백엔드 P0)를 진행하면 로컬 변경과 충돌. 정리 먼저 → 깨끗한 상태에서 신규 작업.
- **T1과 T3 분리 이유**: 다른 레포라 동시 진행 가능. T1은 백엔드 미배포 상태에서도 graceful degradation 되도록 설계됨.
- **T1보다 T2를 먼저 하는 이유**: T1은 단일 레포(tai-admin) 작업이라 충돌 위험 낮음. T2 먼저 끝내야 다음 단계 깔끔.

---

## 단계별 시간 예상

| Step | 작업 | 예상 시간 |
|---|---|---|
| 1 | T2 보고 (Cursor `git status` 등) | 10분 |
| 1.5 | 심태왕 검토 + 분류 결정 | 15분 |
| 2 | T2 푸시 | 10분 |
| 3 | T1 잔여 P0/P1 작업 | 30~60분 |
| 4 | T3 백엔드 P0 작업 | 2~3시간 |
| 5 | 통합 검증 | 30분 |
| **합계** | | **3.5~5시간** |

---

## 의존성 다이어그램

```
[T2 보고]
   ↓
[심태왕 분류 결정]
   ↓
[T2 푸시 완료]
   ↓
   ├─→ [T1 시작] (tai-admin, 독립)
   │     ↓
   │     [T1 main push]
   │     ↓
   │     [Cloudflare Pages 배포 → 프론트 동작]
   │
   └─→ [T3 시작] (tai-api dev)
         ↓
         [T3 dev → main merge]
         ↓
         [Railway 자동 배포]
         ↓
         [백엔드 신규 엔드포인트 활성화]

   ↓ (T1, T3 모두 완료)
   
[통합 검증]
   ↓
[심태왕 최종 OK]
```

---

## 완료 기준

### T1 완료 기준
- `inspect.html` submitCheck에 `TAI.uploadPhoto` 호출 존재
- `construction_inspect.html` 동일
- `camera.html`, `test.txt` 삭제됨
- main push → 모바일 접속 시 정상 동작

### T2 완료 기준
- `tai-api` 로컬 작업트리 clean (`git status` 깨끗)
- `taieng` 로컬 작업트리 clean
- 분류 B/C/D 항목은 별도 보존 또는 보류 처리됨
- 정리 보고서 제출

### T3 완료 기준
- `POST /uploads/inspection-photo` 정상 동작
- `POST /emergency/report` 서버 발급 report_number 반환
- `POST /safety-reports` `photo_urls` 수용
- `POST /worker-check/submit` Authorization 검증 + photo_urls 수용
- Railway `/health` 200 유지

### 전체 완료 기준
- 모바일 실기기에서 점검 → 사진 첨부 → 제출 → 서버 DB에 사진 URL 저장 확인
- 긴급신고 → 서버 발급 EMG 번호 수령 확인
- 비행기 모드 → 점검 제출 → 오프라인 큐 적재 → 네트워크 복구 시 자동 재전송 확인

---

## 참고 문서

- 1차 점검 리뷰: `docs/PWA_APP_REVIEW_20260424.md`
- 1차 진행 확인: `docs/PWA_REVIEW_FOLLOWUP_20260424.md`
- 1차 작업지시서 (이미 완료): `docs/WORK_ORDER_20260424_pwa_frontend.md`
- 통합 인덱스 (이전): `docs/WORK_ORDER_20260424_pwa_index.md`
- Capacitor 작업지시서: `docs/WORK_ORDER_20260424_capacitor_setup.md`
- Capacitor 진행 로그: `docs/CAPACITOR_BUILD_LOG_20260424.md`
- Play Console 진행 로그: `docs/PLAY_CONSOLE_SIGNUP_20260424.md`

---

**작성**: Claude (기획창)  
**조율**: 심태왕  
**실행**: Cursor (T1, T2) + Claude Code (T3)
