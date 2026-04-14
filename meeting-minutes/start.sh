#!/bin/bash
set -e

cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 9011 &
API_PID=$!

nginx -g 'daemon off;' &
WEB_PID=$!

trap 'kill -TERM $API_PID $WEB_PID 2>/dev/null' TERM INT
wait -n $API_PID $WEB_PID
EXIT_CODE=$?
kill -TERM $API_PID $WEB_PID 2>/dev/null || true
exit $EXIT_CODE
