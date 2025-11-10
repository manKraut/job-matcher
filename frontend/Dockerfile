# Stage 1: Build the frontend
FROM node:20-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

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