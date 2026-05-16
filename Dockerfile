FROM node:22-slim AS base
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@9

# Copy workspace config first (cache layer)
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

# Install all deps
RUN pnpm install --no-frozen-lockfile

# Copy source
COPY . .

# Build
RUN pnpm --filter @45cm/marketing-api... --filter @45cm/marketing-worker... build

# Runtime
EXPOSE 3100
CMD ["node", "start-mkt.js"]
