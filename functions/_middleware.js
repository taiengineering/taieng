// Cloudflare Pages Middleware
// HTML 응답에서 new.taieng.co.kr → 현재 요청 도메인으로 동적 치환
// 이니시스 V023 에러 방지: 결제페이지와 returnUrl 동일 도메인 보장

export async function onRequest(context) {
  const response = await context.next();
  const contentType = response.headers.get('content-type') || '';

  // HTML 응답만 처리
  if (!contentType.includes('text/html')) {
    return response;
  }

  const requestHost = new URL(context.request.url).host;

  // taieng.co.kr에서 접속한 경우에만 치환 (new.taieng.co.kr에서는 불필요)
  if (requestHost === 'new.taieng.co.kr') {
    return response;
  }

  let html = await response.text();

  // new.taieng.co.kr → 현재 요청 도메인으로 치환
  html = html.replaceAll('new.taieng.co.kr', requestHost);

  return new Response(html, {
    status: response.status,
    statusText: response.statusText,
    headers: response.headers,
  });
}
