from app.bases import Track, SoundInfo, CoverInfo, ContentMaker
from kivy.core.audio import SoundLoader
from kivy.network.urlrequest import UrlRequest
from mutagen.id3 import ID3, TPE1, TIT2, TEXT, APIC
from multiprocessing import Process
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

        self.cover_info = CoverInfo()
        self.sound_info = SoundInfo()

        self.process_sound = Process(target=self.download_track)
        self.process_cover = Process(target=self.download_cover)

    def process_working(func):
        def main(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if self.need_to_save(): self.save()
            raise Exception('My working is end')
        return main

    @process_working
    def download_track(self):
        if not track_info.track.download_info:
            self.track_info.track.get_download_info(True)

        chunk_size = int(1024 * 1024 * 0.10)
        r = requests.get(self.track_info.track.download_info[0].direct_link, stream=True)
        total_length = int(r.headers.get('content-length'))
        gen = r.iter_content(chunk_size=chunk_size)

        with open(self.path, 'wb') as f: f.write(next(gen))
        self.sound_info.sound = SoundLoader.load(self.path)
        self.sound_info.progress_download_sound = chunk_size / total_length

        with open(file_name, "ab") as f:
            dl = chunk_size
            for data in gen:
                dl += len(data)
                f.write(data)
                self.sound_info.progress_download_sound = dl / total_length
        print('progress downoload SOUND', self.sound_info.progress_download_sound)

    @process_working
    def download_cover(self):
        r = requests.get('http://' + self.track_info.track.cover_uri[:-2] + '300x300', stream=True)
        chunk_size = int(1024 * 1024 * 0.10)
        total_length = int(r.headers.get('content-length'))
        content = b''
        self.cover_info.progress_download_cover = 0
        for data in r.iter_content(chunk_size=chunk_size):
            content += data
            self.cover_info.progress_download_cover = len(content) / total_length
        print('progress downoload COVER', self.cover_info.progress_download_cover)
        self.cover_info.cover = content

    def _need_to_save(self):
        if 1 \
            # and self.track_info.liked \
            and self.cover_info.progress_download_cover == 1 \
            and self.sound_info.progress_download_sound == 1:
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
        self.__del__()