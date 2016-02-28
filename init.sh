#!/bin/sh
#
docker build -t container ./
docker run -i -t -v ${PWD}:/grid container python /grid/gridapi/resources/models.py
