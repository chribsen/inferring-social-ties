from flask import Flask, request, g, render_template, jsonify, Response, redirect, url_for
from flask.ext.login import LoginManager, UserMixin, login_required
import flask.ext.login as flask_login
from flask.ext.triangle import Triangle
from werkzeug.security import generate_password_hash, check_password_hash
import networkx as nx
import psycopg2
import psycopg2.extras
import config
import datetime
from collections import Counter
import pickle

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['PROPAGATE_EXCEPTIONS'] = True
Triangle(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = ''


class AuthUser(flask_login.UserMixin):
    def __init__(self):
        self.access_token = None

    def set_access_token(self, access_token):
        self.access_token = access_token


@login_manager.user_loader
def user_loader(username):
    if not users.get(username):
        return

    user = AuthUser()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')

    if not users.get(username):
        return

    user = AuthUser()
    user.id = username

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['access_token'] == users[username]['access_token']


def connect_db():
    return psycopg2.connect(**config.db['connection_string'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        password = users.get(request.form['email'])

        # No hash for now
        #if check_password_hash(user.password, request.form['password']):
        if password == request.form['password']:
            # Create new object to identify user
            user = AuthUser()
            user.id = request.form['email']

            # Take that object and log the user in
            flask_login.login_user(user)

            # Redirect the user to the dashboard
            return redirect(url_for('home'))

        else:
            return render_template('login.html', invalid_credentials=True)


@app.route('/home')
@login_required
def home():
    return render_template('dashboard.html')


@app.route('/trajectory')
@login_required
def trajectory():
    cur = g.db.cursor()
    cur.execute('SELECT id FROM data_users limit 100;')

    users = []
    for each in cur.fetchall():
        users.append(each[0])

    return render_template('trajectory.html', users=users)


@app.route('/trajectory-timeline')
@login_required
def trajectory_timeline():
    return render_template('trajectory_timeline.html')

@app.route('/general-summary')
@login_required
def general_summary():
    return render_template('summary.html')


@app.route('/api/trajectory', methods=['POST'])
@login_required
def get_trajectory():
    cur = g.db.cursor()
    user_ids = request.form.getlist('user-dropdown')

    if request.form.get('free-text-field'):
        user_ids = request.form.get('free-text-field').split(' ')

    response = []
    statement = "SELECT lat, lon, extract(epoch from c_time) FROM data_outside_tracker WHERE user_id=%s AND c_time > '2015-06-27' AND c_time < '2015-07-06' ORDER BY c_time ASC;"

    for each_user in user_ids:
        d_points = {'lat_lon': [], 'timestamp': [], 'user_id': each_user}
        cur.execute(statement, (each_user,))
        for each_row in cur.fetchall():
            d_points['lat_lon'].append((each_row[0], each_row[1]))
            d_points['timestamp'].append(each_row[2])

        response.append(d_points)

    return jsonify(dict(data=response))


@app.route('/api/trajectory-timeline')
@login_required
def get_trajectory_timeline():
    cur = g.db.cursor()
    response = []
    user_ids = request.args.get('user_ids').split(',')
    for each_user in user_ids:
        d_points = {
              "type": "Feature",
              "geometry": {
                "type": "MultiPoint",
                "coordinates": []
              },
              "properties": {
                "time": []
              }
            }

        cur.execute("SELECT lon, lat, extract(epoch from c_time) FROM data_tracker WHERE user_id=%s AND c_time > '2015-06-27' AND c_time < '2015-07-06' ORDER BY c_time ASC;", (each_user,))

        for each_row in cur.fetchall():
            d_points['geometry']['coordinates'].append(list((each_row[1], each_row[0])))
            d_points['properties']['time'].append(each_row[2] * 1000) # JS timestamp are in milis

        response.append(d_points)

    return jsonify(dict(data=response))


@app.route('/api/users/<user_id>/accuracy', methods=['GET'])
@login_required
def get_accuracy(user_id):
    cur = g.db.cursor()

    sql = "SELECT accuracy, extract(epoch from c_time) FROM data_tracker WHERE user_id=%s ORDER BY c_time ASC"

    cur.execute(sql, (user_id,))

    user_accuracy_timeseries = {'key': [user_id], 'values': []}
    for each_row in cur.fetchall():
        user_accuracy_timeseries['values'].append([each_row[1], each_row[0]])

    response = {'data': [user_accuracy_timeseries]}
    return jsonify(response)


@app.route('/heatmap')
@login_required
def serve_heatmap():
    return render_template('heatmap.html')


@app.route('/user-explorer')
@login_required
def serve_user_explorer():
    return render_template('user-explorer.html')


@app.route('/api/heatmap')
@login_required
def get_heatmap_data():
    cur = g.db.cursor()

    offset = int(request.args.get('offset'))

    sql = "SELECT lat, lon FROM data_tracker WHERE c_time between %s and %s;"

    start = datetime.datetime(2015, 6, 27, 14, 0, 0, 0)

    if offset != 0:
        start = start + datetime.timedelta(minutes=offset)

    end = start + datetime.timedelta(minutes=10)

    cur.execute(sql, (start, end,))

    response = {'data': {
            'points': [[str(float(x[0])), str(float(x[1]))] for x in cur.fetchall()],
            'start': start.strftime("%Y-%m-%d %H:%M:%S"),
            'end': end.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    return jsonify(response)


@app.route('/api/users/clusters', methods=['GET'])
@login_required
def get_user_clusters():
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""select distinct on (clustered_points) user_id,
                    lat,
                    lon,
                    clustered_points,
                    day_counts,
                    evening_counts,
                    night_counts
                    from derived_clusters
                    order by clustered_points desc;


  """)

    return jsonify({'data': [dict(x) for x in cur.fetchall()]})


@app.route('/movement-graph/<string:user_id>', methods=['GET'])
@login_required
def serve_movement_graph(user_id):

    if user_id and user_id !='null':
        return render_template('movement_graph.html', user_id=user_id)
    else:
        cur = g.db.cursor()
        cur.execute('SELECT id FROM data_users limit 100;')

        return render_template('movement_graph.html',
                               users=[x[0] for x in cur.fetchall()])


@app.route('/api/movement-graph/<string:user_id>')
@login_required
def get_movement_graph(user_id):

    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
    select
      grid_id as name,
      max(lat)::float as lat,
      max(lon)::float as lon,
      count(*) as value
    from data_tracker
    where user_id = %s
    group by grid_id
    having count(*) >=2 ;
    """, (user_id,))

    data = {'nodes': [dict(x) for x in cur.fetchall()]}

    cur.execute("""
    select grid_id, time_id, lat::float, lon::float, c_time
        from data_tracker
        where user_id = %s
        group by time_id, grid_id, lat, lon, c_time
        order by c_time asc
    """,(user_id,))

    resultset = tuple(dict(x) for x in cur.fetchall())

    edges = {}
    prev_node = {}
    for row in resultset:
        if prev_node:
            if edges.get((prev_node['grid_id'], row['grid_id'])):
                edges[(prev_node['grid_id'], row['grid_id'])]['value'] += 1

            else:
                edges[(prev_node['grid_id'], row['grid_id'])] = {
                    'start_lat': float(prev_node['lat']),
                    'start_lon': float(prev_node['lon']),
                    'stop_lat': row['lat'], 'stop_lon':row['lon'],
                    'value': 1
                    }

        prev_node = dict(row)

    data['edges'] = list(edges.values())


    # min max vals
    data['max_edge'] = max([x['value'] for x in data['edges']])
    data['min_edge'] = min([x['value'] for x in data['edges']])

    data['max_node'] = max([x['value'] for x in data['nodes']])
    data['min_node'] = min([x['value'] for x in data['nodes']])

    return jsonify(data)

@app.route('/api/dyads', methods=['GET'])
@login_required
def get_dyads():
    offset = int(request.args.get('offset'))
    network_type = str(request.args.get('network_type'))


    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    start = datetime.datetime(2015, 6, 27, 22, 0, 0, 0)
    if offset != 0:
        start = start + datetime.timedelta(minutes=10*offset)

    end = start + datetime.timedelta(minutes=10)

    cur.execute("""
    select pd.user_a, pd.user_b, lat, lon, c_time, dff.distinct_co_occurneces as distinct_grids, dff.same_concerts_jac, dff.same_camp_score from presentation_prediction_dyads pd
    inner join derived_friend_features dff on dff.user_a = pd.user_a and dff.user_b = pd.user_b
        where c_time between %s and %s
    """, (start, end, ))

    G = pickle.load(open("friends_graph.pkl", "rb")).to_undirected()

    nodes = []
    edges = []
    points = []

    degrees = G.degree()

    nodes_added = set()

    for dyads in cur.fetchall():
        points.append({
            'user_a': dyads['user_a'],
            'user_b': dyads['user_b'],
            'lat': float(dyads['lat']),
            'lon': float(dyads['lon'])
        })

        current_nodes = [dyads['user_a'], dyads['user_b']]
        # Add all neighbors

        if network_type == 'common':
            for neighbor in nx.common_neighbors(G, dyads['user_a'], dyads['user_b']):
                if neighbor not in nodes_added:
                    nodes.append((neighbor, 'blue'))
                    nodes_added.add(neighbor)

                for node in current_nodes:
                    edges.append((node, neighbor, 1))
        elif network_type=='no-neighbors':
            pass

        else:
            for node in current_nodes:
                for neighbor in G.neighbors(node):
                    if neighbor not in nodes_added and neighbor not in current_nodes:
                        nodes.append((neighbor, 'blue'))
                        nodes_added.add(neighbor)

                    edges.append((node, neighbor, 1))


        for node in current_nodes:
            if node not in nodes_added:
                nodes.append((node, 'red'))
                nodes_added.add(node)



        edges.append((dyads['user_a'], dyads['user_b'], dyads['distinct_grids']))

    new_nodes = [{'id': x[0], 'label':x[0], 'value': degrees[x[0]], 'color': x[1] } for x in list(set(nodes))]
    new_edges = []
    ids = []
    for edge in edges:
        _id = str(hash(':'.join([str(edge[0]), str(edge[1])])))
        if not _id in ids:
            ids.append(_id)
            new_edges.append({'from': edge[0], 'to': edge[1], 'value': edge[2], 'id': _id})

    print(str(sorted(Counter(ids).items())))

    response = {
            'points': points,
            'network': {
                'nodes': new_nodes,
                'edges': new_edges
            },
            'start': start.strftime("%Y-%m-%d %H:%M:%S"),
            'end': end.strftime("%Y-%m-%d %H:%M:%S")
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
