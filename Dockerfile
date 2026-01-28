# Build main frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Build admin frontend
FROM node:20-alpine AS admin-builder
WORKDIR /app
COPY admin-frontend/package*.json ./
RUN npm ci
COPY admin-frontend/ .
RUN npm run build

# Production
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=admin-builder /app/dist /usr/share/nginx/html/admin
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
