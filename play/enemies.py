"""Конфигурация 12 типов обычных врагов, их траектории движения и паттерны стрельбы."""
import pygame
import random
import math
from play import constants as c
from play.enemy_projectiles import EnemyBullet, BulletTether, EnemyLaser
from play.vfx import make_neon_shape

ENEMY_CONFIGS = {
    "yellow_tri": {"shape": "tri", "color": c.C_YELLOW, "hp": 2, "dmg": 1, "speed": 2.0, "b_spd": 4.0, "cd": 30},
    "orange_tri": {"shape": "tri", "color": c.C_ORANGE, "hp": 3, "dmg": 1, "speed": 3.0, "b_spd": 4.0, "cd": 30},
    "green_tri":  {"shape": "tri", "color": c.C_GREEN,  "hp": 3, "dmg": 1, "speed": 4.0, "b_spd": 4.0, "cd": 60},
    "cyan_tri":   {"shape": "tri", "color": c.C_CYAN,   "hp": 4, "dmg": 1, "speed": 2.0, "b_spd": 4.0, "cd": 48},
    "yellow_sq":  {"shape": "sq",  "color": c.C_YELLOW, "hp": 5, "dmg": 1, "speed": 1.0, "b_spd": 4.0, "cd": 42},
    "orange_sq":  {"shape": "sq",  "color": c.C_ORANGE, "hp": 5, "dmg": 1, "speed": 3.0, "b_spd": 4.0, "cd": 90},
    "green_sq":   {"shape": "sq",  "color": c.C_GREEN,  "hp": 6, "dmg": 1, "speed": 4.0, "b_spd": 4.0, "cd": 60},
    "cyan_sq":    {"shape": "sq",  "color": c.C_CYAN,   "hp": 6, "dmg": 1, "speed": 4.0, "b_spd": 4.0, "cd": 180},
    "yellow_hex": {"shape": "hex", "color": c.C_YELLOW, "hp": 5, "dmg": 2, "speed": 3.0, "b_spd": 3.0, "cd": 48},
    "orange_hex": {"shape": "hex", "color": c.C_ORANGE, "hp": 4, "dmg": 1, "speed": 5.0, "b_spd": 5.0, "cd": 30},
    "green_hex":  {"shape": "hex", "color": c.C_GREEN,  "hp": 7, "dmg": 1, "speed": 3.0, "b_spd": 4.0, "cd": 210},
    "cyan_hex":   {"shape": "hex", "color": c.C_CYAN,   "hp": 6, "dmg": 1, "speed": 4.0, "b_spd": 3.0, "cd": 60},
}


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_kind, diff="normal"):
        super().__init__()
        self.kind, self.diff = enemy_kind, diff
        cfg = ENEMY_CONFIGS[enemy_kind]

        self.color, self.shape = cfg["color"], cfg["shape"]
        self.speed, self.bullet_speed = cfg["speed"], cfg["b_spd"]
        self.shoot_cd, self.damage = cfg["cd"], cfg["dmg"]
        self.hp = int(math.ceil(cfg["hp"] * (2.5 if diff == "masochist" else 1.0)))

        size = 46 if self.shape == "hex" else 42
        self.image = make_neon_shape(self.shape, self.color, size)
        self.move_pattern = random.choice(["straight", "snake", "left_to_right", "right_to_left", "zigzag"])
        self.age, self.vx, self.vy = 0, 0.0, self.speed

        if self.move_pattern == "left_to_right":
            start_x, start_y = c.PLAY_RECT.left - 20, random.randint(80, c.H // 2)
            self.vx, self.vy = self.speed, self.speed * 0.25
        elif self.move_pattern == "right_to_left":
            start_x, start_y = c.PLAY_RECT.right + 20, random.randint(80, c.H // 2)
            self.vx, self.vy = -self.speed, self.speed * 0.25
        else:
            start_x = random.randint(c.PLAY_RECT.left + 45, c.PLAY_RECT.right - 45)
            start_y = random.randint(-70, -30)
            if self.move_pattern == "zigzag":
                self.vx = random.choice([-1, 1]) * (self.speed * 0.85)

        self.base_x = float(start_x)
        self.pos = pygame.math.Vector2(start_x, start_y)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.timer = random.randint(0, max(1, self.shoot_cd // 2))
        self.burst_left, self.burst_delay = 0, 0

    def _dir_to_player(self, lead_offset=0):
        if c.player_group.sprite:
            tx, ty = c.player_group.sprite.rect.center
            d = pygame.math.Vector2(tx, ty - lead_offset) - self.pos
            if d.length() > 0:
                return d.normalize()
        return pygame.math.Vector2(0, 1)

    def _spawn_bullet(self, pos, direction, extra_scale=1.0):
        b = EnemyBullet(pos, direction, self.bullet_speed, self.color, extra_scale, self.damage)
        c.enemy_bullets.add(b)
        return b

    def _fire_shotgun(self, base_dir, count, spread_deg):
        if self.diff in ("hard", "infernum", "masochist"):
            count += 3
            spread_deg += 14
        base_angle = math.degrees(math.atan2(base_dir.y, base_dir.x))
        step = spread_deg / max(1, count - 1)
        start_a = base_angle - spread_deg / 2
        for i in range(count):
            rad = math.radians(start_a + i * step)
            self._spawn_bullet(self.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)))

    def update(self):
        self.age += 1
        if self.move_pattern == "snake":
            self.pos.y += self.speed
            self.pos.x = max(c.PLAY_RECT.left + 20, min(c.PLAY_RECT.right - 20, self.base_x + math.sin(self.age * 0.06) * 75))
        elif self.move_pattern == "zigzag":
            self.pos.x += self.vx
            self.pos.y += self.vy
            if self.pos.x <= c.PLAY_RECT.left + 20 or self.pos.x >= c.PLAY_RECT.right - 20:
                self.vx = -self.vx
        else:
            self.pos.x += self.vx
            self.pos.y += self.vy

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if (self.rect.top > c.H + 40 or
                (self.move_pattern == "left_to_right" and self.rect.left > c.PLAY_RECT.right + 40) or
                (self.move_pattern == "right_to_left" and self.rect.right < c.PLAY_RECT.left - 40)):
            self.kill()
            return

        if self.burst_left > 0:
            self.burst_delay -= 1
            if self.burst_delay <= 0:
                self.burst_left -= 1
                self.burst_delay = 6
                if self.kind == "orange_sq":
                    self._fire_shotgun(self._dir_to_player(), 6, 36)
                else:
                    self._spawn_bullet(self.rect.center, self._dir_to_player())

        self.timer += 1
        if self.timer >= self.shoot_cd:
            self.timer = 0
            self._perform_attack()

    def _perform_attack(self):
        """Выполняет уникальную атаку, привязанную к виду врага."""
        hard_plus = self.diff in ("hard", "infernum", "masochist")
        if self.kind == "yellow_tri":
            self._fire_shotgun(self._dir_to_player(), 2, 14) if hard_plus else self._spawn_bullet(self.rect.center, self._dir_to_player())
        elif self.kind == "orange_tri":
            for ox in ([-14, 0, 14] if hard_plus else [-8, 8]):
                self._spawn_bullet((self.rect.centerx + ox, self.rect.centery), pygame.math.Vector2(0, 1))
        elif self.kind == "green_tri":
            self._fire_shotgun(pygame.math.Vector2(0, 1), 6, 40)
        elif self.kind in ["cyan_tri", "orange_sq", "green_sq"]:
            self.burst_left = {"cyan_tri": 3, "orange_sq": 2, "green_sq": 5}[self.kind] + (2 if hard_plus else 0)
            self.burst_delay = 0
        elif self.kind == "yellow_sq":
            d = self._dir_to_player()
            perp = pygame.math.Vector2(-d.y, d.x) * 12
            for s in ([-2, -1, 0, 1, 2] if hard_plus else [-1, 0, 1]):
                self._spawn_bullet(self.pos + perp * s, d)
        elif self.kind == "cyan_sq":
            c.enemy_lasers.add(EnemyLaser(self, self._dir_to_player(), self.damage, 30, 30, 16, c.C_CYAN))
        elif self.kind == "yellow_hex":
            if hard_plus:
                base_a = math.degrees(math.atan2(self._dir_to_player().y, self._dir_to_player().x))
                for off in [-12, 12]:
                    vec = pygame.math.Vector2(math.cos(math.radians(base_a + off)), math.sin(math.radians(base_a + off)))
                    self._spawn_bullet(self.rect.center, vec, extra_scale=2.4)
            else:
                self._spawn_bullet(self.rect.center, self._dir_to_player(), extra_scale=2.4)
        elif self.kind == "orange_hex":
            self._fire_shotgun(self._dir_to_player(lead_offset=90), 3, 22)
        elif self.kind == "green_hex":
            base_ang = math.degrees(math.atan2(self._dir_to_player().y, self._dir_to_player().x))
            for ang in ([-21, -7, 7, 21] if hard_plus else [-14, 0, 14]):
                vec = pygame.math.Vector2(math.cos(math.radians(base_ang + ang)), math.sin(math.radians(base_ang + ang)))
                c.enemy_lasers.add(EnemyLaser(self, vec, self.damage, 30, 18, 6, c.C_GREEN))
        elif self.kind == "cyan_hex":
            base_ang = math.degrees(math.atan2(self._dir_to_player().y, self._dir_to_player().x))
            b1 = self._spawn_bullet(self.rect.center, pygame.math.Vector2(math.cos(math.radians(base_ang - 16)), math.sin(math.radians(base_ang - 16))))
            b2 = self._spawn_bullet(self.rect.center, pygame.math.Vector2(math.cos(math.radians(base_ang + 16)), math.sin(math.radians(base_ang + 16))))
            c.enemy_lasers.add(BulletTether(b1, b2, self.damage))
