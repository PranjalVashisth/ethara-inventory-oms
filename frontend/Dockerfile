FROM node:20-alpine AS build

WORKDIR /app
COPY frontend/package.json /app/
RUN npm install
COPY frontend /app
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
ENV API_UPSTREAM=http://backend:8000
# Nginx official image will envsubst templates at startup (/etc/nginx/templates/*.template)
COPY docker/nginx/default.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
