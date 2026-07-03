FROM node:20-bookworm-slim AS build

WORKDIR /app
ENV CI=true
RUN corepack enable

COPY . .

RUN pnpm install --frozen-lockfile \
  && pnpm run build:upstream \
  && pnpm run build \
  && pnpm prune --prod

FROM node:20-bookworm-slim AS runtime

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000

COPY --from=build /app/package.json ./package.json
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/upstream/sysml-2ls/packages/syside-base ./upstream/sysml-2ls/packages/syside-base
COPY --from=build /app/upstream/sysml-2ls/packages/syside-languageserver ./upstream/sysml-2ls/packages/syside-languageserver
COPY --from=build /app/upstream/sysml-2ls/packages/syside-protocol ./upstream/sysml-2ls/packages/syside-protocol

USER node
EXPOSE 3000
CMD ["node", "dist/src/server.js"]
