# 기획 세션 2026-04-14 — 웹사이트 리빌드 완료

## 세션 요약
- **참여:** 기획창(Opus) + 프론트엔드 창(Sonnet) 다수
- **대상:** new.taieng.co.kr (repo: taiengineering/taieng, nexas/)
- **결과:** 웹사이트 리빌드 14단계 완료

---

## 작업 내역

### 1. 사이트 분석 및 문제 진단
- site-map.html 기반 전체 페이지 분석
- 발견된 문제: 네비게이션 2종 혼재, 텍스트 깨짐, 구/신 페이지 충돌, pricing.html API 의존
- nexas_sample(원본 템플릿) vs nexas(라이브) 비교 분석
- repo 구조 확인: taiengineering/taieng (new.taieng.co.kr 서빙 repo)

### 2. 리빌드 기획서 v5 작성
- `docs/workorder-website-rebuild-v5.md` → taiengineering/taieng에 커밋
- 대표님의 30+ 장점 목록을 페이지별로 매핑
- Nexas 원본 템플릿(index-1~6) 레이아웃 매핑: 메인→index-1, 안전관리자→index-2, 사업주→index-3, SaaS→index-4, 요금→index-5, 회사소개→index-6
- 디자인 방향: 보라색 그라디언트 상단, Lato 폰트, 밝은 색감 유지
- 콘텐츠 방향: 슬로건 집중 탈피 → 실질적 가치 전달

### 3. 단계별 프롬프트 제공 (14단계)

| 단계 | 작업 | 상태 |
|------|------|------|
| 0 | nexas/ 정리 (파일 삭제, .gitignore) | ✅ 완료 (파일삭제만 보류) |
| 1 | header.js + footer.js 생성, 전 페이지 적용 | ✅ 완료 |
| 2 | index.html 리빌드 (index-1 기반) | ✅ 완료 |
| 3 | for-safety-manager.html 리빌드 (index-2 기반) | ✅ 완료 |
| 4 | for-business-owner.html 리빌드 (index-3 기반) | ✅ 완료 |
| 5 | service/saas.html 리빌드 (index-4 기반) | ✅ 완료 |
| 6 | service/diagnosis.html 리빌드 | ✅ 완료 |
| 7 | service/appointment.html 리빌드 (양면 마켓) | ✅ 완료 |
| 8 | service/repair.html 리빌드 (양면 마켓) | ✅ 완료 |
| 9 | service/consulting.html 리빌드 | ✅ 완료 |
| 10 | service/education.html 리빌드 | ✅ 완료 |
| 11 | service/inapp.html 리빌드 | ✅ 완료 |
| 12 | target/ 3개 리빌드 (건물/공장/건설) | ✅ 완료 |
| 13 | pricing.html + about.html 리빌드 | ✅ 완료 |
| 14 | 나머지 네비 통일 + 텍스트 전수검수 | ✅ 완료 |

### 4. 최종 점검 결과
- 전 페이지 header.js 네비게이션 통일 ✅
- 금지용어(소개비/크레딧) 전무 ✅
- 구 페이지 링크 전무 ✅
- 맞춤법 검수 완료 ("알맞는→알맞은" 등 수정) ✅
- about.html 대표 스토리 반영 ✅
- pricing.html 가격 하드코딩 ✅

### 5. 잔여 정리 작업 (보류)
- 리다이렉트 스텁 14개 완전 삭제 (현재 보류)
- node_modules/ git에서 제거
- Nexas.zip(10MB) nexas/에서 제거
- service/saas.html nav-auth.js 삽입

---

## GitHub 커밋 (기획창)

| repo | 파일 | 내용 |
|------|------|------|
| taiengineering/taieng | docs/workorder-website-rebuild-v5.md | 웹사이트 리빌드 기획서 v5 |
| taiengineering/tai-admin | docs/workorder-website-cleanup.md | 웹사이트 정리 작업지시서 (초기) |
| taiengineering/taieng | docs/session-2026-04-14-planning.md | 이 세션 기록 |

---

## 메모리 업데이트
- #13: Railway → Fly.io 도쿄 이전 완료 확인

---

## 대표님 피드백
- "이전보다 많이 좋아졌다"
- "구조가 특히 잘 풀렸다"
- "서비스가 다르게 소개된 게 있고, 기능들이 빠져 있으니 고도화 작업에서 수정"

---

## 다음 세션 TODO

### 웹사이트 고도화
- [ ] 서비스별 내용 정확도 검토 (대표님 피드백 기반)
- [ ] 빠진 기능들 추가
- [ ] 파일 삭제 (보류 중인 14개 스텁 + 템플릿 잔재)
- [ ] node_modules git 제거
- [ ] 실제 스크린샷 교체 (placeholder → 실서비스 화면)

### 백엔드/프론트 (기존 작업)
- [ ] 법령진단 → 자동일정 → 배정 → 알림 파이프라인 연결
- [ ] menu-tadmin.js sector 필터링
- [ ] safe.taieng.co.kr 대시보드
- [ ] TBM 하드코딩 제거
