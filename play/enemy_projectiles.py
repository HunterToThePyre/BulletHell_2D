"""Снаряды, связки и лазерные лучи врагов с масштабированием под уровень сложности."""
import pygame
from play import constants as c, game_data as gd
from play.vfx import make_glow_circle


def _diff_scale():
    """Возвращает множитель скорости и размера атак (x1.5 на Инфернуме и Мазохисте)."""
    return 1.5 if gd.difficulty in ("infernum", "masochist") else 1.0


class EnemyBullet(pygame.sprite.Sprite):
    """Базовый светящийся снаряд врага, летящий по заданному вектору."""

    def __init__(self, pos, d, spd, col, size_mult=1.0, dmg=1):
        super().__init__()
        scale = _diff_scale()
        rad = max(3, int(5 * size_mult * scale))
        self.image = make_glow_circle(rad, col, core_white=True)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.direction = d.normalize() if d.length() > 0 else pygame.math.Vector2(0, 1)
        self.speed = spd * scale
        self.damage = dmg
        self.radius = max(2, rad - 1)

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if not c.PLAY_RECT.colliderect(self.rect):
            self.kill()


class ExpandingRingBullet(pygame.sprite.Sprite):
    """Сфера Фиолетового босса, увеличивающая свой радиус во время полёта."""

    def __init__(self, pos, d, spd, col, dmg=1):
        super().__init__()
        self.scale = _diff_scale()
        self.pos = pygame.math.Vector2(pos)
        self.direction = d.normalize() if d.length() > 0 else pygame.math.Vector2(0, 1)
        self.speed = spd * self.scale
        self.color = col
        self.damage = dmg
        self.exact_rad = 4.5 * self.scale
        self.radius = int(self.exact_rad)
        self.image = make_glow_circle(max(3, self.radius), col)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.pos += self.direction * self.speed
        self.exact_rad += 0.4 * self.scale
        r = max(3, int(self.exact_rad))
        self.image = make_glow_circle(r, self.color)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.radius = max(2, r - 1)
        if not c.PLAY_RECT.inflate(160, 160).colliderect(self.rect):
            self.kill()


class BulletTether(pygame.sprite.Sprite):
    """Энергетический луч, соединяющий два летящих снаряда между собой."""

    def __init__(self, b1, b2, dmg=1):
        super().__init__()
        self.b1, self.b2 = b1, b2
        self.damage = dmg
        self.is_firing = True
        self.start_pos = pygame.math.Vector2(b1.rect.center)
        self.end_pos = pygame.math.Vector2(b2.rect.center)
        self.image = pygame.Surface((c.W, c.H), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        if not self.b1.alive() or not self.b2.alive():
            self.kill()
            return
        self.start_pos = pygame.math.Vector2(self.b1.rect.center)
        self.end_pos = pygame.math.Vector2(self.b2.rect.center)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.line(self.image, (0, 180, 255, 110), self.start_pos, self.end_pos, 12)
        pygame.draw.line(self.image, c.C_CYAN, self.start_pos, self.end_pos, 6)
        pygame.draw.line(self.image, c.C_WHITE, self.start_pos, self.end_pos, 2)


class EnemyLaser(pygame.sprite.Sprite):
    """Лазерный луч с фазой прицеливания (тонкая линия) и фазой нанесения урона."""

    def __init__(self, owner, direction, dmg=1, warn_frames=30, fire_frames=30, width=16, color=c.C_CYAN, max_length=1400):
        super().__init__()
        scale = _diff_scale()
        self.owner = owner
        self.dir = direction.normalize() if direction.length() > 0 else pygame.math.Vector2(0, 1)
        self.damage = dmg
        self.warn_frames = max(8, int(warn_frames / scale))
        self.total_frames = self.warn_frames + max(8, int(fire_frames / scale))
        self.width = int(width * scale)
        self.color = color
        self.max_length = max_length
        self.timer = 0
        self.is_firing = False

        self.start_pos = pygame.math.Vector2(owner.rect.center)
        self.end_pos = self.start_pos + self.dir * self.max_length
        self.image = pygame.Surface((c.W, c.H), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        self.timer += 1
        if self.owner and self.owner.alive():
            self.start_pos = pygame.math.Vector2(self.owner.rect.center)
            self.end_pos = self.start_pos + self.dir * self.max_length

        self.image.fill((0, 0, 0, 0))
        if self.timer <= self.warn_frames:
            pygame.draw.line(self.image, (255, 70, 90, 170), self.start_pos, self.end_pos, 2)
        elif self.timer <= self.total_frames:
            self.is_firing = True
            pygame.draw.line(self.image, (*self.color[:3], 90), self.start_pos, self.end_pos, self.width + 10)
            pygame.draw.line(self.image, self.color, self.start_pos, self.end_pos, self.width)
            pygame.draw.line(self.image, c.C_WHITE, self.start_pos, self.end_pos, max(2, self.width // 3))
        else:
            self.kill()
