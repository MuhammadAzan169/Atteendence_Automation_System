# Static frontend served by nginx (used by docker-compose; Vercel does not
# need this file).
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html

# Docker build context noise that should not be published.
RUN rm -f /usr/share/nginx/html/Dockerfile \
          /usr/share/nginx/html/nginx.conf \
          /usr/share/nginx/html/.env \
          /usr/share/nginx/html/.env.example \
          /usr/share/nginx/html/vercel.json

EXPOSE 80
