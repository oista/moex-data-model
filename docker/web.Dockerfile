# Web application: build the SPA, then serve it and the publication viewer.
FROM node:20-alpine AS build

WORKDIR /src
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist /usr/share/nginx/html
RUN mkdir -p /usr/share/nginx/viewer \
    && chown nginx:nginx /usr/share/nginx/viewer

EXPOSE 80
