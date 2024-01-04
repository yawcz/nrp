import argparse

parser = argparse.ArgumentParser(
	prog='format_mapping',
	description='formats mapping file'
)

parser.add_argument('-e', '--edges', help='path to .txt file containing edges data', type=str, required=True)
parser.add_argument('-m', '--mapping', help='path to .txt file containing mapping data', type=str, required=True)
# output format: mapping txt file
parser.add_argument('-o', '--output', help='path to output file', type=str, required=True)

args = parser.parse_args()

num_vertices = 0

with open(args.edges, 'r') as f:
	for line in f.readlines():
		u, v, w = line.strip().split()
		num_vertices = max([num_vertices, int(u) + 1, int(v) + 1])

mapping = []

with open(args.mapping, 'r') as f:
	for line in f.readlines():
		mapping.append(line.strip())

mapping = mapping[:num_vertices]

with open(args.output, 'w') as f:
	for s in mapping:
		f.write('%s\n' % s)
