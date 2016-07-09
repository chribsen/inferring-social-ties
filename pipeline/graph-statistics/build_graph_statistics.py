import psycopg2, psycopg2.extras
import networkx as nx
import collections
import community
import json
import pickle

conn = psycopg2.connect(database="", user="", password="", host="")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cur.execute("""
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_degree;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_di_in_degree;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_di_out_degree;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_degree_centrality;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_pagerank_centrality;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_betweenness_centrality;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_closeness_centrality;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_eigenvector_centrality;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_clustering_coef;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_square_clustering_coef;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_louvain_community_id;
ALTER TABLE data_users DROP COLUMN IF EXISTS networkx_component_id;


ALTER TABLE data_users ADD COLUMN networkx_degree smallint;
ALTER TABLE data_users ADD COLUMN networkx_di_in_degree smallint;
ALTER TABLE data_users ADD COLUMN networkx_di_out_degree smallint;

ALTER TABLE data_users ADD COLUMN networkx_degree_centrality FLOAT;
ALTER TABLE data_users ADD COLUMN networkx_pagerank_centrality FLOAT;
ALTER TABLE data_users ADD COLUMN networkx_betweenness_centrality FLOAT;
ALTER TABLE data_users ADD COLUMN networkx_closeness_centrality FLOAT;
ALTER TABLE data_users ADD COLUMN networkx_eigenvector_centrality FLOAT;

ALTER TABLE data_users ADD COLUMN networkx_clustering_coef FLOAT;
ALTER TABLE data_users ADD COLUMN networkx_square_clustering_coef FLOAT;

ALTER TABLE data_users ADD COLUMN networkx_louvain_community_id SMALLINT;
ALTER TABLE data_users ADD COLUMN networkx_component_id SMALLINT;

""")

conn.commit()

cur.execute("""SELECT user_a, user_b, is_friend_ratio FROM derived_dyads where is_friend_ratio>=0.65""")

G = nx.Graph()
Di_G = nx.DiGraph()

for dyad in cur.fetchall():
    G.add_edge(int(dyad['user_a']), int(dyad['user_b']), weight=float(dyad['is_friend_ratio']))
    Di_G.add_edge(int(dyad['user_a']), int(dyad['user_b']), weight=float(dyad['is_friend_ratio']))

# Add degree, in-degree, out-degree
degrees = G.degree()
in_degree = Di_G.in_degree()
out_degree = Di_G.out_degree()

# Centralities
degree_centr = nx.degree_centrality(G)
pagerank_centr = nx.pagerank(G)
betweenness_centr = nx.betweenness_centrality(G)
closeness_centr = nx.closeness_centrality(G)
eigenvector_centr = nx.eigenvector_centrality(G, max_iter=1000)

# Clustering
clustering = nx.clustering(G)
square_clustering = nx.square_clustering(G)

# Louvain community
best_partition = community.best_partition(G)
dendrogram = community.generate_dendrogram(G)
# Print dendogram to file
with open('dendogram-best-partition_final_db', 'w+') as f:
    f.write(json.dumps(dendrogram, indent=2))
    f.close()

# Print partition of dendogram
with open('dendogram-best-partition-at-level_final_db', 'w+') as f:
    for level in range(len(dendrogram) - 1) :
        s = "partition at level " + str(level) + " is " + str(community.partition_at_level(dendrogram, level))  # NOQA
        f.write(s)
        f.write('\n')
    f.close()

# Print modularity to file
with open('modularity-best-partition_final_db', 'w+') as f:
    f.write(str(community.modularity(best_partition,G)))
    f.close()

# Components
total_number_of_nodes_in_components = 0
components = {}
for component_id, component in enumerate(nx.connected_components(G)):
    for node in component:
        components[node] = component_id

    total_number_of_nodes_in_components += len(component)


print('In component: ' + str(total_number_of_nodes_in_components))
print('In network: ' + str(len(G.nodes())))


for i, node in enumerate(G.nodes()):
    cur.execute("""UPDATE data_users SET
                    networkx_degree=%s,
                    networkx_di_in_degree=%s,
                    networkx_di_out_degree=%s,
                    networkx_pagerank_centrality=%s,
                    networkx_betweenness_centrality=%s,
                    networkx_closeness_centrality=%s,
                    networkx_eigenvector_centrality=%s,
                    networkx_clustering_coef=%s,
                    networkx_square_clustering_coef=%s,
                    networkx_louvain_community_id=%s,
                    networkx_component_id=%s
                    """, (degrees[node],
                          in_degree[node],
                          out_degree[node],
                          pagerank_centr[node],
                          betweenness_centr[node],
                          closeness_centr[node],
                          eigenvector_centr[node],
                          clustering[node],
                          square_clustering[node],
                          best_partition[node],
                          components[node]))
    if i % 100 == 0:
        conn.commit()
        print(str(float(i)/float(G.number_of_nodes())))
conn.commit()

conn.close()





