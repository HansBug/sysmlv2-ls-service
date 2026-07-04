FROM node:24-bookworm-slim AS build

WORKDIR /app
ENV CI=true
RUN corepack enable

COPY . .

RUN pnpm install --frozen-lockfile \
  && pnpm run build:upstream \
  && pnpm run build \
  && pnpm prune --prod

FROM node:24-bookworm-slim AS runtime

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000

ARG SERVICE_VERSION
ARG SERVICE_REVISION
ARG SOURCE_REPOSITORY
ARG UPSTREAM_SYSML_2LS_VERSION
ARG UPSTREAM_SYSML_2LS_REVISION
ARG UPSTREAM_SYSML_2LS_REPOSITORY
ARG BUILD_DATE

ENV SERVICE_VERSION=$SERVICE_VERSION
ENV SERVICE_REVISION=$SERVICE_REVISION
ENV SOURCE_REPOSITORY=$SOURCE_REPOSITORY
ENV UPSTREAM_SYSML_2LS_VERSION=$UPSTREAM_SYSML_2LS_VERSION
ENV UPSTREAM_SYSML_2LS_REVISION=$UPSTREAM_SYSML_2LS_REVISION
ENV UPSTREAM_SYSML_2LS_REPOSITORY=$UPSTREAM_SYSML_2LS_REPOSITORY
ENV BUILD_DATE=$BUILD_DATE

LABEL org.opencontainers.image.title="sysmlv2-ls-service"
LABEL org.opencontainers.image.description="Docker-ready SysML v2 validation microservice wrapping sysml-2ls."
LABEL org.opencontainers.image.source=$SOURCE_REPOSITORY
LABEL org.opencontainers.image.revision=$SERVICE_REVISION
LABEL org.opencontainers.image.version=$SERVICE_VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.vendor="HansBug"
LABEL io.hansbug.sysmlv2-ls-service.upstream.sysml-2ls.version=$UPSTREAM_SYSML_2LS_VERSION
LABEL io.hansbug.sysmlv2-ls-service.upstream.sysml-2ls.revision=$UPSTREAM_SYSML_2LS_REVISION
LABEL io.hansbug.sysmlv2-ls-service.upstream.sysml-2ls.repository=$UPSTREAM_SYSML_2LS_REPOSITORY

COPY --from=build --chown=node:node /app/package.json ./package.json
COPY --from=build --chown=node:node /app/VERSION ./VERSION
COPY --from=build --chown=node:node /app/dist ./dist
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/upstream/sysml-2ls/packages/syside-base ./upstream/sysml-2ls/packages/syside-base
COPY --from=build --chown=node:node /app/upstream/sysml-2ls/packages/syside-languageserver ./upstream/sysml-2ls/packages/syside-languageserver
COPY --from=build --chown=node:node /app/upstream/sysml-2ls/packages/syside-protocol ./upstream/sysml-2ls/packages/syside-protocol

USER node
EXPOSE 3000
CMD ["node", "dist/src/server.js"]
