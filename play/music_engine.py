"""Процедурный синтезатор фоновой музыки с переключением тем под каждого босса."""
import pygame
import math
from array import array
from play.sfx import sfx


class MusicEngine:
    """Генерирует зацикленные синтезаторные треки для меню, волн и 3 боссов."""

    def __init__(self):
        self.tracks = {}
        self.current_track = None
        self.channel = None
        self._build_tracks()

    def _synth_loop(self, notes, bpm=125, wave="saw", vol=0.14):
        """Собирает бесшовный музыкальный луп из списка частот (Гц)."""
        if not pygame.mixer.get_init():
            return None
        rate = 22050
        step_sec = (60.0 / bpm) / 2.0
        step_samples = int(rate * step_sec)
        buf = array("h")
        phase = 0.0

        for freq in notes:
            for i in range(step_samples):
                if freq <= 0:
                    buf.append(0)
                    continue
                t = i / step_samples
                env = min(1.0, t * 18.0) * ((1.0 - t) ** 0.75)
                phase += (2.0 * math.pi * freq) / rate
                if wave == "saw":
                    val = 2.0 * ((phase / (2.0 * math.pi)) % 1.0) - 1.0
                elif wave == "square":
                    val = 1.0 if math.sin(phase) >= 0 else -1.0
                else:
                    val = math.sin(phase)
                sample = int(max(-32767, min(32767, val * env * vol * 32767)))
                buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)

    def _build_tracks(self):
        """Создаёт 5 музыкальных тем с разным темпом и формой волны."""
        self.tracks["menu"] = self._synth_loop(
            [110, 130.8, 164.8, 196, 164.8, 130.8, 98, 130.8, 146.8, 174.6, 220, 174.6, 146.8, 130.8, 98, 110],
            bpm=95, wave="sine", vol=0.16
        )
        self.tracks["wave"] = self._synth_loop(
            [110, 110, 130.8, 110, 146.8, 130.8, 98, 110, 110, 110, 164.8, 146.8, 130.8, 110, 98, 82.4],
            bpm=132, wave="saw", vol=0.13
        )
        self.tracks["boss_1"] = self._synth_loop(
            [130.8, 130.8, 196, 130.8, 174.6, 164.8, 130.8, 116.5, 130.8, 130.8, 220, 196, 174.6, 164.8, 146.8, 116.5],
            bpm=148, wave="square", vol=0.12
        )
        self.tracks["boss_2"] = self._synth_loop(
            [146.8, 146.8, 174.6, 146.8, 220, 207.7, 174.6, 130.8, 146.8, 146.8, 261.6, 233.1, 220, 174.6, 164.8, 130.8],
            bpm=156, wave="saw", vol=0.14
        )
        self.tracks["boss_3"] = self._synth_loop(
            [82.4, 82.4, 164.8, 87.3, 82.4, 155.6, 82.4, 98.0, 82.4, 82.4, 196.0, 185.0, 164.8, 146.8, 116.5, 87.3],
            bpm=168, wave="saw", vol=0.15
        )

    def play_track(self, name):
        """Переключает активный трек на выделенном канале и синхронизирует громкость."""
        if not pygame.mixer.get_init():
            return
        if self.channel is None:
            self.channel = pygame.mixer.Channel(7)

        if self.current_track != name:
            self.channel.stop()
            snd = self.tracks.get(name)
            if snd:
                self.channel.play(snd, loops=-1)
            self.current_track = name

        if self.channel:
            self.channel.set_volume(sfx.volume * 0.65)


music = MusicEngine()
