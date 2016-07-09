import psycopg2
import requests
import time

conn_dtu = psycopg2.connect(database="", user="", password="", host="")
cur_dtu = conn_dtu.cursor()

cur_dtu.execute("select artist_name from rf_lineup where itunes_id is null")
search_url = 'https://itunes.apple.com/search'
params = {'term' :None, 'kind': 'artist'}

for each in cur_dtu.fetchall():

    params['term'] = each[0].lower()
    r = requests.get(search_url, params=params)
    artists = r.json()['results']

    for each_artist in artists:
        if each_artist['artistName'].lower().strip() == each[0].lower().strip():
            id = each_artist.get('artistId')

            if id is None:
                print('no id on: {0}'.format(each[0]))
                continue
            r_artist = requests.get('https://itunes.apple.com/lookup', params={'id': id})
            artist_data = r.json()['results']
            genre = each_artist['primaryGenreName']
            cur_dtu.execute("""update rf_lineup set
            itunes_id=%s,
            itunes_genre=%s
            WHERE artist_name=%s""",
                            (id,
                             genre,
                             each[0],))
            break

    conn_dtu.commit()
    time.sleep(0.2)


