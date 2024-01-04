#include <bits/stdc++.h>
using namespace std;

using ld = long double;

int original_num_vertices;
vector<vector<tuple<int, ld, int> > > original_adj;
vector<bool> cache_ready;
vector<vector<ld> > cache_dist;
vector<vector<pair<int, int> > > cache_parents;
priority_queue<pair<ld, int>, vector<pair<ld, int> >, greater<pair<ld, int> > > pq;

ld dijkstra(int origin, int destination, vector<ld> &dist, vector<pair<int, int> > &parents) {
	if (cache_ready[origin]) {
		assert((int)dist.size() == (int)cache_dist[origin].size());
		copy(cache_dist[origin].begin(), cache_dist[origin].end(), dist.begin());
		copy(cache_parents[origin].begin(), cache_parents[origin].end(), parents.begin());
		return dist[destination];
	}
	dist = vector<ld>(original_num_vertices, numeric_limits<ld>::infinity());
	parents = vector<pair<int, int> >(original_num_vertices);
	dist[origin] = 0;
	pq.emplace(0, origin);
	while (!pq.empty()) {
		auto [cur_dist, u] = pq.top();
		pq.pop();
		if (cur_dist != dist[u]) {
			continue;
		}
		for (auto [v, w, edge_ind] : original_adj[u]) {
			if (dist[v] > dist[u] + w) {
				dist[v] = dist[u] + w;
				parents[v] = make_pair(u, edge_ind);
				pq.emplace(dist[v], v);
			}
		}
	}
	cache_ready[origin] = true;
	assert(cache_dist[origin].empty());
	copy(dist.begin(), dist.end(), back_inserter(cache_dist[origin]));
	copy(parents.begin(), parents.end(), back_inserter(cache_parents[origin]));
	return dist[destination];
}

ld get_cost(vector<int> &route, int capacity) {
	vector<ld> dist(original_num_vertices, numeric_limits<ld>::infinity());
	vector<pair<int, int> > parents(original_num_vertices);
	
	int passengers = 0;
	for (int i = 1; i < (int)route.size(); i++) {
		if (route[i] < 0) {
			passengers--;
		} else {
			passengers++;
		}
		
		if (passengers > capacity) {
			return numeric_limits<ld>::infinity();
		}
	}
	
	ld sf = 0, ret = 0;
	for (int i = 1; i < (int)route.size(); i++) {
		sf += dijkstra(abs(route[i - 1]) - 1, abs(route[i]) - 1, dist, parents);
		if (route[i] < 0) {
			ret += sf;
		}
	}
	
	return ret;
}

void output_2d_array(vector<vector<int> > arr, ofstream &output) {
	for (int i = 0; i < (int)arr.size(); i++) {
		for (int j = 0; j < (int)arr[0].size(); j++) {
			output << arr[i][j] << ' ';
		}
		output << '\n';
	}
}

void output_2d_array(vector<vector<ld> > &arr, ofstream &output) {
	output << fixed << setprecision(6);
	for (int i = 0; i < (int)arr.size(); i++) {
		for (int j = 0; j < (int)arr[0].size(); j++) {
			output << arr[i][j] << ' ';
		}
		output << '\n';
	}
}

int main(int argc, char *argv[]) {
	assert(argc == 7);
	// argv[1]: path to .txt file with vehicle information
	// argv[2]: path to .txt file with request information
	// argv[3]: path to .txt file with edge information
	// argv[4]: path to .txt file with mapping information
	// argv[5]: path to initial solution output file
	// argv[6]: path to new requests file
	ifstream vehicles_in(argv[1]), requests_in(argv[2]), edges_in(argv[3]), mapping_in(argv[4]);
	ofstream sol_out(argv[5], ios::trunc), requests_out(argv[6], ios::trunc);
	int num_vertices = 0;
	vector<tuple<int, int, vector<pair<int, int> > > > vehicles;
	vector<pair<int, int> > requests;
	vector<tuple<int, int, ld> > edges;
	vector<string> mapping;
	vector<vector<tuple<int, ld, int> > > adj, adj_r;

	{
		// input vehicles
		int position, capacity;
		while (vehicles_in >> position >> capacity) {
			vehicles.emplace_back(position, capacity, vector<pair<int, int> >());
		}
		vehicles_in.close();
	}
	{
		// input requests
		int origin, destination;
		while (requests_in >> origin >> destination) {
			requests.emplace_back(origin, destination);
		}
		requests_in.close();
	}
	{
		// input edges
		int u, v;
		ld w;
		while (edges_in >> u >> v >> w) {
			num_vertices = max({num_vertices, u + 1, v + 1});
			edges.emplace_back(u, v, w);
		}
		adj.resize(num_vertices);
		original_adj.resize(num_vertices);
		adj_r.resize(num_vertices);
		for (int i = 0; i < (int)edges.size(); i++) {
			auto [u, v, w] = edges[i];
			original_adj[u].emplace_back(v, w, i);
			adj[u].emplace_back(v, w, i);
			adj_r[v].emplace_back(u, w, i);
		}
		edges_in.close();
	}
	{
		// input mapping
		string s;
		while (mapping_in >> s) {
			mapping.push_back(s);
		}
		mapping_in.close();
	}
	original_num_vertices = num_vertices;
	cache_ready.resize(num_vertices);
	cache_dist.resize(num_vertices);
	cache_parents.resize(num_vertices);
	for (int v_ind = 0; v_ind < (int)vehicles.size(); v_ind++) {
		auto &[position, capacity, route] = vehicles[v_ind];
		route = {{position + 1, -1}};
	}
	
	vector<vector<int> > b(vehicles.size(), vector<int>(requests.size(), 0));
	
	vector<ld> dist(original_num_vertices, numeric_limits<ld>::infinity());
	vector<pair<int, int> > parents(original_num_vertices);
	
	for (int r_ind = 0; r_ind < (int)requests.size(); r_ind++) {
		tuple<ld, int, int, int> best_insert = make_tuple(numeric_limits<ld>::infinity(), -1, -1, -1);
		auto [origin, destination] = requests[r_ind];
		
		for (int v_ind = 0; v_ind < (int)vehicles.size(); v_ind++) {
			auto &[position, capacity, route] = vehicles[v_ind];
			
			for (int i = 1; i <= (int)route.size(); i++) {
				for (int j = i; j <= (int)route.size(); j++) {
					vector<int> tmp_route;
					for (auto &[v, _] : route) {
						tmp_route.push_back(v);
					}
					
					tmp_route.insert(tmp_route.begin() + j, -(destination + 1));
					tmp_route.insert(tmp_route.begin() + i, origin + 1);
					if (get_cost(tmp_route, capacity) != numeric_limits<ld>::infinity()) {
						best_insert = min(best_insert, make_tuple(get_cost(tmp_route, capacity), v_ind, i, j));
					}
				}
			}
		}
		
		auto &[_, best_v_ind, best_i, best_j] = best_insert;
		
		assert(best_v_ind != -1);
		
		auto route_to_edit = &get<2>(vehicles[best_v_ind]);
		
		route_to_edit->insert(route_to_edit->begin() + best_j, make_pair(-(destination + 1), r_ind));
		route_to_edit->insert(route_to_edit->begin() + best_i, make_pair(origin + 1, r_ind));
		b[best_v_ind][r_ind] = 1;
	}
	
	vector<vector<tuple<int, int, int> > > real_routes(vehicles.size());
	
	for (int v_ind = 0; v_ind < (int)vehicles.size(); v_ind++) {
		auto &[position, capacity, route] = vehicles[v_ind];
		
		vector<tuple<int, int, int> > real_route = {{position, 0, -1}};
		
		for (int i = 0; i < (int)route.size() - 1; i++) {
			if (abs(route[i].first) == abs(route[i + 1].first)) {
				real_route.emplace_back(abs(route[i].first) - 1, route[i + 1].first > 0 ? 1 : -1, route[i + 1].second);
				continue;
			}
			
			dijkstra(abs(route[i].first) - 1, abs(route[i + 1].first) - 1, dist, parents);
			
			int cur_vertex = abs(route[i + 1].first) - 1;
			vector<int> e_inds;
			
			while (cur_vertex != abs(route[i].first) - 1) {
				e_inds.push_back(parents[cur_vertex].second);
				cur_vertex = parents[cur_vertex].first;
			}
			
			reverse(e_inds.begin(), e_inds.end());
			
			for (int e_ind : e_inds) {
				real_route.emplace_back(get<1>(edges[e_ind]), 0, -1);
			}
			
			get<1>(real_route.back()) = (route[i + 1].first > 0 ? 1 : -1);
			get<2>(real_route.back()) = route[i + 1].second;
		}
		
		real_routes[v_ind] = real_route;
	}
	
	ofstream edges_out(argv[3], ios::app), mapping_out(argv[4], ios::app);
	
	for (auto &real_route : real_routes) {
		set<int> seen;
		
		for (auto &[vertex, _, __] : real_route) {
			if (seen.find(vertex) != seen.end()) {
				// make copy
				adj.push_back({});
				adj_r.push_back({});
				assert(num_vertices != vertex);
				adj[num_vertices].emplace_back(vertex, 0, -1);
				edges.emplace_back(num_vertices, vertex, 0);
				edges_out << num_vertices << ' ' << vertex << " 0\n";
				adj_r[vertex].emplace_back(num_vertices, 0, -1);
				edges.emplace_back(vertex, num_vertices, 0);
				edges_out << vertex << ' ' << num_vertices << " 0\n";
				for (auto [v, w, _] : adj[vertex]) {
					adj[num_vertices].emplace_back(v, w, -1);
					adj_r[v].emplace_back(num_vertices, w, -1);
					edges.emplace_back(num_vertices, v, w);
					edges_out << num_vertices << ' ' << v << ' ' << w << '\n';
				}
				for (auto [u, w, _] : adj_r[vertex]) {
					if (u == num_vertices) {
						continue;
					}
					adj[u].emplace_back(num_vertices, w, -1);
					adj_r[num_vertices].emplace_back(u, w, -1);
					edges.emplace_back(u, num_vertices, w);
					edges_out << u << ' ' << num_vertices << ' ' << w << '\n';
				}
				mapping_out << mapping[vertex] << '\n';
				vertex = num_vertices;
				num_vertices++;
			} else {
				seen.insert(vertex);
			}
		}
	}
	
	map<pair<int, int>, pair<ld, int> > edges_mapping;
	
	for (int e_ind = 0; e_ind < (int)edges.size(); e_ind++) {
		auto [u, v, w] = edges[e_ind];
		if (edges_mapping.find(make_pair(u, v)) == edges_mapping.end()) {
			edges_mapping[make_pair(u, v)] = make_pair(w, e_ind);
		} else {
			edges_mapping[make_pair(u, v)] = min(edges_mapping[make_pair(u, v)], make_pair(w, e_ind));
		}
	}
	
	vector<vector<int> > e(vehicles.size(), vector<int>(num_vertices, 0));
	vector<vector<int> > x(vehicles.size(), vector<int>(edges.size(), 0));
	vector<vector<ld> > t(vehicles.size(), vector<ld>(num_vertices, 0));
	vector<vector<int> > q(vehicles.size(), vector<int>(num_vertices, 0));
	
	vector<int> origin(requests.size()), destination(requests.size());
	
	for (int v_ind = 0; v_ind < (int)vehicles.size(); v_ind++) {
		auto real_route = real_routes[v_ind];
		
		for (auto [s, q, r_ind] : real_route) {
			if (r_ind != -1) {
				if (q > 0) {
					origin[r_ind] = s;
				} else {
					destination[r_ind] = s;
				}
			}
		}
		
		e[v_ind][get<0>(real_route.back())] = 1;
		
		for (int i = 0; i + 1 < (int)real_route.size(); i++) {
			assert(edges_mapping.find(make_pair(get<0>(real_route[i]), get<0>(real_route[i + 1]))) != edges_mapping.end());
			auto tmp = edges_mapping[make_pair(get<0>(real_route[i]), get<0>(real_route[i + 1]))];
			x[v_ind][tmp.second] = 1;
			t[v_ind][get<0>(real_route[i + 1])] = t[v_ind][get<0>(real_route[i])] + tmp.first;
			q[v_ind][get<0>(real_route[i + 1])] = q[v_ind][get<0>(real_route[i])] + get<1>(real_route[i + 1]);
		}
	}
	
	for (int r_ind = 0; r_ind < (int)requests.size(); r_ind++) {
		requests_out << origin[r_ind] << ' ' << destination[r_ind] << '\n';
	}
	
	cout << "Initial solution found" << endl;
	output_2d_array(b, sol_out);
	output_2d_array(e, sol_out);
	output_2d_array(x, sol_out);
	output_2d_array(t, sol_out);
	output_2d_array(q, sol_out);
}
