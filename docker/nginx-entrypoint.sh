#!/bin/sh
set -e

# Create necessary nginx temp directories
# These are required by nginx but can't be created when root filesystem is read-only
# Directories will be owned by the current user (1000) thanks to fsGroup in podSecurityContext
mkdir -p /var/cache/nginx/client_temp \
         /var/cache/nginx/proxy_temp \
         /var/cache/nginx/fastcgi_temp \
         /var/cache/nginx/uwsgi_temp \
         /var/cache/nginx/scgi_temp

# Execute the original nginx entrypoint
exec /docker-entrypoint.sh "$@"
