// Cloudflare Worker — new.taieng.co.kr/_api/* -> api.taieng.co.kr/*
export default {
  async fetch(request) {
    const url = new URL(request.url);

    // /_api/ 경로만 프록시
    if (!url.pathname.startsWith("/_api/")) {
      return fetch(request);
    }

    // /_api 제거 후 api.taieng.co.kr로 전달
    const apiPath = url.pathname.replace(/^\/_api/, "");
    const apiUrl = `https://api.taieng.co.kr${apiPath}${url.search}`;

    const newRequest = new Request(apiUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method === "GET" || request.method === "HEAD" ? null : request.body,
      redirect: "follow",
    });

    const response = await fetch(newRequest);
    const newResponse = new Response(response.body, response);
    newResponse.headers.set("Access-Control-Allow-Origin", "*");
    newResponse.headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    newResponse.headers.set("Access-Control-Allow-Headers", "*");

    return newResponse;
  },
};
