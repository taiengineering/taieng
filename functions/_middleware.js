/**
 * Cloudflare Pages Middleware v2
 * 1. Bootstrap .fade CSS가 이니시스 결제창을 opacity:0으로 숨기는 문제 해결
 *    - 이니시스 기술지원 확인: "bootstrap css에서 fade 스타일을 입혀 결제창이 정상 노출되지 않음"
 * 2. 레거시 호스트명 → 현재 요청 호스트로 치환 (구 new.taieng.co.kr, 이니시스 V023 호환)
 */
export async function onRequest(context) {
  const response = await context.next();
  const contentType = response.headers.get('content-type') || '';

  if (!contentType.includes('text/html')) {
    return response;
  }

  let html = await response.text();

  // 1. 레거시 마케팅 호스트 → 현재 도메인 치환 (미리보기·구 HTML 호환)
  const currentHost = new URL(context.request.url).hostname;
  html = html.replaceAll('new.taieng.co.kr', currentHost);

  // 2. Bootstrap .fade CSS 충돌 해결 — 이니시스 결제창 opacity 강제 복원
  const inicisCSS = `<style>
/* [TAI] 이니시스 결제창 Bootstrap .fade 충돌 해결 */
.fade { opacity: 1 !important; }
.modal-backdrop.fade { opacity: 0.5 !important; }
</style>`;

  html = html.replace('</head>', inicisCSS + '\n</head>');

  return new Response(html, {
    status: response.status,
    statusText: response.statusText,
    headers: response.headers,
  });
}
