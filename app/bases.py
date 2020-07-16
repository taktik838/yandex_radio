from multiprocessing.connection import Connection
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from os.path import isfile
# from os import listdir

# class

class Track:
    # def __init__(self, content_maker, path, artists, title, id_, sound_info, cover_info, liked):
        # self.content_maker = content_maker
        # self.path = path
        # self.artists = artists
        # self.title = title
        # self.id = id_
        # self.sound_info = sound_info
        # self.cover_info = cover_info
        # self.liked = liked
        # print(self.content_maker, self.title)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
        # self.clock_check = Clock.schedule_interval(self.check_download, .5)


    def check_download(self):
        # if type(self.sound) is Connection and self.sound.poll(timeout=0): self.sound = self.sound.recv()
        if type(self.sound) is None and isfile(self.path):
            self.sound = SoundLoader(self.path)

        if type(self.cover) is Connection and self.cover.poll(timeout=0): self.cover = self.cover.recv()

        if type(self.cover) is not Connection and type(self.sound) is not Connection: self.clock_check.cancel()

    def play(self):
        if type(self.sound) is not Connection: self.sound_info.sound.play()

    def stop(self):
        if type(self.sound) is not Connection: self.sound_info.sound.stop()

    def get_state(self):
        if type(self.sound) is not Connection: return self.sound_info.sound.state
        else: return 'stop'

    def seek(self, pos):
        if type(self.sound) is not Connection: self.sound_info.sound.seek(pos)

    def get_pos(self):
        if type(self.sound) is not Connection: return self.sound_info.sound.get_pos()
        else: return 0

    @property
    def progress_download_sound(self):
        try: return self._progress_download_track.value
        except AttributeError: return self._progress_download_sound

    # def __del__(self):
    #     self.content_maker.remove()
        # super().__del__(self)

class ContentMaker:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__init__(*args, **kwargs)

        return Track(
            # content_maker = obj,
            path = obj.path,
            artists = obj.artists,
            title = obj.title,
            id_ = obj.id,
            sound = obj.sound,
            cover = obj.cover,
            liked = obj.liked,
            _progress_download_track = obj.progress_download_track
        )
    # def stop(self):
        # self.__del__()

# class SoundInfo:
#     def __init__(self, progress_download_sound=0, sound=None):
#         self.progress_download_sound = progress_download_sound
#         self.sound = sound

# class CoverInfo:
#     def __init__(self, progress_download_cover=0, cover=None):
#         self.progress_download_cover = progress_download_cover
#         self.cover = cover