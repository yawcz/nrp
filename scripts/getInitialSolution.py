import argparse
import numpy as np
from heapq import heappop, heappush

parser = argparse.ArgumentParser(
	prog='car_sharing',
	description='computes optimal routes given trip, network, and vehicle information'
)

# two space-separated integers per line representing position and capacity of each vehicle
parser.add_argument('-v', '--vehicles', help='path to .txt file with vehicle information', type=str, required=True)
# two space-separated integers per line representing origin and destination of each request
parser.add_argument('-r', '--requests', help='path to .txt file with request information', type=str, required=True)
# three space-separated integers per line representing start, end, and weight of each edge
parser.add_argument('-e', '--edges', help='path to .txt file with edge information', type=str, required=True)
# output format: space-separated integers representing the route of each vehicle
parser.add_argument('-o', '--output', help='path to output file', type=str, required=True)

args = parser.parse_args()

# parameters
num_vertices = 0
vehicles_filename = args.vehicles
requests_filename = args.requests
edges_filename = args.edges

class Vehicle:
	def __init__(self, position, capacity):
		self.capacity = capacity
		self.position = position
		self.route = [position]

class Request:
	def __init__(self, origin, destination):
		self.origin = origin
		self.destination = destination

class Edge:
	def __init__(self, u, v, w):
		self.u = u
		self.v = v
		self.w = w

vehicles = []
requests = []
edges = []

for filename, data, Class in [(vehicles_filename, vehicles, Vehicle), (requests_filename, requests, Request)]:
	with open(filename) as f:
		for line in f.readlines():
			data.append(Class(*map(int, line.strip().split())))

with open(edges_filename) as f:
	for line in f.readlines():
		u, v, w = line.strip().split()
		edges.append(Edge(int(u), int(v), float(w)))

for edge in edges:
	edge.u = int(edge.u)
	edge.v = int(edge.v)
	num_vertices = max([num_vertices, edge.u + 1, edge.v + 1])

outgoing = [[] for i in range(num_vertices)]
incoming = [[] for i in range(num_vertices)]

for e_ind, edge in enumerate(edges):
	outgoing[edge.u].append(e_ind)
	incoming[edge.v].append(e_ind)

def get_dist(origin, destination):
	# uses Dijkstra's algorithm to calculate the shortest path from origin to destination
	dist, parents = np.full((num_vertices), np.infty), np.full((num_vertices, 2), [-1, -1])
	dist[origin] = 0
	
	queue = [(0, origin)]
	while queue:
		path_len, u = heappop(queue)
		
		if u == destination:
			return path_len, parents
		
		if path_len == dist[u]:
			for edge_ind in outgoing[u]:
				v, w = edges[edge_ind].v, edges[edge_ind].w
				if w + path_len < dist[v]:
					dist[v], parents[v] = w + path_len, (u, edge_ind)
					heappush(queue, (w + path_len, v))
	
	# no path found
	return np.infty, []

def get_cost(route, capacity):
	# check if capacity overflows
	passengers = 0
	for i in range(1, len(route)):
		if route[i] < 0:
			passengers -= 1
		else:
			passengers += 1
		
		if passengers > capacity:
			return np.infty
	
	sf = 0
	ret = 0
	for i in range(1, len(route)):
		sf += get_dist(abs(route[i - 1]), abs(route[i]))[0]
		if route[i] < 0:
			ret += sf
	
	return ret

while True:
	for vehicle in vehicles:
		vehicle.route = [vehicle.position]
	
	b = np.zeros((len(vehicles), len(requests)))
	e = np.zeros((len(vehicles), num_vertices))
	x = np.zeros((len(vehicles), len(edges)))
	t = np.zeros((len(vehicles), num_vertices))
	q = np.zeros((len(vehicles), num_vertices))
	
	invalid = False
	
	for r_ind, request in enumerate(requests):
		best_insert = (np.infty, -1, -1)
		
		for v_ind, vehicle in enumerate(vehicles):
			for i in range(1, len(vehicle.route) + 1):
				for j in range(i, len(vehicle.route) + 1):
					tmp = vehicle.route.copy()
					if request.destination in tmp or -request.destination in tmp or request.origin in tmp or -request.origin in tmp:
						continue
					tmp.insert(j, -request.destination)
					tmp.insert(i, request.origin)
					best_insert = min(best_insert, (get_cost(tmp, vehicle.capacity), v_ind, tmp))
		
		_, v_ind, new_route = best_insert
		
		if v_ind == -1:
			invalid = True
			break
		
		print("assigned vehicle %g to request %g" % (v_ind, r_ind))
		
		vehicles[v_ind].route = new_route
		b[v_ind][r_ind] = 1
	
	if invalid:
		continue
	
	for v_ind, vehicle in enumerate(vehicles):
		e[v_ind][abs(vehicle.route[-1])] = 1
		
		real_route = [vehicle.route[0]]
		
		for i in range(len(vehicle.route) - 1):
			parents = get_dist(abs(vehicle.route[i]), abs(vehicle.route[i + 1]))[1]
			assert(len(parents) > 0)
			
			cur_vertex = abs(vehicle.route[i + 1])
			e_inds = []
			
			while cur_vertex != abs(vehicle.route[i]):
				e_inds.append(parents[cur_vertex][1])
				cur_vertex = parents[cur_vertex][0]
			
			if i != 0:
				if vehicle.route[i] > 0:
					q[v_ind][abs(vehicle.route[i])] += 1
				else:
					q[v_ind][abs(vehicle.route[i])] -= 1
			
			e_inds.reverse()
			for e_ind in e_inds:
				x[v_ind][e_ind] = 1
				t[v_ind][edges[e_ind].v] = max(t[v_ind][edges[e_ind].v], t[v_ind][edges[e_ind].u] + edges[e_ind].w)
				q[v_ind][edges[e_ind].v] = max(q[v_ind][edges[e_ind].v], q[v_ind][edges[e_ind].u])
				real_route.append(edges[e_ind].v)
	
		if len(real_route) > len(set(real_route)):
			invalid = True
			break
	
		q[v_ind][abs(vehicle.route[-1])] -= 1
	
	if not invalid:
		with open(args.output, 'w') as f:
			def print_2d_array(arr, dtype):
				for row in arr:
					f.write(' '.join(map(str, map(dtype, row))) + '\n')
		
			print_2d_array(b, int)
			print_2d_array(e, int)
			print_2d_array(x, int)
			print_2d_array(t, float)
			print_2d_array(q, int)
		
		break
	
