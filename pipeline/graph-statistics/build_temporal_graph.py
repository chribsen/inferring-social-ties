import psycopg2, psycopg2.extras
import networkx as nx
import datetime
import numpy as np

def get_connection():
  return psycopg2.connect(database="", user="", password="", host="")

conn = get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


cur.execute("""
DROP TABLE IF EXISTS stats_temporal_network;
CREATE TABLE stats_temporal_network (
  time_bin timestamp,
  node_count smallint,
  edge_count smallint,
  component_count smallint,
  degree_assortativity_coefficient float,
  avg_clustering_coefficient float,
  std_clustering_coefficient float,
  clique_count smallint,
  number_of_cliques_larger_than_2 smallint,
  largest_clique smallint,
  avg_shortest_path float
);
DROP TABLE IF EXISTS stats_temporal_network_gcc;
CREATE TABLE stats_temporal_network_gcc (
  time_bin timestamp,
  node_count smallint,
  edge_count smallint,
  degree_assortativity_coefficient float,
  avg_clustering_coefficient float,
  std_clustering_coefficient float,
  clique_count smallint,
  number_of_cliques_larger_than_2 smallint,
  largest_clique smallint,
  avg_shortest_path float
);
""")
conn.commit()

start_time = datetime.datetime(2015, 6, 27, 0, 0, 0, 0)
date_generated = [start_time + datetime.timedelta(seconds=60*10*x) for x in range(0, 1300)]

for idx, date in enumerate(date_generated):

    cur.execute(""" select pd.user_a as source, pd.user_b as target, lat, lon, c_time, dff.distinct_co_occurneces as distinct_grids, dff.same_concerts_jac, dff.same_camp_score from presentation_prediction_dyads pd
    inner join derived_friend_features dff on dff.user_a = pd.user_a and dff.user_b = pd.user_b
    where c_time between %s and %s  + (10 * interval '1 minute');
    """, (date, date,))

    G = nx.Graph()

    for point in cur.fetchall():
        G.add_edge(point['source'], point['target'])


    # Stats
    node_count = len(G.nodes())
    edge_count = len(G.edges())

    if node_count < 3:
        continue

    cliques = tuple(nx.find_cliques(G))

    component_count = nx.number_connected_components(G)
    assortativity_coef = nx.degree_assortativity_coefficient(G)
    clustering_coef_avg = nx.average_clustering(G)
    clustering_coef_stddev = np.std(list(nx.clustering(G).values()))
    number_of_cliques_larger_than_2 = len(tuple(clique for clique in cliques if len(clique) > 2))
    clique_count = len(cliques)
    largest_clique = nx.graph_clique_number(G)

    cur.execute("""INSERT INTO stats_temporal_network
                    (time_bin,
                      node_count,
                      edge_count,
                      component_count,
                      degree_assortativity_coefficient,
                      avg_clustering_coefficient,
                      std_clustering_coefficient,
                      number_of_cliques_larger_than_2,
                      largest_clique)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (date,
                                                                node_count,
                                                                edge_count,
                                                                component_count,
                                                                float(assortativity_coef),
                                                                clustering_coef_avg,
                                                                clustering_coef_stddev,
                                                                number_of_cliques_larger_than_2,
                                                                largest_clique,))

    gcc = max(nx.connected_component_subgraphs(G), key=len)
    cliques = tuple(nx.find_cliques(gcc))

    # GCC Stats
    node_count = len(gcc.nodes())
    edge_count = len(gcc.edges())
    assortativity_coef = nx.degree_assortativity_coefficient(gcc)
    clustering_coef_avg = nx.average_clustering(gcc)
    clustering_coef_stddev = np.std(list(nx.clustering(gcc).values()))
    number_of_cliques_larger_than_2 = len(tuple(clique for clique in cliques if len(clique) > 2))
    largest_clique = nx.graph_clique_number(gcc)
    avg_shortest_path = nx.average_shortest_path_length(gcc)

    cur.execute("""INSERT INTO stats_temporal_network_gcc
                    (time_bin,
                      node_count,
                      edge_count,
                      degree_assortativity_coefficient,
                      avg_clustering_coefficient,
                      std_clustering_coefficient,
                      clique_count,
                      number_of_cliques_larger_than_2,
                      largest_clique,
                      avg_shortest_path)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (date,
                                                                node_count,
                                                                edge_count,
                                                                float(assortativity_coef),
                                                                clustering_coef_avg,
                                                                clustering_coef_stddev,
                                                                clique_count,
                                                                number_of_cliques_larger_than_2,
                                                                largest_clique,
                                                                avg_shortest_path,))

    if idx % 20 == 0 and idx != 0:
        conn.commit()
        print(str(idx))

conn.commit()
conn.close()


