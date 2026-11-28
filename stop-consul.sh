#!/bin/bash

echo Halting Consul

cd -- "$(dirname -- "${BASH_SOURCE[0]}")" || exit 1
docker compose -p bettermusic-local -f docker-compose.consul-local.yml down
