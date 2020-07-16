from multiprocessing import Process, Lock, Pipe, Value
from time import sleep
from kivy.clock import Clock
from onlinecontent import OnlineContent
# import numpy as np

class TracksProvider(Process):
    def __init__(self, station, shared_now_cache: Value, max_cache):
        super().__init__()
        self._station = station
        self._now_cache = shared_now_cache
        self._max_cache = max_cache
        # self._container = container
        receiver, writer = Pipe(False)
        self.receiver = receiver
        self.writer = writer
        self.start()
        # self._lock = Lock()
        # self._process = Process(target=self._main)
        # self._process.start()

        # if first online track doesn't get for 3s, will get track from hard disk
        # event_timeout = Clock.schedule_once(self._check_for_first_track, 3)

    def get_offline(self):pass

    def get_track(self, timeout=0):
        return self.receiver.recv() if self.receiver.poll(timeout) else None

    def run(self):
        queue = self._station.client.rotor_station_tracks(self._station.ad_params.other_params)
        while True:
            for track in queue.sequence:
                while self._now_cache.value >= self._max_cache: sleep(.5)
                track_ = OnlineContent(track)
                with self._now_cache.get_lock():
                    self._now_cache.value += 1
                    self.writer.send(track_)

                # with self._lock:
                #     while not np.any(self._container == None): sleep(.5)
                #     index = np.where(self._container == None)[0][0]
                #     self._container[index] = track

            queue = self._station.client.rotor_station_tracks(
                self._station.ad_params.other_params,
                True, queue[0].track.id
                )

    def _check_for_first_track(self, dt):
        if np.all(self._container == None):
            track = self.get_offline()
            if np.all(self._container == None):
                with self._lock:
                    index = np.where(self._container == None)[0][0]
                    self._container[index] = track


    # def __del__(self):
    #     try: self._process.kill()
    #     except: pass
        # super().__del__(self)
