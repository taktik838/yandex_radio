from bases import Track, ContentMaker#, SoundInfo, CoverInfo,
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from mutagen.id3 import ID3, TPE1, TIT2, TEXT, APIC
from mutagen.mp3 import MP3
from multiprocessing import Process, Value, Pipe
import os
import requests

class OnlineContent(ContentMaker):
    # def __new__(cls, *args, **kwargs):
    #     obj = super().__new__(cls)
    #     obj.__init__(*args, **kwargs)

    #     return Track(
    #         content_maker = obj,
    #         path = obj.path,
    #         artists = obj.artists,
    #         title = obj.title,
    #         url_to_ym = obj.url_to_ym,
    #         sound_info = obj.sound_info,
    #         cover_info = obj.cover_info,
    #     )

    def __init__(self, track_info, root_path='music'):
        self.track_info = track_info
        file_name = track_info.track.title.replace('/', '|').replace(' ', '_') + '.mp3'

        self.path = os.path.join(root_path, file_name)
        self.artists = ', '.join([artist.name for artist in track_info.track.artists])
        self.title = track_info.track.title
        self.url_to_ym = 'https://music.yandex.ru/track/' + str(track_info.track.id)
        self.id = str(track_info.track.id)
        self.liked = track_info.liked

        # self.cover_info = CoverInfo()
        # self.sound_info = SoundInfo()

        cover_con_recv, cover_con_writer = Pipe(False)
        self.cover = cover_con_recv
        self.progress_download_cover = Value('f', 0)

        # track_con_recv, track_con_writer = Pipe(False)
        # self.sound = track_con_recv
        progress_con_recv, progress_con_writer = Pipe(False)
        self.sound = None
        self.progress_download_track = Value('f', 0)

        self.process_sound = Process(target=self.download_track, args=())
        self.process_cover = Process(target=self.download_cover, args=(cover_con_writer,))

        self.process_cover.start()
        self.process_sound.start()

    def process_working(func):
        def main(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if self._need_to_save(): self.save()
            # raise Exception('My working is end')
        return main

    @process_working
    def download_track(self):
        if not self.track_info.track.download_info:
            self.track_info.track.get_download_info(True)

        chunk_size = int(1024 * 1024 * 0.10)
        r = requests.get(self.track_info.track.download_info[0].direct_link, stream=True)
        total_length = int(r.headers.get('content-length'))
        gen = r.iter_content(chunk_size=chunk_size)

        with open(self.path, 'wb') as f: f.write(next(gen))
        # con.send(SoundLoader.load(self.path))
        # self.sound_info.sound = SoundLoader.load(self.path)
        self.progress_download_track.value = chunk_size / total_length

        with open(self.path, "ab") as f:
            dl = chunk_size
            for data in gen:
                dl += len(data)
                f.write(data)
                with self.progress_download_track.get_lock():
                    self.progress_download_track.value = dl / total_length
        print('progress downoload SOUND', self.progress_download_track.value)

    @process_working
    def download_cover(self, con):
        r = requests.get('http://' + self.track_info.track.cover_uri[:-2] + '300x300', stream=True)
        chunk_size = int(1024 * 1024 * 0.10)
        total_length = int(r.headers.get('content-length'))
        content = b''
        self.progress_download_cover.value = 0
        for data in r.iter_content(chunk_size=chunk_size):
            content += data
            self.progress_download_cover.value = len(content) / total_length
        print('progress downoload COVER', self.progress_download_cover.value)
        con.send(content)

    def _need_to_save(self):
        if (1
            # and self.track_info.liked
            and self.progress_download_cover.value == 1
            and self.progress_download_track.value == 1
            ):
                return True
        else: return False

    def save(self):
        print('save', self.path)
        audio = MP3(self.file_name, ID3=ID3)
        try:audio.add_tags()
        except:pass
        audio.tags.add(TPE1(encoding=3, text=self.artists)) # artist
        audio.tags.add(TIT2(encoding=3, text=self.title))  # title
        audio.tags.add(TEXT(encoding=3, text=self.url_to_ym)) # lyrics
        audio.tags.add(APIC(
                          encoding=3,
                          mime='image/jpeg',
                          type=3, desc=u'Cover',
                          data=self.cover_content
                        )) # cover
        audio.save()

    def remove(self):
        """
        Stops download sound if it workig now. If need, it remove file
        """
        print('stop')
        # self._stop = True
        try: self.process_sound.kill()
        except:pass
        try: self.process_cover.kill()
        except:pass
        if not self._need_to_save:
            os.remove(self.path)
        # self.__del__()