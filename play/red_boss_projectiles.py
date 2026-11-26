"""Специальные снаряды и лазерные зоны финального Красного босса."""
import pygame
import math
from play import constants as c, game_data as gd
from play.enemy_projectiles import EnemyBullet


def _diff_scale():
    return 1.5 if gd.difficulty in ("infernum", "masochist") else 1.0


class RedBossBullet(EnemyBullet):
    """Снаряд Красного босса с поддержкой синусоиды, деления фейерверком и гравитации."""

    def __init__(self, pos, d, spd, col=c.C_RED, size_mult=1.0, dmg=1, mode="normal", split_y=None):
        super().__init__(pos, d, spd, col, size_mult, dmg)
        self.mode = mode
        self.age = 0
        self.base_pos = pygame.math.Vector2(pos)
        self.perp = pygame.math.Vector2(-self.direction.y, self.direction.x)
        self.split_y = split_y

    def update(self):
        self.age += 1
        if self.mode == "sine":
            self.base_pos += self.direction * self.speed
            self.pos = self.base_pos + self.perp * math.sin(self.age * 0.14) * 45
        elif self.mode == "gravity":
            if self.age <= 300:
                self.pos.y -= self.speed
            elif self.age > 360:
                self.pos.y += self.speed * 1.15
        else:
            self.pos += self.direction * self.speed

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Взрыв фейерверка на заданной высоте с разлётом 6 осколков
        if self.mode == "firework" and self.split_y is not None and self.pos.y >= self.split_y:
            for i in range(6):
                rad = math.radians(i * 60 + 15)
                c.enemy_bullets.add(EnemyBullet(self.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)), 4.2, c.C_ORANGE, 1.0, self.damage))
            self.kill()
            return

        if not c.PLAY_RECT.inflate(140, 140).colliderect(self.rect):
            self.kill()


class HomingMineBullet(EnemyBullet):
    """Самонаводящаяся мина: разлетается, зависает на 1 секунду и делает рывок в игрока."""

    def __init__(self, pos, scatter_dir, dmg=1):
        super().__init__(pos, scatter_dir, 4.5, c.C_RED, 1.6, dmg)
        self.timer = 0
        self.scale = _diff_scale()

    def update(self):
        self.timer += 1
        if self.timer <= 18:
            self.pos += self.direction * self.speed
        elif self.timer == 78:
            if c.player_group.sprite:
                d = pygame.math.Vector2(c.player_group.sprite.rect.center) - self.pos
                self.direction = d.normalize() if d.length() > 0 else pygame.math.Vector2(0, 1)
            self.speed = 9.5 * self.scale
        elif self.timer > 78:
            self.pos += self.direction * self.speed

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if not c.PLAY_RECT.inflate(80, 80).colliderect(self.rect):
            self.kill()


class ContractingRingBullet(EnemyBullet):
    """Сегмент сжимающегося вращающегося кольца с безопасным проходом."""

    def __init__(self, center, radius, angle_deg, shrink_spd=1.5, rot_spd=0.7, dmg=1):
        rad = math.radians(angle_deg)
        cx, cy = center
        pos = (cx + math.cos(rad) * radius, cy + math.sin(rad) * radius)
        super().__init__(pos, pygame.math.Vector2(0, 1), 0, c.C_RED, 1.4, dmg)
        scale = _diff_scale()
        self.center = pygame.math.Vector2(cx, cy)
        self.dist = float(radius)
        self.angle = float(angle_deg)
        self.shrink_spd = shrink_spd * scale
        self.rot_spd = rot_spd * scale

    def update(self):
        self.dist -= self.shrink_spd
        self.angle += self.rot_spd
        if self.dist <= 18:
            self.kill()
            return
        rad = math.radians(self.angle)
        self.pos.x = self.center.x + math.cos(rad) * self.dist
        self.pos.y = self.center.y + math.sin(rad) * self.dist
        self.rect.center = (int(self.pos.x), int(self.pos.y))


class RotatingBeamLaser(pygame.sprite.Sprite):
    """Вращающийся лазерный луч босса с периодической сменой направления вращения."""

    def __init__(self, owner, start_angle, rot_speed, reverse_every=120, life=360, dmg=1):
        super().__init__()
        scale = _diff_scale()
        self.owner = owner
        self.angle = float(start_angle)
        self.rot_speed = rot_speed * scale
        self.reverse_every = reverse_every
        self.life = life
        self.timer = 0
        self.damage = dmg
        self.width = int(14 * scale)
        self.is_firing = False
        self.start_pos = pygame.math.Vector2(owner.rect.center)
        self.end_pos = self.start_pos.copy()
        self.image = pygame.Surface((c.W, c.H), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        self.timer += 1
        if self.timer > self.life or not self.owner.alive():
            self.kill()
            return
        if self.reverse_every > 0 and self.timer > 30 and (self.timer - 30) % self.reverse_every == 0:
            self.rot_speed = -self.rot_speed
        if self.timer > 30:
            self.angle += self.rot_speed

        self.start_pos = pygame.math.Vector2(self.owner.rect.center)
        rad = math.radians(self.angle)
        self.end_pos = self.start_pos + pygame.math.Vector2(math.cos(rad), math.sin(rad)) * 1300

        self.image.fill((0, 0, 0, 0))
        if self.timer <= 30:
            pygame.draw.line(self.image, (255, 100, 100, 160), self.start_pos, self.end_pos, 2)
        else:
            self.is_firing = True
            pygame.draw.line(self.image, c.C_RED, self.start_pos, self.end_pos, self.width)
            pygame.draw.line(self.image, c.C_WHITE, self.start_pos, self.end_pos, max(2, self.width // 3))


class ChessHazardZone(pygame.sprite.Sprite):
    """Прямоугольная опасная зона шахматной матрицы (предупреждение -> активация урона)."""

    def __init__(self, rect, dmg=1):
        super().__init__()
        self.zone_rect = rect
        self.damage = dmg
        self.timer = 0
        self.image = pygame.Surface((c.W, c.H), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        self.timer += 1
        self.image.fill((0, 0, 0, 0))
        if self.timer <= 48:
            pygame.draw.rect(self.image, (255, 60, 60, 70), self.zone_rect)
            pygame.draw.rect(self.image, c.C_RED, self.zone_rect, 2)
        elif self.timer <= 72:
            pygame.draw.rect(self.image, (255, 40, 40, 200), self.zone_rect)
            if c.player_group.sprite and self.zone_rect.colliderect(c.player_group.sprite.rect):
                self.player_hit = True
        else:
            self.kill()
