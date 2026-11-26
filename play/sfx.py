"""Процедурный синтезатор звуковых эффектов без внешних аудиофайлов."""
import pygame
import math
import random
from array import array

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
except Exception:
    pass


class SoundEngine:
    """Генерирует и воспроизводит звуки попаданий, взрывов, грейза и бонусов."""

    def __init__(self):
        self.volume = 0.5
        self.sounds = {}
        self._build_all()

    def _make_wave(self, freq_start, freq_end, duration, wave="square", vol=0.35):
        """Создаёт Sound-буфер с плавным изменением частоты и затуханием громкости."""
        if not pygame.mixer.get_init():
            return None
        rate = 22050
        n = int(rate * duration)
        buf = array("h")
        phase = 0.0
        for i in range(n):
            t = i / max(1, n)
            freq = freq_start + (freq_end - freq_start) * t
            env = (1.0 - t) ** 1.4
            phase += (2.0 * math.pi * freq) / rate
            if wave == "noise":
                val = random.uniform(-1.0, 1.0)
            elif wave == "sine":
                val = math.sin(phase)
            else:
                val = 1.0 if math.sin(phase) >= 0 else -1.0
            sample = int(max(-32767, min(32767, val * env * vol * 32767)))
            buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)

    def _build_all(self):
        """Предварительно синтезирует все игровые звуки при запуске."""
        self.sounds["hit"] = self._make_wave(520, 260, 0.06, "square", 0.22)
        self.sounds["kill"] = self._make_wave(240, 55, 0.22, "noise", 0.45)
        self.sounds["boss_kill"] = self._make_wave(180, 28, 0.65, "noise", 0.65)
        self.sounds["player_hit"] = self._make_wave(190, 65, 0.30, "square", 0.55)
        self.sounds["graze"] = self._make_wave(950, 1350, 0.05, "sine", 0.22)
        self.sounds["pickup"] = self._make_wave(440, 880, 0.14, "sine", 0.35)

    def set_volume(self, new_vol):
        self.volume = max(0.0, min(1.0, round(new_vol, 2)))

    def change_volume(self, delta):
        self.set_volume(self.volume + delta)
        self.play("pickup")

    def play(self, name):
        """Проигрывает звук по его ключу с учётом текущей общей громкости."""
        snd = self.sounds.get(name)
        if snd and self.volume > 0:
            snd.set_volume(self.volume)
            snd.play()


sfx = SoundEngine()
