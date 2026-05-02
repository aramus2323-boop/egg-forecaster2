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

# Serve the built React app
CMD ["serve", "-s", "dist", "-l", "3000"]
