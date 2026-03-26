# Static file hosting using nginx:alpine
FROM nginx:1.25-alpine-slim

# Non-root user (nginx user exists in image - uid 101)
# No additional user creation needed

# Environment defaults
ENV NGINX_PORT=8080
ENV STATIC_ROOT=/usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d /etc/nginx/conf.d

# Copy static files
COPY public/ ${STATIC_ROOT}/

# Ensure non-root ownership
RUN chown -R nginx:nginx ${STATIC_ROOT} /var/cache/nginx /var/log/nginx

# Expose port
EXPOSE ${NGINX_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${NGINX_PORT}/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
