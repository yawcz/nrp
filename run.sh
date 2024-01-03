#!/bin/bash

# first parameter: path to network file (.net.xml)
# second parameter: number of requests
# third parameter: number of vehicles
# fourth parameter: capacity of each vehicle

if [ -d "tmp" ]; then rm -Rf tmp; fi
mkdir tmp

# get underlying graph
python scripts/getGraph.py -n "$1" -go tmp/edges.txt -mo tmp/mapping.txt
# keep largest strongly connected component
./scripts/keepSCC tmp/edges.txt tmp/new_edges.txt
# generate random trips
python scripts/randomTrips.py -n $1 -e "$2" -o tmp/trips.trips.xml
# convert trips from xml into csv format
python scripts/xml2csv.py tmp/trips.trips.xml
# format trips csv into model-friendly format
python scripts/formatTrips.py -t tmp/trips.trips.csv -m tmp/mapping.txt -o tmp/requests.txt
# generate random vehicles
python scripts/randomVehicles.py -e tmp/new_edges.txt -n "$3" -c "$4" -o tmp/vehicles.txt
# generate initial feasible solution
./scripts/getInitialSolution tmp/vehicles.txt tmp/requests.txt tmp/new_edges.txt tmp/initial_solution.txt
# run model
python scripts/modelGurobi.py -v tmp/vehicles.txt -r tmp/requests.txt -e tmp/new_edges.txt -i tmp/initial_solution.txt -o tmp/routes.txt
# format routes txt into SUMO-friendly xml
python scripts/formatRoutes.py -r tmp/routes.txt -m tmp/mapping.txt -o tmp/routes.xml
# run SUMO
sumo-gui -n "$1" -r tmp/routes.xml
