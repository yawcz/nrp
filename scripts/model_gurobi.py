import argparse
import gurobipy as gp
from gurobipy import *

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

m = gp.Model('car_sharing')

m.setParam('IntegralityFocus', 1)
m.setParam('MIPFocus', 1)

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
b = m.addVars(len(vehicles), len(requests), vtype=GRB.BINARY, name='b')
e = m.addVars(len(vehicles), num_vertices, vtype=GRB.BINARY, name='e')
x = m.addVars(len(vehicles), len(edges), vtype=GRB.BINARY, name='x')
t = m.addVars(len(vehicles), num_vertices, vtype=GRB.CONTINUOUS, lb=0, name='t')
q = m.addVars(len(vehicles), num_vertices, vtype=GRB.CONTINUOUS, lb=0, name='q')

# define objective
m.setObjective(quicksum(t[k_ind, r.destination] for k_ind in range(len(vehicles)) for r in requests), GRB.MINIMIZE)

# define constraints
m.addConstrs(((quicksum(b[k_ind, r_ind] for k_ind in range(len(vehicles))) == 1)
	for r_ind in range(len(requests))),
	name='requests_assigned_to_exactly_one_vehicle')

m.addConstrs(((quicksum(e[k_ind, v_ind] for v_ind in range(num_vertices)) == 1)
	for k_ind in range(len(vehicles))),
	name='vehicles_have_exactly_one_ending_vertex')

m.addConstrs(((quicksum(x[k_ind, incoming_e_ind] for incoming_e_ind in incoming[v_ind]) - quicksum(x[k_ind, outgoing_e_ind] for outgoing_e_ind in outgoing[v_ind]) == e[k_ind, v_ind])
	for v_ind in range(num_vertices)
	for k_ind, k in enumerate(vehicles)
	if v_ind != k.position),
	name='flow_conservation')

m.addConstrs(((quicksum(x[k_ind, incoming_e_ind] for incoming_e_ind in incoming[k.position]) == 0)
	for k_ind, k in enumerate(vehicles)),
	name='no_incoming_flow_to_start_vertex')

m.addConstrs(((quicksum(x[k_ind, outgoing_e_ind] for outgoing_e_ind in outgoing[k.position]) <= 1)
	for k_ind, k in enumerate(vehicles)),
	name='generate_outgoing_flow_from_start_vertex')

m.addConstrs(((b[k_ind, r_ind] == 1) >> (quicksum(x[k_ind, outgoing_e_ind] for outgoing_e_ind in outgoing[r.origin]) >= 1)
	for k_ind, k in enumerate(vehicles)
	for r_ind, r in enumerate(requests)
	if r.origin != k.position),
	name='vehicle_visits_origin_of_request')

m.addConstrs(((b[k_ind, r_ind] == 1) >> (quicksum(x[k_ind, incoming_e_ind] for incoming_e_ind in incoming[r.destination]) >= 1)
	for k_ind, k in enumerate(vehicles)
	for r_ind, r in enumerate(requests)
	if r.destination != k.position),
	name='vehicle_visits_destination_of_request')

m.addConstrs((((x[k_ind, e_ind] == 1) >> (t[k_ind, e.v] >= t[k_ind, e.u] + e.w))
	for e_ind, e in enumerate(edges)
	for k_ind in range(len(vehicles))),
	name='time_of_arrival_corresponds_to_route')

m.addConstrs((((b[k_ind, r_ind] == 1) >> (t[k_ind, r.destination] >= t[k_ind, r.origin]))
	for r_ind, r in enumerate(requests)
	for k_ind in range(len(vehicles))),
	name='arrive_at_destination_later_than_origin')

m.addConstrs(((q[k_ind, v_ind] <= k.capacity)
	for v_ind in range(num_vertices)
	for k_ind, k in enumerate(vehicles)),
	name='number_of_passengers_does_not_exceed_capacity')

m.addConstrs(((q[k_ind, k.position] == quicksum(b[k_ind, r_ind] for r_ind, r in enumerate(requests) if r.origin == k.position)
	for k_ind, k in enumerate(vehicles))),
	name='passengers_enter_vehicle_at_start_vertex')

m.addConstrs(((x[k_ind, e_ind] == 1) >> (q[k_ind, e.v] >= q[k_ind, e.u] + quicksum(b[k_ind, r_ind] for r_ind, r in enumerate(requests) if r.origin == e.v) - quicksum(b[k_ind, r_ind] for r_ind, r in enumerate(requests) if r.destination == e.v))
	for e_ind, e in enumerate(edges)
	for k_ind in range(len(vehicles))),
	name='passengers_enter_and_alight_vehicle')

# find optimal solution
m.optimize()

# check quality of solution found
m.printQuality()

print('\nMinimum total arrival time: %g\n' % m.ObjVal)

for r_ind, r in enumerate(requests):
	assigned_vehicle = -1
	for k_ind in range(len(vehicles)):
		if b[k_ind, r_ind].X == 1:
			assigned_vehicle = k_ind
	print('Request #%g (from vertex %g to %g) assigned to vehicle %g, pick-up time: %g, drop-off time: %g' % (r_ind, r.origin, r.destination, assigned_vehicle, t[assigned_vehicle, r.origin].X, t[assigned_vehicle, r.destination].X))

with open(args.output, 'w') as f:
	for k_ind, k in enumerate(vehicles):
		to = [-1 for i in range(num_vertices)]
		
		for e_ind, e in enumerate(edges):
			if x[k_ind, e_ind].X:
				to[e.u] = e.v
		
		current_position = k.position
		
		while current_position != -1:
			f.write('%s ' % current_position)
			current_position = to[current_position]
		
		f.write('\n')
