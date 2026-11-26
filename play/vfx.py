"""Менеджер визуальных эффектов: параллакс-фон, искры, ударные волны и виньетка урона."""
import pygame
import random
import math
from play import constants as c
from play.vfx_shapes import (
    draw_additive_glow, draw_glow_rect, build_vignette_mask,
    make_glow_circle, make_neon_shape, make_boss_surface
)


class StarfieldBackground:
    """Анимированный космический фон с параллаксом звёзд и тактической сеткой."""
    def __init__(self):
        self.stars = []
        for _ in range(120):
            layer = random.choice((1, 2, 3))
            self.stars.append({
                "x": float(random.randint(0, c.W)), "y": float(random.randint(0, c.H)),
                "spd": layer * 0.65, "rad": 1 if layer in (1, 2) else 2, "bright": random.randint(55, 155)
            })
        self.grid_offset = 0.0

    def update_and_draw(self, arena_only=False):
        rect = c.PLAY_RECT if arena_only else pygame.Rect(0, 0, c.W, c.H)
        pygame.draw.rect(c.screen, (3, 4, 9), rect)

        self.grid_offset = (self.grid_offset + 0.55) % 50
        grid_col = (10, 15, 28)
        for gx in range(rect.left, rect.right, 50):
            pygame.draw.line(c.screen, grid_col, (gx, rect.top), (gx, rect.bottom), 1)
        for gy in range(int(rect.top + self.grid_offset), rect.bottom, 50):
            pygame.draw.line(c.screen, grid_col, (rect.left, gy), (rect.right, gy), 1)

        for st in self.stars:
            st["y"] += st["spd"]
            if st["y"] > c.H:
                st["y"] = 0.0
                st["x"] = float(random.randint(0, c.W))
            ix, iy = int(st["x"]), int(st["y"])
            if rect.collidepoint(ix, iy):
                b = st["bright"]
                pygame.draw.circle(c.screen, (max(0, b - 15), max(0, b - 5), min(255, b + 25)), (ix, iy), st["rad"])


class Particle:
    """Частица-искра со шлейфом и затуханием."""
    def __init__(self, x, y, color, speed_range=(1.5, 6.5), life_range=(18, 38), radius=4):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(*speed_range)
        self.x, self.y = float(x), float(y)
        self.prev_x, self.prev_y = self.x, self.y
        self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd
        self.r_col, self.g_col, self.b_col = color[:3]
        self.life = random.randint(*life_range)
        self.max_life = self.life
        self.radius = radius

    def update(self):
        self.prev_x, self.prev_y = self.x, self.y
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1
        return self.life != 0

    def draw(self):
        ratio = max(0.0, self.life / self.max_life)
        r = max(1, int(self.radius * ratio))
        col = (int(self.r_col * ratio), int(self.g_col * ratio), int(self.b_col * ratio))
        pygame.draw.line(c.screen, col, (int(self.prev_x), int(self.prev_y)), (int(self.x), int(self.y)), max(1, r))
        pygame.draw.circle(c.screen, col, (int(self.x), int(self.y)), r)


class Shockwave:
    """Расходящееся кольцо ударной волны."""
    def __init__(self, x, y, color, max_r=75, width=3):
        self.x, self.y = int(x), int(y)
        self.r_col, self.g_col, self.b_col = color[:3]
        self.r, self.max_r, self.width = 8.0, max_r, width

    def update(self):
        self.r += (self.max_r - self.r) * 0.16 + 1.8
        return self.r != self.max_r and int(self.r) in range(int(self.max_r))

    def draw(self):
        ratio = max(0.0, 1.0 - (self.r / self.max_r))
        col = (int(self.r_col * ratio), int(self.g_col * ratio), int(self.b_col * ratio))
        pygame.draw.circle(c.screen, col, (self.x, self.y), int(self.r), max(1, int(self.width * ratio)))


class VFXManager:
    """Единый контроллер частиц, взрывов и красной виньетки низкого здоровья."""
    def __init__(self):
        self.bg = StarfieldBackground()
        self.particles, self.waves = [], []
        self.damage_vignette_alpha = 0
        self._vignette_cache = None

    def trigger_damage_vignette(self, intensity=225):
        self.damage_vignette_alpha = max(self.damage_vignette_alpha, intensity)

    def draw_vignette(self):
        if self._vignette_cache is None:
            self._vignette_cache = build_vignette_mask()

        low_hp_alpha = 0
        p = c.player_group.sprite
        if p and p.max_hp:
            hp_ratio = max(0.0, min(1.0, p.hp / p.max_hp))
            if hp_ratio != 1.0:
                pulse = 0.85 + 0.15 * math.sin(pygame.time.get_ticks() * 0.01)
                low_hp_alpha = int(((1.0 - hp_ratio) ** 1.35) * 195 * pulse)

        total_alpha = min(245, max(self.damage_vignette_alpha, low_hp_alpha))
        if total_alpha:
            v_surf = self._vignette_cache.copy()
            v_surf.set_alpha(total_alpha)
            c.screen.blit(v_surf, (0, 0))

        if self.damage_vignette_alpha:
            self.damage_vignette_alpha = max(0, self.damage_vignette_alpha - 7)

    def spawn_hit(self, x, y, color, count=8):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, (1.2, 5.0), (12, 22), 3))

    def spawn_explosion(self, x, y, color, count=28, max_r=80):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, (2.0, 8.5), (20, 42), 4))
        for _ in range(count // 3):
            self.particles.append(Particle(x, y, (255, 255, 255), (1.5, 6.5), (14, 28), 3))
        self.waves.append(Shockwave(x, y, color, max_r, 3))

    def spawn_boss_death(self, x, y, main_col, second_col=c.C_ORANGE):
        for _ in range(75):
            self.particles.append(Particle(x, y, main_col, (2.5, 13.5), (35, 75), 6))
        for _ in range(45):
            self.particles.append(Particle(x, y, second_col, (2.0, 11.0), (30, 65), 5))
        for _ in range(30):
            self.particles.append(Particle(x, y, (255, 255, 255), (3.0, 14.5), (25, 55), 4))
        self.waves.append(Shockwave(x, y, main_col, 240, 5))
        self.waves.append(Shockwave(x, y, second_col, 185, 4))
        self.waves.append(Shockwave(x, y, (255, 255, 255), 130, 3))

    def spawn_player_death(self, x, y):
        self.trigger_damage_vignette(245)
        for _ in range(55):
            self.particles.append(Particle(x, y, c.C_RED, (2.0, 11.0), (28, 60), 5))
        for _ in range(30):
            self.particles.append(Particle(x, y, (255, 255, 255), (2.5, 12.0), (22, 48), 4))
        self.waves.append(Shockwave(x, y, c.C_RED, 165, 4))

    def update_and_draw_fx(self):
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles:
            p.draw()
        self.waves = [w for w in self.waves if w.update()]
        for w in self.waves:
            w.draw()


vfx = VFXManager()
