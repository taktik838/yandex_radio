from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.lang.builder import Builder

from kivymd.app import MDApp
from kivymd.uix.button import Button


from pagePlayer import PagePlayer

from yandex_music.client import Client

class MainPage(AnchorLayout):pass

class MyYandexMusicApp(MDApp):
    def __init__(self, **args):
        super().__init__(**args)
        self.client = Client()

    def build(self):
        self.hey = 'hey'
        self.theme_cls.theme_style = "Dark"
        # page = MainPage()
        favorite_stations = self.client.rotor_stations_dashboard().stations
        taktik838 = favorite_stations[0]
        # favorite_stations = favorite_stations['stations']

        page = PagePlayer(taktik838)
        return page


if __name__ == '__main__':
    app = MyYandexMusicApp().run()
