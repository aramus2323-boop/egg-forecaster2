# Build stage
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install static file server
RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 3000

# Serve the built React app (use $PORT env var for Railway compatibility)
CMD ["serve", "-s", "dist", "-l", "${PORT:-3000}"]
