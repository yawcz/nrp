#include <cassert>
#include <fstream>
#include <numeric>
#include <tuple>
#include <vector>

void dfs(int u, std::vector<std::vector<std::pair<int, int> > > &adj, std::vector<bool> &vis, std::vector<int> &tout, int &ptr) {
	if (vis[u]) {
		return;
	}
	vis[u] = true;
	for (auto [v, _] : adj[u]) {
		dfs(v, adj, vis, tout, ptr);
	}
	tout[u] = ptr++;
}

// depth-first search on transposed graph
void dfs_r(int u, std::vector<std::vector<std::pair<int, int> > > &adj, std::vector<bool> &vis, std::vector<int> &comp, int cur_comp) {
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
	std::ifstream edges_in(argv[1]);
	std::ofstream output(argv[2], std::ios::trunc);
	int num_vertices = 0;
	std::vector<std::tuple<int, int, long double> > edges;
	std::vector<std::vector<std::pair<int, int> > > adj, adj_r;
	{
		// input edges
		int u, v;
		long double w;
		while (edges_in >> u >> v >> w) {
			num_vertices = std::max({num_vertices, u + 1, v + 1});
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
	
	// kosaraju's algorithm
	std::vector<bool> vis(num_vertices);
	std::vector<int> tout(num_vertices);
	int ptr = 0;
	for (int i = 0; i < num_vertices; i++) {
		dfs(i, adj, vis, tout, ptr);
	}
	std::vector<int> proc(num_vertices);
	iota(proc.begin(), proc.end(), 0);
	sort(proc.begin(), proc.end(), [tout](const auto &lhs, const auto &rhs) {
		return tout[lhs] > tout[rhs];
	});
	fill(vis.begin(), vis.end(), false);
	std::vector<int> comp(num_vertices);
	int cur_comp = 0;
	for (int vertex : proc) {
		if (!vis[vertex]) {
			dfs_r(vertex, adj_r, vis, comp, cur_comp);
			cur_comp++;
		}
	}
	
	// extract largest SCC
	std::vector<int> cnt(cur_comp);
	for (int i = 0; i < num_vertices; i++) {
		cnt[comp[i]]++;
	}
	int max_comp = max_element(cnt.begin(), cnt.end()) - cnt.begin();
	
	// output edges that are in the maximum SCC
	for (auto [u, v, w] : edges) {
		if (comp[u] == max_comp && comp[v] == max_comp) {
			output << u << ' ' << v << ' ' << w << '\n';
		}
	}
}
