#!/bin/sh
#
docker build -t container ./
if [ ! -f grids.db ]; then
  docker run -i -t -v ${PWD}:/grid container python /grid/gridapi/resources/models.py
fi
docker run -d -p 5555:5555 -v ${PWD}:/grid container bash -c "eval \$(ssh-agent -s); /usr/bin/python2 main.py"

