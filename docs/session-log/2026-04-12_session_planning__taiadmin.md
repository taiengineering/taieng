# TAI Safe 기획 세션 — 2026-04-12

> 대표 + Claude(Opus) 기획 토의 결과. 모든 창에서 참고할 것.
> 원본: tai-api/docs/session-2026-04-12-planning.md

---

## 핵심 결정 요약

### 1. 개발 원칙
- 개발 75% 시점, **인프라 변경 금지**
- 100% 완료 후 안정화 기간(2~3주)에 일괄 전환
- 현재 Railway + Supabase + Cloudflare Pages 그대로 유지

### 2. 배포 정책 (즉시 적용)
- 모든 커밋을 **dev 브랜치**에 (main 직접 커밋 금지)
- MCP push_files 시 `branch: "dev"` 지정
- 확인 후 PR(dev→main)으로 병합, main만 운영 자동배포
- 긴급 핫픽스는 main 직접 허용하되 즉시 dev 동기화

### 3. 서버 전환 (→1순위 Fly.io 도쿄, 100% 후)
- Fly.io 도쿄: 한국 레이턴시 25~35ms (Railway 대비 1/4~1/5)
- 이전 예상 소요: 반나절
- DB/프론트/코드 변경 없음

### 4. 하이브리드 아키텍처 (100% 후)
- CRUD 15개+ 라우터 → PostgREST + RLS 직접 호출
- 알림 → Supabase Edge Function
- 인증 → Supabase Auth
- Cron → pg_cron
- PDF → Gotenberg (Docker, ~$5/월)
- FastAPI는 PDF + 법령엔진만 남김

### 5. 모니터링
- UptimeRobot 4개 모니터 설정 완료
- 100% 후: pg_cron 비즈니스 로직, Sentry, 일일 리포트 추가

### 6. 웹사이트 디자인
- AI에게 단순 지시 → 디자이너에게 지시하는 방식으로 변경
- 레퍼런스 + 특징 + 구조 설명 + 섹션단위 검수
- 역할 기반 접근 (안전관리자 vs 현장소장) 확정

### 7. 조직 계획
- 단기: 1.5명 (대표 + AI + 파트타임 운영)
- 중기: 3~4명 (영업/고객담당 우선, 개발자는 후순위)
- 첫 채용은 개발자가 아니라 영업/고객 담당

### 8. QA
- QA 반복 점검은 Sonnet이 적합 (Opus는 기획/분석)

---

> 상세 내용은 tai-api/docs/session-2026-04-12-planning.md 참고
