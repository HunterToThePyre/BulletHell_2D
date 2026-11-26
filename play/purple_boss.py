"""Мини-босс 2-й волны: Фиолетовый круг с телепортацией, лазерами и расширяющимися пулями."""
import pygame
import random
import math
from play import constants as c
from play.enemy_projectiles import EnemyBullet, ExpandingRingBullet, EnemyLaser
from play.vfx import make_boss_surface


class PurpleCircleBoss(pygame.sprite.Sprite):
    def __init__(self, diff="normal"):
        super().__init__()
        self.diff = diff
        self.name = "ГИГАНТСКИЙ ФИОЛЕТОВЫЙ КРУГ"
        self.base_image = make_boss_surface(65, c.C_PURPLE, c.C_PINK)

        self.image = self.base_image.copy()
        self.top_pos = pygame.math.Vector2(c.PLAY_RECT.centerx, 140)
        self.center_pos = pygame.math.Vector2(c.PLAY_RECT.centerx, c.H // 2)

        self.rect = self.image.get_rect(center=(c.PLAY_RECT.centerx, -90))
        self.pos = pygame.math.Vector2(self.rect.center)

        mult = {"hard": 2.0, "infernum": 2.0, "masochist": 3.5}.get(diff, 1.0)
        self.hp = int(150 * mult)
        self.max_hp = self.hp
        self.speed = 4.0
        self.bullet_speed = 5.0
        self.damage = 1

        self.hidden = False
        self.phase = 1
        self.timer = 0
        self.sub_step = 0
        self.flip_axis = False

    def _dir_to_player(self, origin=None):
        src = origin if origin is not None else self.pos
        if c.player_group.sprite:
            d = pygame.math.Vector2(c.player_group.sprite.rect.center) - src
            if d.length() > 0:
                return d.normalize()
        return pygame.math.Vector2(0, 1)

    def _spawn_bullet(self, pos, direction, color=c.C_PURPLE):
        c.enemy_bullets.add(EnemyBullet(pos, direction, self.bullet_speed, color, 1.0, self.damage))

    def update(self):
        """Управляет 4 фазами боя: лазеры -> телепорт в центр -> расширяющееся кольцо -> двусторонний обстрел."""
        if self.phase == 1 and self.pos.y < self.top_pos.y and not self.hidden:
            self.pos.y = min(self.top_pos.y, self.pos.y + self.speed)
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            return

        self.timer += 1

        if self.phase == 1:
            if self.sub_step < 6 and self.timer >= 24:
                self.timer = 0
                self.sub_step += 1
                c.enemy_lasers.add(EnemyLaser(self, self._dir_to_player(), self.damage, 24, 30, 16, c.C_PURPLE))
            elif self.sub_step >= 6 and self.timer >= 40:
                self.phase, self.sub_step, self.timer = 2, 0, 0
                self.hidden = True
                self.image = pygame.Surface((1, 1), pygame.SRCALPHA)

        elif self.phase == 2:
            # Телеграф телепортации в центр арены
            pygame.draw.circle(c.screen, (45, 45, 55), (int(self.center_pos.x), int(self.center_pos.y)), 70)
            pygame.draw.circle(c.screen, c.C_PURPLE, (int(self.center_pos.x), int(self.center_pos.y)), 70, 3)
            if self.timer >= 90:
                self.hidden = False
                self.image = self.base_image.copy()
                self.pos = self.center_pos.copy()
                self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
                self.phase, self.sub_step, self.timer = 3, 0, 0

        elif self.phase == 3:
            if self.sub_step == 0:
                for i in range(36):
                    rad = math.radians(i * 10)
                    vec = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                    c.enemy_bullets.add(ExpandingRingBullet(self.rect.center, vec, self.bullet_speed, c.C_PURPLE, self.damage))
                self.sub_step = 1
            elif self.timer >= 90:
                self.phase, self.sub_step, self.timer = 4, 0, 0
                self.flip_axis = False

        elif self.phase == 4:
            self.pos = self.center_pos.copy()
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            if self.timer % 180 == 0:
                self.flip_axis = not self.flip_axis

            if self.timer % 8 == 0:
                d_front = self._dir_to_player()
                if self.flip_axis:
                    d_front = pygame.math.Vector2(-d_front.y, d_front.x)
                self._spawn_bullet(self.pos + d_front * 55, d_front, c.C_PURPLE)
                self._spawn_bullet(self.pos - d_front * 55, -d_front, c.C_PURPLE)

            if self.timer % 13 == 0:
                corners = [
                    pygame.math.Vector2(c.PLAY_RECT.left + 15, 15),
                    pygame.math.Vector2(c.PLAY_RECT.right - 15, 15),
                    pygame.math.Vector2(c.PLAY_RECT.left + 15, c.H - 15),
                    pygame.math.Vector2(c.PLAY_RECT.right - 15, c.H - 15),
                ]
                corner = random.choice(corners)
                self._spawn_bullet(corner, self._dir_to_player(corner), c.C_PINK)

            if self.timer >= 780:
                self.pos = self.top_pos.copy()
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                self.phase, self.sub_step, self.timer = 1, 0, 0
