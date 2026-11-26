import pygame
import math
from play import constants as c


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, pos, d, dmg, max_lifetime=-1, is_small=False, is_big_destroyer=False, is_purple_base=False,
                 is_brown_main=False, satellite_count=1, is_clearing_wave=False, is_rainbow_diamond=False,
                 homing_continuous=False, is_ability_diamond=False, bullet_color=None):
        super().__init__()
        self.is_big_destroyer = is_big_destroyer
        self.is_clearing_wave = is_clearing_wave
        self.is_brown_main = is_brown_main
        self.is_purple_base = is_purple_base
        self.is_rainbow_diamond = is_rainbow_diamond
        self.is_ability_diamond = is_ability_diamond
        self.homing_continuous = homing_continuous
        self.satellite_count = satellite_count
        self.lifetime = max_lifetime
        self.bullet_color = bullet_color

        if is_clearing_wave:
            self.size_w, self.size_h = 120, 120
        elif is_big_destroyer:
            self.size_w, self.size_h = 48, 48
        elif is_purple_base or is_brown_main:
            self.size_w, self.size_h = 16, 32
        elif is_rainbow_diamond:
            self.size_w, self.size_h = 20, 36
        elif is_small:
            self.size_w, self.size_h = 6, 12
        else:
            self.size_w, self.size_h = 8, 16

        self.base_image = pygame.Surface((self.size_w + 60, self.size_h + 60), pygame.SRCALPHA)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.direction = d.normalize() if d.length() > 0 else pygame.math.Vector2(0, -1)
        self.speed = 4 if is_clearing_wave else (6 if is_big_destroyer else 10)
        self.damage = dmg
        self.angle_offset = 0.0

    def _resolve_color(self, fallback):
        if self.bullet_color is not None:
            return self.bullet_color
        p = c.player_group.sprite
        if p and isinstance(p.color_type, tuple):
            return p.color_type
        return fallback

    def update(self):
        if self.homing_continuous:
            target_pos = None
            boss_found = False
            min_dist = 999999

            for enemy in c.enemies:
                if enemy.alive() and enemy.__class__.__name__ != 'Dummy':
                    is_boss = hasattr(enemy, 'max_hp') and enemy.max_hp > 50
                    if is_boss and not boss_found:
                        target_pos = enemy.rect.center
                        boss_found = True
                    elif not boss_found:
                        d_vec = pygame.math.Vector2(enemy.rect.center) - self.pos
                        if d_vec.length() < min_dist:
                            min_dist = d_vec.length()
                            target_pos = enemy.rect.center

            if target_pos:
                dir_to_target = pygame.math.Vector2(target_pos) - self.pos
                if dir_to_target.length() > 0:
                    self.direction = dir_to_target.normalize()

        self.pos += self.direction * self.speed
        self.base_image.fill((0, 0, 0, 0))

        center_x = (self.size_w + 60) // 2
        center_y = (self.size_h + 60) // 2

        if self.is_clearing_wave:
            col = self._resolve_color(c.C_PURPLE)
            pygame.draw.circle(self.base_image, col, (center_x, center_y), self.size_w // 2, 4)
            pygame.draw.circle(self.base_image, c.C_WHITE, (center_x, center_y), self.size_w // 2 - 4, 1)
        elif self.is_rainbow_diamond:
            r = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
            g = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01 + 2))
            b = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01 + 4))
            points = [
                (center_x, center_y - self.size_h // 2),
                (center_x + self.size_w // 2, center_y),
                (center_x, center_y + self.size_h // 2),
                (center_x - self.size_w // 2, center_y)
            ]
            pygame.draw.polygon(self.base_image, (r, g, b), points)
            pygame.draw.polygon(self.base_image, c.C_WHITE, points, 1)
        elif self.is_brown_main:
            col = self._resolve_color(c.C_PURPLE)
            pygame.draw.ellipse(self.base_image, col,
                                (center_x - self.size_w // 2, center_y - self.size_h // 2, self.size_w, self.size_h))
            pygame.draw.ellipse(self.base_image, c.C_WHITE,
                                (center_x - self.size_w // 2, center_y - self.size_h // 2, self.size_w, self.size_h), 1)
        elif self.is_big_destroyer:
            col = self._resolve_color(c.C_RED)
            pygame.draw.ellipse(self.base_image, col,
                                (center_x - self.size_w // 2, center_y - self.size_h // 2, self.size_w, self.size_h))
            pygame.draw.ellipse(self.base_image, c.C_ORANGE,
                                (center_x - self.size_w // 3, center_y - self.size_h // 3, self.size_w * 2 // 3, self.size_h * 2 // 3))
        elif self.is_purple_base:
            col = self._resolve_color(c.C_CYAN)
            pygame.draw.ellipse(self.base_image, col,
                                (center_x - self.size_w // 2, center_y - self.size_h // 2, self.size_w, self.size_h))
            pygame.draw.ellipse(self.base_image, c.C_WHITE,
                                (center_x - self.size_w // 2, center_y - self.size_h // 2, self.size_w, self.size_h), 1)
        else:
            col = self._resolve_color(c.C_WHITE)
            pygame.draw.ellipse(self.base_image, col,
                                (center_x - self.size_w // 2, center_y - self.size_h // 2, self.size_w, self.size_h))

        if self.is_brown_main:
            self.angle_offset += 0.1
            for i in range(self.satellite_count):
                ang = self.angle_offset + (i * (math.pi * 2 / self.satellite_count))
                sx = center_x + int(math.cos(ang) * 25)
                sy = center_y + int(math.sin(ang) * 25)
                pygame.draw.circle(self.base_image, c.C_WHITE, (sx, sy), 4)

        angle_deg = math.degrees(math.atan2(-self.direction.x, -self.direction.y))
        self.image = pygame.transform.rotate(self.base_image, angle_deg)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        if self.is_big_destroyer or self.is_clearing_wave or self.is_ability_diamond:
            pygame.sprite.spritecollide(self, c.enemy_bullets, True)

        if self.lifetime > 0:
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.kill()
        if not c.PLAY_RECT.colliderect(self.rect):
            self.kill()


class OrbitShield(pygame.sprite.Sprite):
    """Орбитальный защитный шар Защитника (голубой неон)"""

    def __init__(self, color=c.C_CYAN):
        super().__init__()
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (9, 9), 9)
        pygame.draw.circle(self.image, c.C_WHITE, (9, 9), 3)
        self.rect = self.image.get_rect()
        self.damage = 1

    def update(self):
        hits = pygame.sprite.spritecollide(self, c.enemy_bullets, True)
        if hits:
            self.kill()


class PlayerClone(pygame.sprite.Sprite):
    """Визуальный клон Абсолюта, следующий за игроком"""

    def __init__(self, player, side):
        super().__init__()
        self.player = player
        self.side = side
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.damage = 0

    def update(self):
        if not self.player.alive() or not getattr(self.player, 'rainbow_clones_active', False):
            self.kill()
            return

        offset = -50 if self.side == 'left' else 50
        self.rect.centerx = self.player.rect.centerx + offset
        self.rect.centery = self.player.rect.centery

        self.image.fill((0, 0, 0, 0))
        t = pygame.time.get_ticks() * 0.005
        col = (int(128 + 127 * math.sin(t)), int(128 + 127 * math.sin(t + 2)), int(128 + 127 * math.sin(t + 4)))
        pygame.draw.circle(self.image, col, (16, 16), 16)
        pygame.draw.circle(self.image, (240, 240, 240), (16, 16), 4)
        self.image.set_alpha(150)

        if pygame.sprite.spritecollide(self, c.enemy_bullets, True):
            self.kill()
            return

        if pygame.sprite.spritecollide(self, c.enemies, False):
            self.kill()
            return
