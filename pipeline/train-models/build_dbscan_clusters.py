from __future__ import division
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
import psycopg2
import sys

from collections import defaultdict

EARTH_CIRCUMFERENCE = 6378137     # earth circumference in meters
conn = psycopg2.connect(database="", user="", password="", host="")
cur = conn.cursor()

# Distance formula has been obtained from this thread:
# http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
from math import radians, cos, sin, asin, sqrt
def haversine(lat_lon1, lat_lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """

    # Return huge error if the tuple contains more than 2 values
    # This is necessary due to an error in the output
    try:
        # convert decimal degrees to radians
        lat1, lon1 = tuple(lat_lon1)
        lat2, lon2 = tuple(lat_lon2)
    except ValueError as e:
        #print('failed...')
        return 999 # return a huge distance, so it's not considered as a part of the cluster

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # This thread
    #http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
    R = 6371  #radius of the earth in km
    x = (lon2 - lon1) * cos( 0.5*(lat2+lat1) )
    y = lat2 - lat1
    d = R * sqrt( x*x + y*y )
    return d


def get_cluster_stats(observation_hours_list):

    prev = 0
    prel_counters = dict(night=0,day=0,evening=0)

    counters = dict(night=0,day=0,evening=0)
    for obs in observation_hours_list:

        if prev +1 == obs or prev+2 ==obs:
            if 1 <= obs <= 9:
                prel_counters['night'] += 1

            elif 9 <= obs <= 17:
                prel_counters['day'] += 1
            elif 17 < obs <= 23:
                prel_counters['evening'] += 1

            prev = obs
        elif prev == obs:
            pass
        else:
            prel_counters = dict(night=0,day=0,evening=0)

        empty_counts = False
        for k, v in prel_counters.items():
            if v >= 5:
                counters[k] +=1
                empty_counts=True

        if empty_counts:
            prel_counters = dict(night=0,day=0,evening=0)

    return dict(day_counts=counters['day'],
                evening_counts=counters['evening'],
                night_counts=counters['night'],
                )



if len(sys.argv) == 3:
    start_id = sys.argv[1]
    end_id = sys.argv[2]
else:
    raise ValueError()
    start_id = 0
    end_id = 999999999

cur.execute("SELECT us.id FROM data_users as us where not exists(select 1 from derived_clusters WHERE user_id=us.id) and us.id between %s and %s",
            (start_id, end_id))
user_ids = cur.fetchall()

zero_points_users = []
for x, user_id in enumerate(user_ids):
    print(str(user_id))

    cur.execute("SELECT lat, lon, date_part('hour', c_time) FROM data_tracker WHERE user_id=%s and rf_place_id between 38 and 59 or rf_place_id=1", (user_id,))

    X = []
    timestamps = []
    for row in cur.fetchall():
        X.append(row[:2])
        timestamps.append(row[2])

    X = np.array(X)

    db = DBSCAN(eps=0.03, min_samples=30, metric=haversine).fit(X)

    labels = db.labels_
    res_dict = defaultdict(lambda: [])
    timestamp_dict = defaultdict(lambda: [])
    noise_count = 0

    for (label, coordinates, timestamp) in zip(labels, X, timestamps):
        if label == -1:
            noise_count += 1
            continue
        res_dict[str(label)].append(tuple(coordinates))
        timestamp_dict[str(label)].append(timestamp)

    for i, (k, v) in enumerate(res_dict.items()):
        avg = np.mean(v, axis=0)
        observation_count = len(v)

        observation_stats = get_cluster_stats(observation_hours_list=timestamp_dict[k])
        cur.execute("""INSERT into derived_clusters
                            (user_id, lat, lon, clustered_points, observation_hours, noise_count, day_counts, evening_counts, night_counts)
                             VALUES (%s,%s,%s,%s,%s,%s) """,
                        (user_id,
                         avg[0],
                         avg[1],
                         observation_count,
                         timestamp_dict[k],
                         noise_count,
                         observation_stats['day_counts'],
                         observation_stats['evening_counts'],
                         observation_stats['night_counts'],))


    if x % 100 == 0:
        print('Reached {0} users. Saving...'.format(str(x)))
        print('users with <200 points: ' + str(zero_points_users))
        conn.commit()
conn.commit()
conn.close()