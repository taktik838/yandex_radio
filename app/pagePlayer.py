# from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Ellipse
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
)
# from kivy.vector import Vector
from kivy.clock import Clock
# from kivy.lang.builder import Builder

from kivy.core.audio import Sound, SoundLoader

# from kivymd.app import MDApp
from kivymd.uix.button import Button
from kivymd.uix.boxlayout import BoxLayout
# from kivy.uix.image import

from getcontentfromcloud import GetContentFromCloud
from audioplayer import AudioPlayer
# from functools import partial
# from threading import Thread
# import requests
from time import time
class Timer:
    def __init__(self, title):
        self.title = title
    def __enter__(self):
        self.start = time()
    def __exit__(self, *args):
        print(f'\033[92m{self.title} was worked for {time() - self.start:.3f}s\033[0m')

class AudioManager:

    def __init__(self, station, visible_next=1, cache_next=1, visible_previous=5, cache_previous=0):
        with Timer('init audio'):
            self._station = station
            # with Timer('get_quque'): self._queue = self._get_new_queue()
            with Timer('create generator'): self._generator = self._generator_new_tracks()
            self._root_path = 'music/'
            self._index = 0
            # self.next_track()
            self._cache_next = cache_next
            self._cache_previous = cache_previous

            # self.visible_next = [None] * (visible_next + 1)
            # self.visible_next[0] = self._get_track()
            with Timer('get tracks'): self.visible_next = self._get_tracks(cache_next + 1)
            self.visible_previous = [None] * visible_previous
            with Timer('cache'): self._to_cache()

    def switch_track(self, n):
        """
        Set as current_track track through n position.
        """
        if abs(self._index + n) >= len(self.visible_previous) or \
            self._index + n >= len(self.visible_next): return

        future_track = self._get_track(self._index + n)

        if future_track is None: return

        current_track = self._get_track()
        current_state = self.get_state()
        self.stop()

        self._index += n

        if 'sound' not in future_track.__dict__: self._get_data_track(future_track)
        self.seek(0)
        if current_state == 'play': self.play()

        if self._index > 0:
            self._clear_cache(
                self.visible_previous[-self._cache_previous : -self._cache_previous + self._index]
                + self.visible_next[self._cache_previous : self._index]
                )
            self.visible_previous = self.visible_previous[self._index:] + self.visible_next[:self._index]
            self.visible_next = self.visible_next[self._index:] + self._get_tracks(self._index)
            self._to_cache()
            self.index = 0


    def play(self):
        self._get_track().sound.play()

    def stop(self):
        self._get_track().sound.stop()

    def get_state(self):
        if 'sound' in self._get_track().__dict__:
            return self._get_track().sound.state
        else:
            return 'stop'

    def seek(self, n):
        self._get_track().sound.seek(n)

    def _get_track(self, index=None):
        if index is None: index = self._index
        if index < 0: return self.visible_previous[self._index]
        else: return self.visible_next[self._index]

    def _clear_cache(self, tracks):
        for track in tracks:
            if track is not None: track.way_getting.remove()

    def _to_cache(self):
        for track in self.visible_next[:self._cache_next+1] + self.visible_previous[-self._cache_previous:]:
            with Timer('get data'): self._get_data_track(track)

    def _get_data_track(self, track):
        if track is None: return
        if 'way_getting' not in track.__dict__:
            with Timer('create GetContentFromCloud'): track.way_getting = GetContentFromCloud(track)
        with Timer('start download track'):track.way_getting.sound(self._root_path + track.track.title.replace('/','|') + '.mp3')
        # track.sound.on_play = self._func_on_play

    def _func_on_play(self):
        # def to_start_in_future(now)
        track = self._get_track()
        if track is None or 'sound' not in track.__dict__: return
        pos_s = track.sound.get_pos()
        duration_ms = int(track.track.duration_ms)
        track.part_play = pos_s / duration_ms * 1000
        # if track.part_play == track.download_part_of_sound:
        #     Clock.schedule_once(partial(self.switch_track, 1), 0.25)
        if track.part_play == 1: self.switch_track(1)

    def _get_only_cover_track(self, track):
        if track is None: return
        if 'way_getting' not in track.__dict__:
            track.way_getting = GetContentFromCloud(track)
        track.way_getting.cover()

    def _get_tracks(self, n):
        return [next(self._generator) for _ in range(n)]

    def _get_new_queue(self):
        if 'queue' not in self.__dict__:
            return self._station.client.rotor_station_tracks(self._get_station_id())
        else:
            return self._station.client.rotor_station_tracks(
                self._get_station_id(), True, self._queue[0].track.id
                )

    def _generator_new_tracks(self):
        while True:
            queue = self._get_new_queue()
            for track in queue.sequence:
                yield track

    def _get_station_id(self):
        return self._station.ad_params.other_params

class PagePlayer(BoxLayout):
    def __init__(self, station, **args):
        self.station = station
        # self.queue = None
        # self.queue = station.client.rotor_station_tracks(self.get_station_id())
        # self.sound = SoundLoader.load('test.mp3')
        # self.player = AudioPlayer(station)
        self.player = AudioManager(station)

        # self._get_gradient_texture()
        super().__init__(**args)
        # self.app.player = 'ter'
        pass

    def _gradient_texture(self):
        bg = self.station.station.icon.background_color
        texture = Texture.create(size=(64, 64), colorfmt='rgba')
        r, g, b = [int(bg[i:i+2], base=16) for i in range(1,7,2)]
        p = []
        with open('app/gausiandistribution', 'rb') as f:
            data = f.read()
            for a in data: p += [r, g, b, a]
        buf = bytes(p)
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture

    def _play_pause(self):
        if self.player.get_state() == 'stop':
            self.player.play()
            self.ids['play_pause'].icon = 'pause'
        else:
            self.player.stop()
            self.ids['play_pause'].icon = 'play'

    def _skip_previos(self):
        # self.player.switch_track(-1)
        self.player.previous()

    def _skip_next(self):
        # self.player.switch_track(1)
        self.player.next()

    def _dislike(self):
        print('dislike')

    def _like(self):
        print('like')