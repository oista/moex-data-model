# Self-hosted drawDB + MOEX postMessage bridge (ADR-005)
# Build: docker build -t moex-drawdb apps/drawdb
ARG UPSTREAM_SHA=e918bf1b457fd56bd756d5d2565c178c52b9fa7f

FROM node:20-alpine AS build
ARG UPSTREAM_SHA
WORKDIR /src
RUN apk add --no-cache git
RUN git clone --depth 1 https://github.com/drawdb-io/drawdb.git repo \
 && cd repo \
 && git fetch --depth 1 origin ${UPSTREAM_SHA} \
 && git checkout ${UPSTREAM_SHA}
WORKDIR /src/repo
RUN npm ci || npm install
RUN npm run build
COPY overlay/moex-bridge.js /src/repo/dist/moex-bridge.js
# Inject bridge script into index.html before </body>
RUN if [ -f dist/index.html ]; then \
      sed -i 's#</body>#<script src="/moex-bridge.js"></script></body>#' dist/index.html; \
    fi

FROM nginx:1.27-alpine
COPY --from=build /src/repo/dist /usr/share/nginx/html
# Also ship static-bridge as /bridge/ for debugging
COPY static-bridge /usr/share/nginx/html/bridge
EXPOSE 80
