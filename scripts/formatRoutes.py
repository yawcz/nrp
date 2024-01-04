import argparse
import pandas as pd
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(
	prog='format_routes',
	description='formats routes from txt to SUMO-friendly format'
)

parser.add_argument('-r', '--routes', help='path to .txt file containing route data', type=str, required=True)
parser.add_argument('-m', '--mapping', help='path to .txt file containing mapping data', type=str, required=True)
# output format: xml route file
parser.add_argument('-o', '--output', help='path to output file', type=str, required=True)

args = parser.parse_args()

mapping = []

with open(args.mapping, 'r') as f:
	for line in f.readlines():
		mapping.append(line.strip())

routes = ET.Element('routes')

vType = ET.SubElement(routes, 'vType')
vType.set('id', 'type1')
vType.set('accel', '0.8')
vType.set('decel', '4.5')
vType.set('sigma', '0.5')
vType.set('length', '5')
vType.set('maxSpeed', '70')
vType.set('vClass', 'ignoring')

def make_unique(route):
	ret = []
	
	for i in route:
		if len(ret) == 0 or ret[-1] != i:
			ret.append(i)
	
	return ret

with open(args.routes, 'r') as f:
	for index, line in enumerate(f.readlines()):
		vehicle = ET.SubElement(routes, 'vehicle')
		vehicle.set('id', str(index))
		vehicle.set('type', 'type1')
		vehicle.set('depart', '0')
		
		route = ET.SubElement(vehicle, 'route')
		route.set('edges', ' '.join(make_unique(list(map(lambda x : mapping[int(x)], line.strip().split())))))

with open(args.output, 'wb') as f:
    f.write(ET.tostring(routes))
