import psycopg2, psycopg2.extras, pickle
import networkx as nx
from collections import defaultdict


class Database():

    def __init__(self):
        self.conn = psycopg2.connect(database="", user="", password="", host="")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


class Concert:

    def __init__(self):
        self.artist_name = None
        self.start_time = None
        self.stage = None
        self.spotify_followers = None
        self.spotify_popularity = None
        self.genre = None


    def create_from_db_json(self, json):
        self.artist_name = json['artist_name']
        self.start_time = json['concert_start_time']
        self.stage = json['location']
        self.spotify_followers = json['spotify_followers']
        self.spotify_popularity = json['spotify_popularity']
        self.genre = json['itunes_genre']

class User:

    def __init__(self, user_id):
        self.user_id = user_id
        self.concerts = []
        self.rf_days = None # from data_users
        self.datapoint_count = None # from data_users


    def sync_from_db(self, cur):
        cur.execute('select * from data_users where id=%s', (self.user_id,))
        node = dict(cur.fetchone())

        self.rf_days = node['rf_days']
        self.datapoint_count = node['datapoint_count']


    def get_concerts(self, cur):
        cur.execute('select * from user_concerts uc inner join rf_lineup rfl on rfl.artist_id = uc.artist_id where uc.user_id=%s', (self.user_id,))

        for concert in cur.fetchall():
            c = Concert()
            c.create_from_db_json(concert)
            self.concerts.append(c)

class Point:

    def __init__(self, lon=None, lat=None, c_time=None):
        self.lon = lon
        self.lat = lat
        self.c_time = c_time

class FeatureSet:

    def __init__(self):
        pass

    def create_from_json(self, json):
        self.co_occurrences = json['co_occurneces']
        self.co_occurrences_rank = json['co_occurneces_rank']
        self.distinct_co_occurrences = json['distinct_co_occurneces']
        self.same_camp_score = json['same_camp_score']
        self.same_genre_score = json['same_genre_score']
        self.max_time_consecutive_grid = json['max_time_consecutive_grid']
        self.diversity_in_cooccurrences = json['diversity_in_cooccurrences']
        self.location_entropy = json['location_entropy']
        self.mutual_friend_count = json['mutual_friend_count']
        self.same_concerts_jac = json['same_concerts_jac']

class Dyad:

    def __init__(self, source_user, target_user):
        self.source_user = source_user
        self.target_user = target_user
        self.common_points = []
        self.meeting_hours = None
        self.common_concerts = [] # typeof Concert

    def get_features(self, cur):
        cur.execute('select * from derived_friend_features where user_a=%s and user_b=%s', (self.source_user.user_id, self.target_user.user_id,))

        feat_json = dict(cur.fetchone())
        self.features = FeatureSet()
        self.features.create_from_json(feat_json)


    def get_common_concerts(self):

        common_artist_names = {x.artist_name for x in self.source_user.concerts}.intersection({x.artist_name for x in self.target_user.concerts})

        for concert in self.source_user.concerts:
            if concert.artist_name in common_artist_names:
                self.common_concerts.append(concert)

        return self.common_concerts

    def get_common_points(self, cur):
        cur.execute("""select * from friend_list_common_points
                              inner join data_tracker on tracker_id_a = data_tracker.id
                              where user_a=%s and user_b=%s""", (self.source_user.user_id, self.target_user.user_id,))

        self.meeting_hours = defaultdict(lambda: 0)
        for point in cur.fetchall():
            p = Point(lat=point['lat'], lon=point['lon'], c_time=point['c_time'])
            self.common_points.append(p)
            self.meeting_hours[p.c_time.hour] += 1




class Community:

    def __init__(self, dyads):
        self.dyads = dyads

    def create_graph(self):
        self.G = nx.Graph()
        for dyad in self.dyads:
            self.G.add_edge(dyad.user_id, dyad.user_id)
        return self.G


class UserFactory():

    def __init__(self, database):
        self.database = database

    def get_prediction_dyads(self):

        self.database.cur.execute('select user_a as from, user_b as to from prediction_dyads where is_friends=1')

        dyads = []

        for idx, edge in enumerate(self.database.cur.fetchall()):
            print(str('Getting dyad set number {0}'.format(str(idx))))

            source_user = User(edge['from'])
            source_user.sync_from_db(self.database.cur)

            target_user = User(edge['to'])
            target_user.sync_from_db(self.database.cur)

            dyad = Dyad(source_user=source_user, target_user=target_user)
            dyad.get_common_points(self.database.cur)

            dyads.append(dyad)

            if idx > 10:
                break

        return dyads

db = Database()
factory = UserFactory(db)

dyads = factory.get_prediction_dyads()
pickle.dump(dyads, open("dyads.pkl", "wb"))





