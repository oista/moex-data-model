# Web application: build the SPA, then serve it and the publication viewer.
FROM node:20-alpine AS build

WORKDIR /src
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM nginx:1.27-alpine

ARG DEPS_FINGERPRINT=
ARG MOEX_VERSION=
ARG GIT_SHA=
LABEL moexmodel.deps_fingerprint="${DEPS_FINGERPRINT}" \
      moexmodel.full_version="${MOEX_VERSION}" \
      moexmodel.git_sha="${GIT_SHA}"

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/40-moex-auth.sh /docker-entrypoint.d/40-moex-auth.sh
RUN sed -i 's/\r$//' /docker-entrypoint.d/40-moex-auth.sh \
    && chmod 755 /docker-entrypoint.d/40-moex-auth.sh
COPY --from=build /src/dist /usr/share/nginx/html
RUN mkdir -p /usr/share/nginx/viewer \
    && chown 10001:10001 /usr/share/nginx/viewer

EXPOSE 80
