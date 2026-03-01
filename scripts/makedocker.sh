#!/bin/bash
docker build -t dynamiq-app:local -f docker/Dockerfile .
docker compose -f docker/docker-compose.yml up -d
