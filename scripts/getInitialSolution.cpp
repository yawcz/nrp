#include <bits/stdc++.h>
using namespace std;

using ld = long double;

priority_queue<pair<ld, int>, vector<pair<ld, int> >, greater<pair<ld, int> > > pq;

ld dijkstra(int origin, int destination, vector<vector<tuple<int, int, ld> > > &adj, vector<ld> &dist, vector<pair<int, int> > &parents) {
	int num_vertices = (int)adj.size();
	dist = vector<ld>(num_vertices, numeric_limits<ld>::infinity());
	parents = vector<pair<int, int> >(num_vertices);
	dist[origin] = 0;
	pq.emplace(0, origin);
	while (!pq.empty()) {
		auto [cur_dist, u] = pq.top();
		pq.pop();
		if (cur_dist != dist[u]) {
			continue;
		}
		if (u == destination) {
			return cur_dist;
		}
		for (auto [v, w, edge_ind] : adj[u]) {
			if (dist[v] > dist[u] + w) {
				dist[v] = dist[u] + w;
				parents[v] = make_pair(u, edge_ind);
				pq.emplace(dist[v], v);
			}
		}
	}
	return numeric_limits<ld>::infinity();
}

ld get_cost(vector<int> &route, int capacity, vector<vector<tuple<int, int, ld> > > &adj) {
	vector<ld> dist;
	vector<pair<int, int> > parents;
	
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
		sf += dijkstra(abs(route[i - 1]), abs(route[i]), adj, dist, parents);
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
	assert(argc == 5);
	// argv[1]: path to .txt file with vehicle information
	// argv[2]: path to .txt file with request information
	// argv[3]: path to .txt file with edge information
	// argv[4]: path to output file
	ifstream vehicles_in(argv[1]), requests_in(argv[2]), edges_in(argv[3]);
	ofstream output(argv[4], ios::trunc);
	int num_vertices = 0;
	vector<tuple<int, int, vector<int> > > vehicles;
	vector<pair<int, int> > requests;
	vector<tuple<int, int, ld> > edges;
	vector<vector<tuple<int, int, ld> > > adj;
	
	vector<ld> dist(num_vertices, numeric_limits<ld>::infinity());
	vector<pair<int, int> > parents(num_vertices);

	{
		// input vehicles
		int position, capacity;
		while (vehicles_in >> position >> capacity) {
			vehicles.emplace_back(position, capacity, vector<int>());
		}
	}
	{
		// input requests
		int origin, destination;
		while (requests_in >> origin >> destination) {
			requests.emplace_back(origin, destination);
		}
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
		for (int i = 0; i < (int)edges.size(); i++) {
			auto [u, v, w] = edges[i];
			adj[u].emplace_back(v, w, i);
		}
	}
	for (int v_ind = 0; v_ind < (int)vehicles.size(); v_ind++) {
		auto &[position, capacity, route] = vehicles[v_ind];
		route = {position};
	}
	
	vector<vector<int> > b(vehicles.size(), vector<int>(requests.size(), 0));
	vector<vector<int> > e(vehicles.size(), vector<int>(num_vertices, 0));
	vector<vector<int> > x(vehicles.size(), vector<int>(edges.size(), 0));
	vector<vector<ld> > t(vehicles.size(), vector<ld>(num_vertices, 0));
	vector<vector<int> > q(vehicles.size(), vector<int>(num_vertices, 0));
	
	for (int r_ind = 0; r_ind < (int)requests.size(); r_ind++) {
		tuple<ld, int, vector<int> > best_insert = make_tuple(numeric_limits<ld>::infinity(), -1, vector<int>());
		auto [origin, destination] = requests[r_ind];
		
		for (int v_ind = 0; v_ind < (int)vehicles.size(); v_ind++) {
			auto &[position, capacity, route] = vehicles[v_ind];
			
			for (int i = 1; i <= (int)route.size(); i++) {
				for (int j = i; j <= (int)route.size(); j++) {
					vector<int> tmp_route;
					copy(route.begin(), route.end(), back_inserter(tmp_route));
					
					tmp_route.insert(tmp_route.begin() + j, -destination);
					tmp_route.insert(tmp_route.begin() + i, origin);
					best_insert = min(best_insert, make_tuple(get_cost(tmp_route, capacity, adj), v_ind, tmp_route));
				}
			}
		}
		
		auto &[_, best_v_ind, best_new_route] = best_insert;
		
		assert(best_v_ind != -1);
		
		get<2>(vehicles[best_v_ind]) = best_new_route;
		b[best_v_ind][r_ind] = 1;
	}
	
	for (int v_ind = 0; v_ind < (int)vehicles.size(); v_ind++) {
		auto &[position, capacity, route] = vehicles[v_ind];
		
		e[v_ind][abs(route.back())] = 1;
		
		vector<int> real_route = {position};
		
		for (int i = 0; i < (int)route.size() - 1; i++) {
			dijkstra(abs(route[i]), abs(route[i + 1]), adj, dist, parents);
			
			int cur_vertex = abs(route[i + 1]);
			vector<int> e_inds;
			
			while (cur_vertex != abs(route[i])) {
				e_inds.push_back(parents[cur_vertex].second);
				cur_vertex = parents[cur_vertex].first;
			}
			
			if (i != 0) {
				if (route[i] > 0) {
					q[v_ind][abs(route[i])]++;
				} else {
					q[v_ind][abs(route[i])]--;
				}
			}
			
			reverse(e_inds.begin(), e_inds.end());
			
			for (int e_ind : e_inds) {
				x[v_ind][e_ind] = 1;
				auto [u, v, w] = edges[e_ind];
				t[v_ind][v] = max(t[v_ind][v], t[v_ind][u] + w);
				q[v_ind][v] = max(q[v_ind][v], q[v_ind][u]);
				real_route.push_back(v);
			}
		}
		
		sort(real_route.begin(), real_route.end());
		assert(unique(real_route.begin(), real_route.end()) == real_route.end());
		
		q[v_ind][abs(route.back())]--;
	}
	
	cout << "Initial solution found" << endl;
	output_2d_array(b, output);
	output_2d_array(e, output);
	output_2d_array(x, output);
	output_2d_array(t, output);
	output_2d_array(q, output);
}
