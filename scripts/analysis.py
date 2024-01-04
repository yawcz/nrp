import argparse
import math
import pandas as pd

parser = argparse.ArgumentParser(
	prog='analysis',
	description='analyses SUMO output'
)

parser.add_argument('-fcd', '--fcd', help='path to fcd output (csv format)', type=str, required=True)
parser.add_argument('-e', '--emissions', help='path to emissions output (csv format)', type=str, required=True)
parser.add_argument('-m', '--mapping', help='path to mapping file', type=str, required=True)
parser.add_argument('-r', '--request', help='path to .txt file with request information', type=str, required=True)
parser.add_argument('-a', '--assignment', help='path to .txt file with request assignment information', type=str, required=True)

args = parser.parse_args()

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

# analyse floating car data
df_fcd = pd.read_csv(args.fcd, sep=';')

for index, row in df_fcd.iterrows():
	if type(row['vehicle_lane']) == float:
		continue
	df_fcd.loc[index, 'vehicle_lane'] = row['vehicle_lane'].split('_')[0]

total_arrival_time = 0

for r_ind, assigned_vehicle in enumerate(assignment):
	sub_df_fcd = (df_fcd.loc[(df_fcd['vehicle_id'] == assigned_vehicle) & (df_fcd['vehicle_lane'] == mapping[requests[r_ind][1]])])

	arrival_time = None
	
	if sub_df_fcd.empty:
		arrival_time = df_fcd.iloc[-1]['timestep_time']
	else:
		arrival_time = sub_df_fcd.iloc[0]['timestep_time']
	
	total_arrival_time += arrival_time

print("Total arrival time (seconds):", total_arrival_time)

# analyse emissions data
df_emissions = pd.read_csv(args.emissions, sep=';')

total_co2 = 0

for index, row in df_emissions.iterrows():
	cur_co2 = float(row['vehicle_CO2'])
	if not math.isnan(cur_co2):
		total_co2 += cur_co2

print("Total CO2 emitted (mg):", total_co2)
