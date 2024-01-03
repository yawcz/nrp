#include <bits/stdc++.h>
using namespace std;

using ld = long double;

void dfs(int u, vector<vector<pair<int, int> > > &adj, vector<bool> &vis, vector<int> &tout, int &ptr) {
	if (vis[u]) {
		return;
	}
	vis[u] = true;
	for (auto [v, _] : adj[u]) {
		dfs(v, adj, vis, tout, ptr);
	}
	tout[u] = ptr++;
}

void dfs_r(int u, vector<vector<pair<int, int> > > &adj, vector<bool> &vis, vector<int> &comp, int cur_comp) {
	if (vis[u]) {
		return;
	}
	comp[u] = cur_comp;
	vis[u] = true;
	for (auto [v, _] : adj[u]) {
		dfs_r(v, adj, vis, comp, cur_comp);
	}
}

int main(int argc, char *argv[]) {
	assert(argc == 3);
	// argv[1]: path to .txt file with edge information
	// argv[2]: path to output file
	ifstream edges_in(argv[1]);
	ofstream output(argv[2], ios::trunc);
	int num_vertices = 0;
	vector<tuple<int, int, ld> > edges;
	vector<vector<pair<int, int> > > adj, adj_r;
	{
		// input edges
		int u, v;
		ld w;
		while (edges_in >> u >> v >> w) {
			num_vertices = max({num_vertices, u + 1, v + 1});
			edges.emplace_back(u, v, w);
		}
		adj.resize(num_vertices);
		adj_r.resize(num_vertices);
		for (int i = 0; i < (int)edges.size(); i++) {
			auto [u, v, w] = edges[i];
			adj[u].emplace_back(v, i);
			adj_r[v].emplace_back(u, i);
		}
	}
	vector<bool> vis(num_vertices);
	vector<int> tout(num_vertices);
	int ptr = 0;
	for (int i = 0; i < num_vertices; i++) {
		dfs(i, adj, vis, tout, ptr);
	}
	vector<int> proc(num_vertices);
	iota(proc.begin(), proc.end(), 0);
	sort(proc.begin(), proc.end(), [tout](const auto &lhs, const auto &rhs) {
		return tout[lhs] > tout[rhs];
	});
	fill(vis.begin(), vis.end(), false);
	vector<int> comp(num_vertices);
	int cur_comp = 0;
	for (int vertex : proc) {
		if (!vis[vertex]) {
			dfs_r(vertex, adj_r, vis, comp, cur_comp);
			cur_comp++;
		}
	}
	vector<int> cnt(cur_comp);
	for (int i = 0; i < num_vertices; i++) {
		cnt[comp[i]]++;
	}
	int max_comp = max_element(cnt.begin(), cnt.end()) - cnt.begin();
	for (auto [u, v, w] : edges) {
		if (comp[u] == max_comp && comp[v] == max_comp) {
			output << u << ' ' << v << ' ' << w << '\n';
		}
	}
}
