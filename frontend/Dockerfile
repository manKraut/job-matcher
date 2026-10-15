# Stage 1: Build the frontend
FROM node:20-alpine AS build

WORKDIR /app

# Trust the corporate Cisco Umbrella root CA (needed on the company network)
COPY certs/cisco-umbrella-root.crt /usr/local/share/ca-certificates/cisco-umbrella-root.crt
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/cisco-umbrella-root.crt

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build

# Stage 2: Serve with a static file server
FROM nginx:alpine

# Copy built frontend from previous stage
COPY --from=build /app/dist /usr/share/nginx/html

# Optional: Replace the default nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]