"""Модуль первого босса (Синий круг) и базового финального босса."""
import pygame
import math
from play import constants as c
from play.enemy_projectiles import EnemyBullet
from play.vfx import make_boss_surface


class BlueCircleBoss(pygame.sprite.Sprite):
    """Мини-босс после 1-й волны: Гигантский синий круг с 3 фазами атак."""

    def __init__(self, diff="normal"):
        super().__init__()
        self.diff = diff
        self.name = "ГИГАНТСКИЙ СИНИЙ КРУГ"
        self.image = make_boss_surface(65, c.C_BLUE, c.C_CYAN)

        self.rect = self.image.get_rect(center=(c.PLAY_RECT.centerx, -90))
        self.pos = pygame.math.Vector2(self.rect.center)

        # Масштабирование HP в зависимости от выбранной сложности
        mult = {"hard": 2.0, "infernum": 2.0, "masochist": 3.5}.get(diff, 1.0)
        self.hp = int(100 * mult)
        self.max_hp = self.hp
        self.speed = 4.0
        self.bullet_speed = 4.0
        self.damage = 1
        self.move_dir = 1

        self.phase = 1
        self.timer = 0
        self.sub_step = 0

    def _dir_to_player(self):
        """Возвращает нормализованный вектор направления к игроку."""
        if c.player_group.sprite:
            d = pygame.math.Vector2(c.player_group.sprite.rect.center) - self.pos
            if d.length() > 0:
                return d.normalize()
        return pygame.math.Vector2(0, 1)

    def _spawn_bullet(self, pos, direction, extra_scale=1.0, color=c.C_BLUE):
        """Создаёт снаряд босса и добавляет его в группу вражеских пуль."""
        c.enemy_bullets.add(EnemyBullet(pos, direction, self.bullet_speed, color, extra_scale, self.damage))

    def update(self):
        """Обновляет выход босса на арену, патрулирование по горизонтали и цикл фаз."""
        if self.rect.centery < 140:
            self.pos.y += self.speed
        else:
            self.pos.x += self.speed * self.move_dir
            if self.pos.x >= c.PLAY_RECT.right - 85:
                self.pos.x = c.PLAY_RECT.right - 85
                self.move_dir = -1
            elif self.pos.x <= c.PLAY_RECT.left + 85:
                self.pos.x = c.PLAY_RECT.left + 85
                self.move_dir = 1

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.timer += 1

        # Фаза 1: шеренга из 5 снарядов в сторону игрока (3 залпа)
        if self.phase == 1:
            if self.timer >= 30:
                self.timer = 0
                d = self._dir_to_player()
                perp = pygame.math.Vector2(-d.y, d.x) * 16
                for idx in range(-2, 3):
                    self._spawn_bullet(self.pos + perp * idx, d, 1.0, c.C_CYAN)
                self.sub_step += 1
                if self.sub_step >= 3:
                    self.phase, self.sub_step, self.timer = 2, 0, 0

        # Фаза 2: два круговых кольца по 24 пули со смещением угла
        elif self.phase == 2:
            if self.sub_step == 0 and self.timer >= 30:
                for i in range(24):
                    rad = math.radians(i * 15 - 12)
                    self._spawn_bullet(self.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)), 1.0, c.C_BLUE)
                self.sub_step, self.timer = 1, 0
            elif self.sub_step == 1 and self.timer >= 120:
                for i in range(24):
                    rad = math.radians(i * 15 + 12)
                    self._spawn_bullet(self.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)), 1.0, c.C_CYAN)
                self.phase, self.sub_step, self.timer = 3, 0, 0

        # Фаза 3: прицельная очередь крупными сферами
        elif self.phase == 3:
            if self.timer % 18 == 0:
                self._spawn_bullet(self.rect.center, self._dir_to_player(), extra_scale=2.5, color=c.C_BLUE)
            if self.timer >= 300:
                self.phase, self.sub_step, self.timer = 1, 0, 0


class Boss(pygame.sprite.Sprite):
    """Базовый класс финального босса со спиральной круговой атакой."""

    def __init__(self, diff="normal"):
        super().__init__()
        self.diff = diff
        self.name = "ФИНАЛЬНЫЙ БОСС"
        self.image = make_boss_surface(40, c.C_RED, c.C_ORANGE)
        self.rect = self.image.get_rect(center=(c.PLAY_RECT.centerx, -100))
        self.pos = pygame.math.Vector2(self.rect.center)
        mult = {"hard": 2.0, "infernum": 2.0, "masochist": 3.5}.get(diff, 1.0)
        self.hp = int(150 * mult)
        self.max_hp = self.hp
        self.cooldown = 0
        self.angle = 0

    def update(self):
        if self.rect.centery < 150:
            self.pos.y += 1
        else:
            self.pos.x += math.sin(pygame.time.get_ticks() * 0.001) * 1.5
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.cooldown += 1
        width_delay = 6 if (self.diff in ["infernum", "masochist"]) else 12
        if self.cooldown >= width_delay:
            self.cooldown, self.angle = 0, self.angle + 8
            for i in range(12):
                rad = math.radians(self.angle + (i * 30))
                vec = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                c.enemy_bullets.add(EnemyBullet(self.rect.center, vec, 2.5, c.C_RED, 1.0))
