import argparse
import random

parser = argparse.ArgumentParser(
	prog='random_vehicles',
	description='generates random vehicles'
)

parser.add_argument('-m', '--mapping', help='path to mapping file', type=str, required=True)
parser.add_argument('-n', '--num_vehicles', help='number of vehicles', type=int, required=True)
parser.add_argument('-c', '--capacity', help='capacity of each vehicle', type=int, required=True)
# output format: two space-separated integers representing position and capacity of each vehicle
parser.add_argument('-o', '--output', help='path to output file', type=str, required=True)

args = parser.parse_args()

num_vertices = 0

with open(args.mapping, 'r') as f:
	num_vertices += len(f.readlines())

with open(args.output, 'w') as f:
	for i in range(args.num_vehicles):
		f.write('%g %g\n' % (random.randint(0, num_vertices - 1), args.capacity))
