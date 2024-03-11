#!/bin/sh
echo "Argument num thread pass to entrypoint: $@"
./multi_tor.sh "$@"
python3 collect_buildings.py "$@"
