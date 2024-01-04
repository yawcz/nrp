#!/bin/bash

# first parameter: path to network file (.net.xml)
# second parameter: number of requests
# third parameter: output of requests file
# fourth parameter number of vehicles
# fifth parameter: capacity of each vehicle
# sixth parameter: output of vehicles file

# get underlying graph
python scripts/getGraph.py -n "$1" -go tmp/edges.txt -mo tmp/mapping.txt
# keep largest strongly connected component
./scripts/keepSCC tmp/edges.txt tmp/new_edges.txt
# generate requests
python scripts/randomTrips.py -e tmp/new_edges.txt -n "$2" -o "$3"
# generate vehicles
python scripts/randomVehicles.py -e tmp/new_edges.txt -n "$4" -c "$5" -o "$6"
