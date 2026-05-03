# diagnosis.html 재설계 + footer 정리 작업로그

**날짜**: 2026-05-03 (저녁 세션)
**대상 페이지**: https://taieng.co.kr/service/diagnosis
**대상 파일**:
- `nexas/service/diagnosis.html`
- `nexas/assets/js/footer.js`

## 작업 흐름 요약

가격 직전에 이미지 6장 + 메시지 그리드 추가 작업으로 시작 → 사용자가 6장은 본문 ②～⑧의 메인 비주얼로 만들어진 것임을 확인 → 본문 6개 섭션을 일러스트 기반으로 재구성 → 콘티/설명 톤 정정 → 일부 섭션 HTML 카드로 전환 + 카운트업 추가 → footer 패딩 정리.

## 커밋 순서

| Commit | 메시지 | 마메소서 |
|--------|--------|------|
| `21b90f9` | fix(diagnosis): correct ⑧-2 alert image paths under site-assets/diagnosis/ | 사용자 직접 push (Cursor) |
| `9b2d5a8` | feat(diagnosis): replace ②~⑧ with diagnosis1~6.png illustrations, remove ⑧-2 alert section | 사용자 직접 push (Cursor) |
| `714b582` | refactor(diagnosis): rewrite section copy to match illustrations, remove app-preview, add decisive band before pricing | MCP push |
| `fc78ff4` | feat(diagnosis): rebuild ⑥⑦⑧ as full-width HTML cards, add count-up animation on stats, indent left text | MCP push |
| `3c306f3` | tweak(diagnosis): restore diagnosis5.png illustration on ⑦, slow down counter animation | MCP push |
| `e8cbf0f` | fix(footer): trim oversized padding (footer-inner 80px+ → 36px, bottom 14px) | MCP push |

## 최종 페이지 구조

| 섭션 | 위치 | 콘텐츠 |
|------|------|--------|
| ① | 히어로 | "모르면 벌금, 알면 안심입니다" (유지) |
| ② | 본문 | diagnosis1.png — 4가지 답답한 현실 |
| ③ | 본문 (alt) | diagnosis2.png — 입력→분석→결과 흐름 |
| ④ | 본문 | diagnosis3.png — 결과 리포트 |
| ⑤ | 본문 (alt) | HTML 풌가로 카드 2장 (기존방식 vs TAI 솔루션) + 가운데 VS 원형 배지 |
| ⑥ | 본문 | diagnosis5.png — 점검 준비/내부 점검 계획/초기 안전관리 구축 |
| ⑦ | 본문 (alt) | HTML 통계 카드 4장 (752/32,808/2,677/35) + 카운트업 + 하단 메시지 밴드 |
| — | 가격 직전 | 결정짓는 문구 — 다크 navy(#0a1424) + 정제된 타이포 |
| — | 보호 영역 | 가격 섭션 (KG이니시스 카드 심사 중, 무변경) |
| ⑧ | 최종 CTA | "무료로 법령진단을 시작하세요" |

※ alt = 다크 톤 .alt 배경 (③⑤⑦ 줄무달 리듬)

## 주요 디자인 결정

1. **본문 좌측 텍스트**: 작업용 라벨("문제 정의/해결 방식" 등) 모두 제거. 일러스트 내용에 맞는 콘티(헤드라인) + 본문 설명으로 재작성. col-3에 narrow 배치, padding-left 24px 들여쓰기.
2. **이미지 사용 일관성**: diagnosis1~3은 ②③④에 직접 표시. diagnosis4는 HTML 카드(⑤)로 대체, diagnosis5는 ⑥에 사용, diagnosis6는 HTML 통계 카드(⑦)로 대체.
3. **카운트업**: IntersectionObserver(threshold 0.4) + ease-out cubic. 1,000+ 숫자 2,800ms / 미만 2,200ms. tabular-nums + Intl.NumberFormat ko-KR. 한 번만 실행.
4. **결정짓는 문구**: 박스/그림자 일체 없이 다크 navy(#0a1424) 단색 + 36px 가는 디바이더 + 정제된 타이포(weight 800 헤드라인 / weight 400 서브). "고급적이고 전문성" 요구 반영.
5. **footer**: footer-inner 외부 CSS 기본 80px+ → 36px, footer-bottom 14px, widget 간격 축소. footer.js v3.4.0으로 전 사이트 자동 적용.

## 미사용 자산

- `site-assets/diagnosis/diagnosis4.png` — ⑤ HTML로 대체됨, Storage 삭제 가능
- `site-assets/diagnosis/diagnosis6.png` — ⑦ HTML로 대체됨, Storage 삭제 가능

## 보호 영역 (이번 작업에서 일체 손대지 않음)

- `<section class="price-section" id="pricing">` 가격 블록 전체
- `#diag_inicis_form` 결제 폼
- `diagPay()` 함수, INIStdPay 스크립트
- `<section class="diag-hero">` 히어로
- `<section class="final-cta-section">` 최종 CTA

## 관련 문서

- 이슈 목록: `nexas/docs/issues-20260503-diagnosis.md`
