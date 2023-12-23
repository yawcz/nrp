import argparse
import pandas as pd

parser = argparse.ArgumentParser(
	prog='format_trips',
	description='formats trips from csv to model-friendly format'
)

parser.add_argument('-t', '--trips', help='path to .csv file containing trip data', type=str, required=True)
parser.add_argument('-m', '--mapping', help='path to .txt file containing mapping data', type=str, required=True)
# output format: two space-separated integers representing origin and destination of each request
parser.add_argument('-o', '--output', help='path to output file', type=str, required=True)

args = parser.parse_args()

trips = pd.read_csv(args.trips, dtype={'trip_from': 'string', 'trip_to': 'string'}, sep=';')
mapping = []

with open(args.mapping, 'r') as f:
	for line in f.readlines():
		mapping.append(line.strip())

with open(args.output, 'w') as f:
	for index, row in trips.iterrows():
		f.write('%g %g\n' % (mapping.index(row['trip_from']), mapping.index(row['trip_to'])))
