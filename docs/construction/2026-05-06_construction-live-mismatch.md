# 이슈: construction.html 라이브 vs repo 콘텐츠 불일치

- **날짜**: 2026-05-06
- **상태**: OPEN
- **심각도**: CRITICAL
- **관련 페이지**: https://taieng.co.kr/target/construction
- **관련 파일**: `nexas/target/construction.html` (SHA `3ce45c8292c0`)

## 증상

사용자가 라이브 페이지에서 캡처해서 보낸 콘텐츠 3종:

1. **"선임 관리" 섹션**
   - eyebrow: "선임 관리" (작은 라벨)
   - 헤드라인: "선임 의무가 / 시설 규모에 맞춰 산출됩니다"
   - 부연: "안전관리자, 보건관리자, 소방안전관리자. 누구를 선임해야 하는지 시스템이 판정합니다."

2. **"리스크 가시화" 섹션**
   - eyebrow: "리스크 가시화" (작은 라벨)
   - 헤드라인: "리스크가 / 사전에 보입니다"
   - 부연: "의무 미이행 시 발생할 수 있는 과태료·벌금·영업정지 수준이 사전에 표시됩니다."
   - 좌측: 깨진 이미지 자리표시자 (alt: "위반 처벌 사전 가시화")

3. 사용자가 "전체 페이지에서 삭제" 요청한 sub-title 디자인 패턴 — 빨간색/오렌지 톤 작은 라벨

## 모순

이 콘텐츠가 GitHub repo의 `construction.html`에 **존재하지 않음**.

repo `construction.html` (SHA `3ce45c8292c0`, 18.98KB) 본문 검사 결과:
- 7섹션 + CTA 구조: 현실공감 / 핵심메시지 / 현실대응 / 감정압축 / 전환메시지 / 방향제시 / CTA
- "선임 관리", "리스크 가시화", "위반 처벌" 키워드 0건
- sub-title 디자인은 직전 커밋 `1569da05dd`에서 4곳 모두 삭제 완료

## 가능한 원인

### A. 사용자 브라우저 캐시 (가장 가능성 높음)
- 직전 작업들이 13:23~13:30 사이에 9차례 push됨
- Cloudflare Pages 자동 배포 시간(1~2분) + 사용자 브라우저 디스크 캐시로 옛 버전이 보일 수 있음
- **검증 방법**: Cmd/Ctrl + Shift + R 강제 새로고침

### B. Cloudflare Pages 빌드 실패 (중간 가능성)
- 어떤 시점부터 main 브랜치 자동 빌드가 실패해서 라이브에 옛 버전이 stuck됐을 가능성
- **검증 방법**: Cloudflare Pages 대시보드에서 최근 빌드 로그 + 마지막 성공 배포 시각 확인

### C. 다른 파일 라우팅 (낮은 가능성)
- `nexas/target/` 디렉토리 listing 결과:
  - `building.html` (15.98KB)
  - `construction.html` (18.98KB)
  - `factory.html` (18.84KB)
  - 다른 construction 관련 파일 없음
- **결론**: 라우팅 문제는 아님

## 확인 시도 결과

| 시도 | 결과 |
|---|---|
| Chrome MCP `tabs_create_mcp` + `get_page_text` | "No tab available" 실패 (사용자 Chrome과 Claude 세션 미연결) |
| GitHub `nexas/target/` 디렉토리 listing | construction.html 단일, 다른 후보 없음 |
| GitHub `construction.html` SHA 본문 검사 | 7섹션 + CTA만 존재, 캡처 콘텐츠 0건 |

## 다음 단계

1. **사용자 hard refresh 후 재캡처** — 가장 빠른 검증. 직전 작업이 배포된 최신 상태가 보이면 위 캡처 콘텐츠는 사라질 것.
2. **Cloudflare Pages 빌드 로그 확인** — hard refresh 후에도 옛 콘텐츠 보이면 빌드 실패 의심.
3. **사용자가 라이브 inspect element / view-source 확인** — 실제 HTML 발췌 제공받아 라우팅 검증.
4. **만약 라이브에 진짜 그 콘텐츠가 있고 repo는 없으면** — 다른 source(예: Cloudflare Pages 별도 배포, branch deploy 등)에서 오는 거 — 인프라 조사 필요.

## 사용자가 본 콘텐츠가 다른 페이지일 가능성

사용자가 직전 답변으로 라이브 URL `https://taieng.co.kr/target/construction`만 명시했지만, 실제로는 사용자가 다른 페이지 (예: `target/building.html`, `service/saas.html`, `service/inapp.html`)에서 캡처했을 가능성도 있음. 사용자가 "이 페이지 맞습니다"라고 명시적으로 확인 필요.

## 잠재적 후속 작업 (이슈 해결 후)

사용자가 보고 있는 페이지가 진짜 construction.html이면:
- 라이브-repo 불일치 원인 해결 (배포/캐시)
- 새 섹션 "리스크 가시화" 추가 가능성 (construction5.png 좌측 + 텍스트 오버레이)
  - 사용자가 이미 supabase에 `construction5.png` 업로드 완료
  - 적용 페이지 미확정

사용자가 보고 있는 페이지가 다른 페이지라면:
- 해당 페이지에 동일 sub-title 패턴 일괄 삭제
- 같은 페이지에 "리스크 가시화" 섹션 디자인 변경 (좌측 이미지 + 텍스트 오버레이)

## 작업 원칙 회고

- **검증 없는 진행 금지**: 사용자가 본 캡처를 "라이브에 진짜 있다"고 가정하고 작업하면 잘못된 페이지/잘못된 위치에 추가될 위험. 라이브-repo 불일치 원인부터 해결 필요.
- **Chrome MCP 의존 한계**: "No tab available"로 라이브 직접 검사 불가능. 사용자 협조(hard refresh, inspect element)가 결정적.
