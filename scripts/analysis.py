import argparse
import pandas as pd

parser = argparse.ArgumentParser(
	prog='analysis',
	description='analyses SUMO output'
)

parser.add_argument('-fcd', '--fcd', help='path to fcd output (csv format)', type=str, required=True)
parser.add_argument('-m', '--mapping', help='path to mapping file', type=str, required=True)
parser.add_argument('-r', '--request', help='path to .txt file with request information', type=str, required=True)
parser.add_argument('-a', '--assignment', help='path to .txt file with request assignment information', type=str, required=True)

args = parser.parse_args()

df = pd.read_csv(args.fcd, sep=';')

mapping = []
requests = []
assignment = []

with open(args.mapping, 'r') as f:
	for line in f.readlines():
		mapping.append(line.strip())

with open(args.request, 'r') as f:
	for line in f.readlines():
		requests.append(list(map(int, line.strip().split())))

with open(args.assignment, 'r') as f:
	for line in f.readlines():
		assignment.append(int(line.strip()))

for index, row in df.iterrows():
	if type(row['vehicle_lane']) == float:
		continue
	df.loc[index, 'vehicle_lane'] = row['vehicle_lane'].split('_')[0]

total_arrival_time = 0

for r_ind, assigned_vehicle in enumerate(assignment):
	sub_df = (df.loc[(df['vehicle_id'] == assigned_vehicle) & (df['vehicle_lane'] == mapping[requests[r_ind][1]])])
	total_arrival_time += sub_df.iloc[0]['timestep_time']

print("Total arrive time: ", total_arrival_time)
