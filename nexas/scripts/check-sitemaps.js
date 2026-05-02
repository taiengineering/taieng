#!/usr/bin/env node
/**
 * 빌드 산출물(nexas 루트)에 사이트맵 핵심 파일이 있는지 확인합니다.
 * 분할 개수가 바뀌면 generate_sitemap.py 재실행 후 _redirects 목록도 맞추세요.
 */
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const required = [
  "sitemap.xml",
  "sitemap_index.xml",
  "sitemap_marketing.xml",
  "sitemap_news_1.xml",
  "sitemap_cases.xml",
  "sitemap_laws.xml",
  "sitemap_precedents.xml",
];

let ok = true;
for (const f of required) {
  const p = path.join(root, f);
  if (!fs.existsSync(p)) {
    console.error(`[check-sitemaps] Missing: ${f}`);
    ok = false;
  }
}
if (!ok) {
  console.error(
    "[check-sitemaps] Run: python3 scripts/generate_sitemap.py (from nexas/)"
  );
  process.exit(1);
}
console.log("[check-sitemaps] OK");
