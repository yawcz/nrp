import argparse
from xml.sax import make_parser, handler

parser = argparse.ArgumentParser(
	prog='get_graph',
	description='get the underlying graph of a given network'
)

parser.add_argument('-n', '--net', help='path to .net.xml file with network information', type=str, required=True)
# output format: three space-separated strings/floats per line representing start, end, and weight of each edge
parser.add_argument('-go', '--graph_output', help='path to graph output file', type=str, required=True)
# output format: one string per line representing the IDs of each vertex
parser.add_argument('-mo', '--mapping_output', help='path to mapping output file', type=str, required=True)

args = parser.parse_args()

class NetReader(handler.ContentHandler):
	def __init__(self):
		self._nb = {}
		self._weight = {}

	def startElement(self, name, attrs):
		if 'length' in attrs.keys():
			self._weight[attrs['id'].split('_')[0]] = float(attrs['length']) / float(attrs['speed'])
		if name == 'edge' and ('function' not in attrs or attrs['function'] != 'internal'):
			self._nb[attrs['id']] = set()
		elif name == 'connection':
			if attrs['from'] in self._nb and attrs['to'] in self._nb:
				self._nb[attrs['from']].add((attrs['to'], self._weight[attrs['to']]))

	def output_graph(self, graph_output_filename, mapping_output_filename):
		mapping = {}
		
		with open(mapping_output_filename, 'w') as mapping_output_file:
			for vertex in self._nb.keys():
				mapping_output_file.write('%s\n' % vertex)
				mapping[vertex] = len(mapping)
		
		num_vertices = 0
		num_edges = 0
		
		with open(graph_output_filename, 'w') as graph_output_file:
			for vertex, outgoing_edges in self._nb.items():
				num_vertices += 1
				for outgoing_vertex, weight in outgoing_edges:
					num_edges += 1
					graph_output_file.write('%s %s %f\n' % (mapping[vertex], mapping[outgoing_vertex], weight))
		
		return (num_vertices, num_edges)

net = NetReader()

xml_parser = make_parser()
xml_parser.setContentHandler(net)

print('Reading network...')
xml_parser.parse(args.net)
print('Network loaded')

num_vertices, num_edges = net.output_graph(args.graph_output, args.mapping_output)

print('Number of vertices: %g, Number of edges: %g' % (num_vertices, num_edges))
