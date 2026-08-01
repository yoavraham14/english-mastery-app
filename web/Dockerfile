# Static frontend served by nginx, which also proxies /api to the FastAPI service.
# Build context: repo root (english-mastery-app/), consistent with api/ and worker/.

FROM nginx:1.27-alpine

# nginx:alpine runs any *.template in this directory through envsubst at startup
# and writes the result to /etc/nginx/conf.d/. This is how API_HOST gets injected
# without baking an environment-specific value into the image.
COPY web/default.conf.template /etc/nginx/templates/default.conf.template

COPY web/index.html /usr/share/nginx/html/index.html

# Default for local Compose; overridden in Kubernetes via env.
ENV API_HOST=api:8000
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d

EXPOSE 8080
