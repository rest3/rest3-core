#!/usr/bin/env bash

docker rm -f $(docker ps | grep rest3api| awk "{print \$1}")
docker rmi -f dutronlabs/rest3api
docker build -t dutronlabs/rest3api .
