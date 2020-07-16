# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from yandex_music.client import Client
import yandex_music as ym


# %%
# client = Client.from_credentials('taktik838@yandex.ru', '34erdfcv')


# %%
import pickle
# with open('auth.pickle', 'wb') as f:
#     pickle.dump(client, f)
with open('auth.pickle', 'rb') as f:
    client = pickle.load(f)


# %%
stations = client.rotorStationsList()


# %%
for st in stations:
    print(st['station']['name'])


# %%
st['station']


# %%
favorite_stations = client.rotor_stations_dashboard()
favorite_stations = favorite_stations['stations']


# %%
favorite_stations[0]


# %%
eval(str(favorite_stations[0]))


# %%
tracks = client.rotor_station_tracks('user:259649747')


# %%
tmp = tracks.sequence[0].track.get_download_info(True)
eval(str(tmp))


# %%
import requests

link = tmp[0].direct_link

file_name = 'req.mp3'

with open(file_name, "wb") as f:
        print ("Downloading %s" % file_name)
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            print(1)
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                # sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                # sys.stdout.flush()
                print(len(response.content))

