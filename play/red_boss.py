"""Финальный босс 3-й волны: Красный круг, делегирующий 9 фаз атак модулю red_boss_attacks."""
import pygame
from play import constants as c
from play.red_boss_attacks import run_phase_1_to_5, run_phase_6_to_9
from play.vfx import make_boss_surface


class RedCircleBoss(pygame.sprite.Sprite):
    def __init__(self, diff="normal"):
        super().__init__()
        self.diff = diff
        self.name = "ГИГАНТСКИЙ КРАСНЫЙ КРУГ"
        self.base_image = make_boss_surface(75, c.C_RED, c.C_ORANGE)

        self.image = self.base_image.copy()
        self.top_pos = pygame.math.Vector2(c.PLAY_RECT.centerx, 140)
        self.center_pos = pygame.math.Vector2(c.PLAY_RECT.centerx, c.H // 2)
        self.rect = self.image.get_rect(center=(c.PLAY_RECT.centerx, -100))
        self.pos = pygame.math.Vector2(self.rect.center)

        mult = {"hard": 2.0, "infernum": 2.0, "masochist": 3.5}.get(diff, 1.0)
        self.hp = int(250 * mult)
        self.max_hp = self.hp
        self.damage = 1

        self.hidden = False
        self.invulnerable = False
        self.trap_rect = None
        self.gravity_pull = False

        self.phase = 1
        self.timer = 0
        self.sub_step = 0
        self.ring_bullets = []
        self.orbit_angle = 0.0

    def dir_to_player(self, origin=None):
        src = origin if origin is not None else self.pos
        if c.player_group.sprite:
            d = pygame.math.Vector2(c.player_group.sprite.rect.center) - src
            if d.length() > 0:
                return d.normalize()
        return pygame.math.Vector2(0, 1)

    def move_towards(self, target, speed=6.0):
        diff = target - self.pos
        if diff.length() <= speed:
            self.pos = target.copy()
            return True
        self.pos += diff.normalize() * speed
        return False

    def next_phase(self, next_p):
        """Сбрасывает временные ограничения арены и переводит босса в следующую фазу."""
        self.phase = next_p
        self.timer = 0
        self.sub_step = 0
        self.hidden = False
        self.invulnerable = False
        self.trap_rect = None
        self.gravity_pull = False
        self.image = self.base_image.copy()

    def update(self):
        self.timer += 1
        if self.phase <= 5:
            run_phase_1_to_5(self)
        else:
            run_phase_6_to_9(self)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
