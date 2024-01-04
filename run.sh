#!/bin/bash

# first parameter: path to network file (.net.xml)
# second parameter: path to request file (.txt)
# third parameter: path to vehicle file (.txt)

if [ -d "tmp" ]; then rm -Rf tmp; fi
mkdir tmp

# get underlying graph
python scripts/getGraph.py -n "$1" -go tmp/edges.txt -mo tmp/mapping.txt
# keep largest strongly connected component
./scripts/keepSCC tmp/edges.txt tmp/new_edges.txt
# format mapping
python scripts/formatMapping.py -m tmp/mapping.txt -e tmp/new_edges.txt -o tmp/new_mapping.txt
# generate initial feasible solution
./scripts/getInitialSolution "$3" $2 tmp/new_edges.txt tmp/new_mapping.txt tmp/initial_solution.txt tmp/new_requests.txt
# run model
python scripts/modelGurobi.py -v "$3" -r tmp/new_requests.txt -e tmp/new_edges.txt -i tmp/initial_solution.txt -ro tmp/routes.txt -ao tmp/assignments.txt
# format routes txt into SUMO-friendly xml
python scripts/formatRoutes.py -r tmp/routes.txt -m tmp/new_mapping.txt -o tmp/routes.xml
# run SUMO
sumo -n "$1" -r tmp/routes.xml --fcd-output tmp/fcd.xml
# convert FCD data to csv for post-processing
python scripts/xml2csv.py tmp/fcd.xml
# perform post-processing on FCD data
python scripts/analysis.py -fcd tmp/fcd.csv -m tmp/new_mapping.txt -r tmp/new_requests.txt -a tmp/assignments.txt
