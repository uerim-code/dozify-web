#!/bin/sh
# Push deploy/nginx.conf into the Coolify app (custom nginx configuration),
# force www -> apex, and redeploy. Run after `python3 tools/build-nginx.py`.
set -e
VPS=root@178.104.193.186
APP=ansxeoavqzazxpf5vnjbuzdd
cd "$(dirname "$0")/.."
B64=$(base64 < deploy/nginx.conf | tr -d '\n')
ssh -o BatchMode=yes "$VPS" "T=\$(cat /root/.coolify_token);
  curl -s -X PATCH -H \"Authorization: Bearer \$T\" -H 'Content-Type: application/json' \
    http://localhost:8000/api/v1/applications/$APP \
    -d '{\"custom_nginx_configuration\":\"$B64\",\"redirect\":\"non-www\"}' | head -c 300; echo;
  curl -s -H \"Authorization: Bearer \$T\" \"http://localhost:8000/api/v1/deploy?uuid=$APP&force=false\" | head -c 300; echo"
