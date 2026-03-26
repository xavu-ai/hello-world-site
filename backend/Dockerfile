# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Stage 2: Production
FROM node:20-alpine-slim

# Create non-root user
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup

WORKDIR /app

# Copy node_modules from builder
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules

# Copy application files
COPY --chown=appuser:appgroup server.js ./
COPY --chown=appuser:appgroup public/ ./public/

# Switch to non-root user
USER appuser

# Expose port from environment
EXPOSE ${PORT:-3000}

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:${PORT:-3000}/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start server
CMD ["node", "server.js"]
