#!/bin/bash
set -e

echo "=== Building Docker image ==="
docker-compose build 2>&1 | tee build.log

echo ""
echo "=== Testing configuration ==="
docker-compose run --rm smart-video python -m src.main --help 2>&1 | head -20

echo ""
echo "=== Running test ==="
docker-compose run --rm smart-video python -m src.main --url "https://www.youtube.com/watch?v=lbCP_2f4rwI" 2>&1 | tee test.log

echo ""
echo "=== Test completed ==="

