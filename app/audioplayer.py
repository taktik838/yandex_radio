from multiprocessing import Process, Value, Pipe
from kivy.clock import Clock
import numpy as np
from tracksprovider import TracksProvider

class Timer:
    def __init__(self, title):
        self.title = title
    def __enter__(self):
        self.start = time()
    def __exit__(self, *args):
        print(f'{self.title} was worked for {time() - self.start:.2f}s')

class AudioPlayer:
    def __init__(self, station, cache_previous=5, cahce_next=2):
        self._station = station
        self._index = cache_previous
        self.cache_previous = cache_previous
        self.cahce_next = cahce_next
        self._in_cache_next = Value('i', 0)
        # self.visible_tracks = self._get_new_tracks(cahce_next + 1) + [None]*cache_previous
        self.visible_tracks = np.array([None for _ in range(cache_previous + 1 + cahce_next)])
        self._tracks_provider = TracksProvider(station, self._in_cache_next, cahce_next)

        # self._generator = self._create_generator()
        self.clock = Clock.schedule_interval(self._get_new_track, .5)


    def next(self):
        now_track, next_track = self.visible_tracks[self._index : self._index + 2]
        self._swap(now_track, next_track)
        if self._index == self.cache_previous: self._shift(1)
        elif self._index < self.cache_previous : self._index += 1
        else: raise Exception(f'index = {self.index}, cache_previous = {self.cache_previous}, cache_next = {self.cache_next}, len = {len(self.visible_tracks)}')

    def previous(self):
        if self._index == 0: return
        next_track, now_track = self.visible_tracks[self._index - 1 : self._index + 1]
        self._swap(now_track, next_track)
        self._index -= 1

    def play(self):
        track = self._get_now_track()
        if track is not None: track.play()

    def stop(self):
        track = self._get_now_track()
        if track is not None: track.stop()

    def seek(self, position):
        track = self._get_now_track()
        if track is not None: track.seek(position)

    def get_state(self):
        track = self._get_now_track()
        if track is not None: track.get_state()

    def like(self):
        track = self._get_now_track()
        if track is not None: track.like()

    def dislike(self):
        track = self._get_now_track()
        if track is not None: track.dislike()

    def _swap(self, now_track, next_track):
        if now_track is None or next_track is None: return
        now_state = self.state()
        now_track.stop()
        if now_state == 'play': next_track.play()
        next_track.seek(0)

    def _get_now_track(self):
        return self.visible_tracks[self._index]

    # def _get_new_tracks(self, n):
    #     start_index = self.visible_tracks.index(None)
    #     for i in range()

    # def _create_generator(self):
    #     def download_content_queue(*args):
    #         self._queue = self._station.client.rotor_station_tracks(*args)

    #     def wait(event):
    #         if self._queue
    #     self._queue = None
    #     Process(target=download_content_queue, args=(self._get_station_id(),))
    #     while True:
    #         wait = Clock.schedule_interval()
    #         for track in self._queue.sequence:
    #             yield track
    #         Process(target=download_content_queue,
    #                         args=(self._get_station_id(), True, self._queue[0].track.id))

    def _shift(self, n):
        assert  n > 0, 'n must be greater than 0, now n <= 0'

        self.visible_tracks[:-n] = self.visible_tracks[n:]
        self.visible_tracks[-n:] = None
        with self._in_cache_next.get_lock(): self._in_cache_next.value -= n

    def _get_station_id(self):
        return self._station.ad_params.other_params

    def _get_new_track(self, timeout=0):
        if self._in_cache_next.value == self.cahce_next: return
        track = self._tracks_provider.get_track(timeout)
        if track is None: return

        index = self.cache_previous + np.where(self.visible_tracks[-self.cahce_next:] == None)[0][0]
        self.visible_tracks[index] = track

    # def go_to(self, track):
    #     current_track = self._get_current_track()
    #     self._index = self.visible_tracks.index(track)