FROM nginx:alpine

# Copy custom nginx configuration for routing fallbacks
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy production index.html to serve
COPY dist/index.html /usr/share/nginx/html/index.html

EXPOSE 80
