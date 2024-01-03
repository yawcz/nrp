import argparse
import random

parser = argparse.ArgumentParser(
	prog='random_vehicles',
	description='generates random vehicles'
)

parser.add_argument('-e', '--edges', help='path to edges file', type=str, required=True)
parser.add_argument('-n', '--num_vehicles', help='number of vehicles', type=int, required=True)
parser.add_argument('-c', '--capacity', help='capacity of each vehicle', type=int, required=True)
# output format: two space-separated integers representing position and capacity of each vehicle
parser.add_argument('-o', '--output', help='path to output file', type=str, required=True)

args = parser.parse_args()

valid_vertices = []

with open(args.edges, 'r') as f:
	for line in f.readlines():
		u, v, w = line.strip().split()
		valid_vertices.append(u)
		valid_vertices.append(v)

valid_vertices = list(set(valid_vertices))

with open(args.output, 'w') as f:
	for i in range(args.num_vehicles):
		f.write('%s %g\n' % (random.choice(valid_vertices), args.capacity))
