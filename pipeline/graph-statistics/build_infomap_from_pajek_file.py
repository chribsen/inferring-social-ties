import sys
import psycopg2, psycopg2.extras

filename = sys.argv[1]
markov_time = float(sys.argv[2])

data = []

with open(filename, 'r') as f:

    for i, line in enumerate(f.read().split('\n')):
        if line == '' or i <= 1:
            continue

        cols = line.split(' ')

        communities = tuple(int(x) for x in cols[0].split(':'))
        node_name = cols[2][1:-1] # remove quotes
        item = dict(path=communities, flow=float(cols[1]), name=node_name)
        data.append(item)

    f.close()


def get_connection():
    return psycopg2.connect(database="", user="", password="", host="")

conn = get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Setup DDL
setup_ddl=False
if setup_ddl:
    cur.execute("""
    drop table if EXISTS community_user;
    drop table if EXISTS community;

    create table community (
      community_id smallint primary key,
      size smallint
    );
    create table community_user (
      community_id smallint references community(community_id),
      user_id integer,
      flow float,
      rank_for_finest_community smallint,
      markov_time numeric(4,2)
    );
    """)
conn.commit()

inserted_communities = set()
for i, node in enumerate(data):
    for path in node['path'][:-1]:
        cur.execute("""
          insert into community_user
          (community_id,
          user_id,flow,
          rank_for_finest_community,
          markov_time)
          VALUES (%s,%s,%s,%s,%s)""",
                    (path,
                     int(node['name']),
                     node['flow'],
                     int(node['path'][-1]),
                     markov_time,))

    if i % 10 == 0:
        print(str(float(i)/len(data)))

conn.commit()