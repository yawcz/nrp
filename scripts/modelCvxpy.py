import argparse
import cvxpy as cp
import numpy as np

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
INFTY = 1e6 # tune if needed

class Vehicle:
	def __init__(self, position, capacity):
		self.position = position
		self.capacity = capacity

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

# define model variables
b = cp.Variable((len(vehicles), len(requests)), boolean=True)
e = cp.Variable((len(vehicles), num_vertices), nonneg=True)
x = cp.Variable((len(vehicles), len(edges)), boolean=True)
t = cp.Variable((len(vehicles), num_vertices), nonneg=True)
q = cp.Variable((len(vehicles), num_vertices), nonneg=True)

# define objective
objective = cp.Minimize(cp.sum([t[k_ind, r.destination] for k_ind in range(len(vehicles)) for r in requests]))

# define constraints
constraints = []

# requests are assigned to exactly one vehicle
for r_ind in range(len(requests)):
	constraints.append(cp.sum([b[k_ind, r_ind] for k_ind in range(len(vehicles))]) == 1)

# vehicles have exactly one ending vertex
for k_ind in range(len(vehicles)):
	constraints.append(cp.sum([e[k_ind, v_ind] for v_ind in range(num_vertices)]) == 1)

# flow conservation
for v_ind in range(num_vertices):
	for k_ind, k in enumerate(vehicles):
		if v_ind != k.position:
			constraints.append(cp.sum([x[k_ind, incoming_e_ind] for incoming_e_ind in incoming[v_ind]]) - cp.sum([x[k_ind, outgoing_e_ind] for outgoing_e_ind in outgoing[v_ind]]) == e[k_ind, v_ind])

# no incoming flow to start vertex
for k_ind, k in enumerate(vehicles):
	constraints.append(cp.sum([x[k_ind, incoming_e_ind] for incoming_e_ind in incoming[k.position]]) == 0)

# generate outgoing flow from start vertex
for k_ind, k in enumerate(vehicles):
	constraints.append(cp.sum([x[k_ind, outgoing_e_ind] for outgoing_e_ind in outgoing[k.position]]) <= 1)

# vehicle visits origin of request
for k_ind, k in enumerate(vehicles):
	for r_ind, r in enumerate(requests):
		if r.origin != k.position:
			constraints.append(cp.sum([x[k_ind, outgoing_e_ind] for outgoing_e_ind in outgoing[r.origin]]) >= 1 - INFTY * (1 - b[k_ind, r_ind]))

# vehicle visits destination of request
for k_ind, k in enumerate(vehicles):
	for r_ind, r in enumerate(requests):
		if r.destination != k.position:
			constraints.append((cp.sum([x[k_ind, incoming_e_ind] for incoming_e_ind in incoming[r.destination]]) >= 1 - INFTY * (1 - b[k_ind, r_ind])))

# time of arrival corresponds to route
for e_ind, edge in enumerate(edges):
	for k_ind in range(len(vehicles)):
		constraints.append(t[k_ind, edge.v] >= t[k_ind, edge.u] + edge.w - INFTY * (1 - x[k_ind, e_ind]))

# arrive at destination later than origin
for r_ind, r in enumerate(requests):
	for k_ind in range(len(vehicles)):
		constraints.append(t[k_ind, r.destination] >= t[k_ind, r.origin] - INFTY * (1 - b[k_ind, r_ind]))

# number of passengers does not exceed capacity
for v_ind in range(num_vertices):
	for k_ind, k in enumerate(vehicles):
		constraints.append(q[k_ind, v_ind] <= k.capacity)

# passengers enter vehicle at start vertex
for k_ind, k in enumerate(vehicles):
	constraints.append(q[k_ind, k.position] == cp.sum([b[k_ind, r_ind] for r_ind, r in enumerate(requests) if r.origin == k.position]))

# passengers enter and alight vehicle
for e_ind, edge in enumerate(edges):
	for k_ind in range(len(vehicles)):
		constraints.append(q[k_ind, edge.v] >= q[k_ind, edge.u] + cp.sum([b[k_ind, r_ind] for r_ind, r in enumerate(requests) if r.origin == edge.v]) - cp.sum([b[k_ind, r_ind] for r_ind, r in enumerate(requests) if r.destination == edge.v]) - INFTY * (1 - x[k_ind, e_ind]))

problem = cp.Problem(objective, constraints)

problem.solve(solver=cp.COPT, Threads=20, MipTasks=20, Presolve=3, SolTimeLimit=120, verbose=True)

print('\nMinimum total arrival time: %g\n' % problem.value)

for r_ind, r in enumerate(requests):
	assigned_vehicle = -1
	for k_ind in range(len(vehicles)):
		if b[k_ind, r_ind].value == 1:
			assigned_vehicle = k_ind
	print('Request #%g (from vertex %g to %g) assigned to vehicle %g, pick-up time: %g, drop-off time: %g' % (r_ind, r.origin, r.destination, assigned_vehicle, t[assigned_vehicle, r.origin].value, t[assigned_vehicle, r.destination].value))

with open(args.output, 'w') as f:
	for k_ind, k in enumerate(vehicles):
		to = [-1 for i in range(num_vertices)]
		
		for e_ind, e in enumerate(edges):
			if x[k_ind, e_ind].value:
				to[e.u] = e.v
		
		current_position = k.position
		
		while current_position != -1:
			f.write('%s ' % current_position)
			current_position = to[current_position]
		
		f.write('\n')
