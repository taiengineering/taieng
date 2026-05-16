FROM node:22-slim AS base
WORKDIR /app

RUN npm install -g pnpm@9

COPY package.json pnpm-workspace.yaml ./
COPY packages/core-shared-types/package.json packages/core-shared-types/
COPY packages/core-ai-runtime/package.json packages/core-ai-runtime/
COPY packages/core-queue-runtime/package.json packages/core-queue-runtime/
COPY packages/core-event-runtime/package.json packages/core-event-runtime/
COPY packages/core-policy-runtime/package.json packages/core-policy-runtime/
COPY packages/core-db-runtime/package.json packages/core-db-runtime/
COPY packages/channel-naver-kin/package.json packages/channel-naver-kin/
COPY packages/domain-pack-tai/package.json packages/domain-pack-tai/
COPY apps/marketing-api/package.json apps/marketing-api/
COPY apps/marketing-worker/package.json apps/marketing-worker/
COPY apps/marketing-collector/package.json apps/marketing-collector/
COPY apps/marketing-ai-worker/package.json apps/marketing-ai-worker/
COPY apps/scheduler/package.json apps/scheduler/

RUN pnpm install --no-frozen-lockfile

COPY . .

RUN pnpm --filter @45cm/marketing-api... --filter @45cm/marketing-worker... build

# Diagnostic: show dist structure + catch startup errors
EXPOSE 3100
CMD ["node", "-e", "\
  console.log('=== DIAG START ===');\
  console.log('node_modules exists:', require('fs').existsSync('/app/node_modules/@45cm'));\
  console.log('api dist exists:', require('fs').existsSync('/app/apps/marketing-api/dist/server.js'));\
  console.log('worker dist exists:', require('fs').existsSync('/app/apps/marketing-worker/dist/worker.js'));\
  try { require('/app/apps/marketing-api/dist/server.js'); }\
  catch(e) { console.error('FATAL:', e.message); console.error(e.stack); }\
"]
