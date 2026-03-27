# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for layer caching
COPY package*.json ./

RUN npm ci --only=production

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application files
COPY --chown=node:1000 . .

# Switch to non-root user (node user already exists in node:20-alpine with uid 1000)
USER node

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start application
CMD ["node", "server.js"]
