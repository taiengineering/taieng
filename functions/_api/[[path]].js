/**
 * Cloudflare Pages Function — /_api/* 프록시
 * taieng.co.kr/_api/payments/inicis/return (레거시: new.taieng.co.kr 동일 경로)
 *   → api.taieng.co.kr/payments/inicis/return
 *
 * 목적: 이니시스 V023 에러 방지 (결제요청 페이지와 returnUrl 도메인 일치)
 */
export async function onRequest(context) {
  const { request, params } = context;
  const url = new URL(request.url);

  // /_api/ 이후 경로 추출
  const apiPath = '/' + (params.path ? params.path.join('/') : '');
  const apiUrl = 'https://api.taieng.co.kr' + apiPath + url.search;

  // OPTIONS preflight 처리
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  }

  // 원본 요청을 api.taieng.co.kr로 전달
  const proxyRequest = new Request(apiUrl, {
    method: request.method,
    headers: request.headers,
    body: ['GET', 'HEAD'].includes(request.method) ? null : request.body,
    redirect: 'manual',
  });

  try {
    const response = await fetch(proxyRequest);
    const newHeaders = new Headers(response.headers);
    newHeaders.set('Access-Control-Allow-Origin', '*');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
