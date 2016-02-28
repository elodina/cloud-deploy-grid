#!/bin/sh
#
docker build -t container ./
docker run -d -p 5555:5555 -v ${PWD}:/grid container bash -c "eval \$(ssh-agent -s); /usr/bin/python2 main.py"