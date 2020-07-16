from kivy.core.audio import SoundLoader
import os
import requests
from multiprocessing import Process
from threading import Thread
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1, TPE2

from time import time
class Timer:
    def __init__(self, title):
        self.title = title
    def __enter__(self):
        self.start = time()
    def __exit__(self, *args):
        print(f'\033[93m{self.title} was worked for {time() - self.start:.3f}s\033[0m')
        # print(f'{self.title} was worked for {time() - self.start} s')

class GetContentFromCloud:
    def __init__(self, track):
        self.track = track
        # self._stop = False
        self.track.download_part_of_sound = 0
        self.track.cover_content = None
        print(track.track.title)

        if not track.track.download_info:
            with Timer('get_download_info'): track.track.get_download_info(True)

    def cover(self):
        if self.track.cover_content is not None:
            with Timer('create Thread'): self.coverThread = Thread(target=self._download_cover, args=('http://' + self.track.track.cover_uri[:-2] + '300x300',))
            self.coverThread.start()

    def sound(self, file_name):
        self.file_name = file_name
        if self.track.download_part_of_sound != 1:
            chunk_size = int(1024 * 1024 * 0.10)
            r = requests.get(self.track.track.download_info[0].direct_link, stream=True)
            total_length = int(r.headers.get('content-length'))
            gen = r.iter_content(chunk_size=chunk_size)
            with open(file_name, 'wb') as f: f.write(next(gen))
            self.track.sound = SoundLoader.load(file_name)

            with Timer('create Thread'): self.soundThread = Thread(target=self._download_sound, args=(gen, file_name, total_length, chunk_size))
            self.soundThread.start()

    def _download_cover(self, url):
        # print('working download cover1')
        r = requests.get(url)
        self.track.cover_content = r.content

        # if self._need_to_save(): self._save()

    def _download_sound(self, gen, file_name, total_length, chunk_size):
        # print('working download sound1')
        with open(file_name, "ab") as f:
            dl = chunk_size
            for data in gen:
                # if self._stop: return
                dl += len(data)
                f.write(data)
                self.track.download_part_of_sound = dl / total_length
        # print('download done')
        # if self._need_to_save(): self._save()
        # self.track.sound = SoundLoader.load(file_name)

    def _save(self):
        print('working save')
        audio = MP3(self.file_name, ID3=ID3)
        # filename_cover = 'cover.png'
        # add ID3 tag if it doesn't exist
        try:
            audio.add_tags()
        except error:
            pass

        audio.tags.add(
            APIC(
                encoding=3, # 3 is for utf-8
                mime='image/png', # image/jpeg or image/png
                type=3, # 3 is for the cover image
                desc=u'Cover',
                data=self.track.cover_content
            )
        )
        audio.tags.add(TIT2(text=self.track.track.title))
        audio.tags.add(TPE1(text=', '.join([artist.name for artist in self.track.track.artists])))
        audio.tags.add(TPE2(text=self.track.id))
        audio.save()

    def _need_to_save(self):
        if self.track.liked \
            and self.track.cover_content is not None \
            and self.track.download_part_of_sound == 1:
                return True
        else: return False

    def remove(self):
        """
        Stops download sound if it workig now. If need, it remove file, it nullifies property "download_part_of_sound"
        """
        # print('stop for', self.track.track.title)
        # self._stop = True
        try: self.soundThread.terminate()
        except:pass
        try: self.coverThread.terminate()
        except:pass
        if not self._need_to_save:
            os.remove(self.file_name)
            self.track.download_part_of_sound = 0

    def __del__(self):
        self.remove()

    # def remove(self):
    #     # print('working stop')
    #     self.track.sound.unload()
    #     self._state = 'del'
    #     del self.track.sound
    #     # del self.track.cover_content
    #     del self.track.file_name
    #     del self.track.download_part_of_sound
    #     del self.track.way_getting
    #     if not self._need_to_save(): os.remove(self.track.file_name)

    # def __del__(self):
    #     # print('working del')
    #     self.remove()