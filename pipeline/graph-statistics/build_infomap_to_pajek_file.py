import psycopg2, psycopg2.extras
import networkx as nx
import datetime
import numpy as np
import sys


filename = sys.argv[1]

def get_connection():
  return psycopg2.connect(database="", user="", password="", host="")

conn = get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cur.execute("""SELECT dd.user_a, dd.user_b, dd.is_friend_ratio FROM derived_dyads dd
                INNER JOIN derived_friend_features dff ON dff.user_a = dd.user_a AND dff.user_b = dd.user_b
                WHERE dd.is_friend_ratio >= 0.65""")

G = nx.Graph()
weights = dict()
remap = {}
i = 1


for dyad in cur.fetchall():

    weights[(dyad['user_a'], dyad['user_b'])] = dyad['is_friend_ratio']
    G.add_edge(dyad['user_a'], dyad['user_b'])



with open(filename, 'w') as f:

    # Add nodes
    f.write('*Vertices {0}'.format(str(G.number_of_nodes())))
    f.write('\n')
    for node in G.nodes():
        remap[node] = i
        i += 1

        f.write('{0} "{1}"'.format(str(remap[node]), node))
        f.write('\n')

    # Add edges
    f.write('*Edges {0}'.format(str(G.number_of_edges())))
    f.write('\n')
    for edge in G.edges():

        weight = weights.get(edge) if weights.get(edge) else weights.get(tuple(reversed(edge)))
        f.write('{source} {target} {weight}'.format(source=remap[edge[0]], target=remap[edge[1]], weight=weight))
        f.write('\n')

    f.close()





