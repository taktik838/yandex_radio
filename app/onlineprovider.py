from multiprocessing import Process, Queue
from onlinecontent import OnlineContent

class TracksProvider:
    def __init__(self, station, size_cache):
        self._station = station
        self._queue = Queue(size_cache)
        self._process = Process(target=self._main)

    def get_track(self, timeout=0):
        return self._queue.get(timeout=timeout)

    def _main(self):
        queue = self._station.client.rotor_station_tracks(self._station.ad_params.other_params)
        while True:
            for track in queue.sequence:
                while self._queue.full(): pass
                self._queue.put(OnlineContent(track))
            queue = self._station.client.rotor_station_tracks(
                self._station.ad_params.other_params,
                True, queue[0].track.id
                )

    def __del__(self):
        self._process.kill()
        super().__del__(self)
