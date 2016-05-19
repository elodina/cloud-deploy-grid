#!/bin/sh
#
cluster_name="$1"
docker build -t cdg .
docker tag cdg docker-registry.service.${cluster_name}:5000/cdg
docker push docker-registry.service.${cluster_name}:5000/cdg
