"""Демонстрационная арена в главном меню: живой бой ботов, барьер и пульсирующий заголовок."""
import pygame
import random
import math
from play import constants as c
from play import game_data as gd
from play.enemies import ENEMY_CONFIGS
from play.vfx import make_neon_shape, make_glow_circle, draw_additive_glow, vfx

SPLIT_X = int(c.W * 0.72)
ALL_KINDS = list(ENEMY_CONFIGS.keys())
MAX_MENU_ENEMIES = 9


class MenuFlashSegment:
    """Красная вспышка на чёрной разделительной линии при попадании пули."""

    def __init__(self, y):
        self.y = y
        self.timer = 30

    def update(self):
        self.timer -= 1
        return self.timer != 0

    def draw(self):
        ratio = max(0.0, self.timer / 30.0)
        col = (int(255 * ratio), int(25 * ratio), int(45 * ratio))
        draw_additive_glow(SPLIT_X, int(self.y), int(34 * ratio) + 6, (255, 30, 50), intensity=int(130 * ratio))
        pygame.draw.line(c.screen, col, (SPLIT_X, int(self.y - 26)), (SPLIT_X, int(self.y + 26)), 8)


class MenuDemoBullet:
    """Снаряд демонстрационной битвы в левой части главного меню."""

    def __init__(self, x, y, vx, color, is_player=False, dmg=1):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.color = color
        self.is_player = is_player
        self.dmg = dmg
        self.radius = 6 if is_player else 5
        self.image = make_glow_circle(self.radius, color, core_white=True)
        self.alive = True

    def update(self, flashes):
        prev_x = self.x
        self.x += self.vx

        # При столкновении с барьером SPLIT_X пуля исчезает и оставляет красную вспышку
        if (prev_x in range(SPLIT_X) and self.x >= SPLIT_X - self.radius) or (prev_x >= SPLIT_X and self.x <= SPLIT_X + self.radius):
            flashes.append(MenuFlashSegment(self.y))
            self.alive = False
            return

        if int(self.x) in range(10):
            self.alive = False

    def draw(self):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        c.screen.blit(self.image, rect)


class MenuDemoEnemy:
    """Бот-враг для фоновой демонстрации в левой половине меню."""

    def __init__(self):
        self.kind = random.choice(ALL_KINDS)
        cfg = ENEMY_CONFIGS[self.kind]
        self.color = cfg["color"]
        self.shape = cfg["shape"]
        self.hp = cfg["hp"]
        self.vx = random.choice((-1, 1)) * cfg["speed"]
        self.cd = cfg["cd"]
        self.timer = random.randint(0, max(1, self.cd // 2))

        self.x = float(random.randint(70, SPLIT_X // 2 - 80))
        self.y = float(random.randint(180, c.H - 90))
        self.radius = 20

        base_surf = make_neon_shape(self.shape, self.color, 44)
        self.image = pygame.transform.rotate(base_surf, 90)

    def update(self, bullets):
        self.x += self.vx
        if int(self.x) in range(51):
            self.x = 50.0
            self.vx = abs(self.vx)
        elif self.x >= SPLIT_X // 2 - 40:
            self.x = float(SPLIT_X // 2 - 40)
            self.vx = -abs(self.vx)

        self.timer += 1
        if self.timer >= self.cd:
            self.timer = 0
            bullets.append(MenuDemoBullet(self.x + 20, self.y, 6.0, self.color, is_player=False))

    def draw(self):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        c.screen.blit(self.image, rect)


def draw_neon_player_model(cx, cy, col, radius=18):
    """Отрисовывает многослойную неоновую модель игрока для меню и карточек выбора."""
    rc, gc, bc = col[:3]
    draw_additive_glow(cx, cy, int(radius * 1.9), (rc, gc, bc), intensity=65)
    pygame.draw.circle(c.screen, (14, 18, 30), (cx, cy), radius)
    pygame.draw.circle(c.screen, (rc, gc, bc), (cx, cy), radius, 4)
    pygame.draw.circle(c.screen, (min(255, rc + 70), min(255, gc + 70), min(255, bc + 70)), (cx, cy), int(radius * 0.62), 2)
    pygame.draw.circle(c.screen, (255, 255, 255), (cx, cy), 5)


class MenuBattleArena:
    """Управляет симуляцией боя в меню, кликами по врагам и анимацией логотипа."""

    def __init__(self):
        self.enemies = [MenuDemoEnemy() for _ in range(MAX_MENU_ENEMIES)]
        self.bullets = []
        self.flashes = []
        self.respawn_timers = []

        self.px = float(SPLIT_X - 180)
        self.py = float(c.H // 2 + 60)
        self.pvx = 3.2
        self.pvy = 2.4
        self.shoot_timer = 0

        self.title_timer = 0
        self.pulse_phase = 0.0
        f_title = pygame.font.SysFont("Arial", 54, bold=True)

        s1 = f_title.render("Пулевой ад: ", True, c.C_WHITE)
        s2 = f_title.render("ФОРМА", True, (35, 85, 235))
        s3 = f_title.render("ция", True, c.C_ORANGE)
        w = s1.get_width() + s2.get_width() + s3.get_width()
        h = max(s1.get_height(), s2.get_height(), s3.get_height())

        self.normal_title_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self.normal_title_surf.blit(s1, (0, 0))
        self.normal_title_surf.blit(s2, (s1.get_width(), 0))
        self.normal_title_surf.blit(s3, (s1.get_width() + s2.get_width(), 0))

        self.red_title_surf = f_title.render("Пулевой ад: ФОРМАция", True, c.C_RED)

    def _draw_animated_title(self):
        """Чередует плавную пульсацию заголовка (3 сек) и красную тряску (1 сек)."""
        self.title_timer += 1
        cycle_pos = self.title_timer % 240
        is_frozen = cycle_pos >= 180

        if not is_frozen:
            self.pulse_phase += 0.08
            base_surf = self.normal_title_surf
            shake_x, shake_y = 0, 0
            glow_col = (40, 90, 220)
        else:
            base_surf = self.red_title_surf
            shake_x = random.randint(-4, 4)
            shake_y = random.randint(-4, 4)
            glow_col = (240, 30, 45)

        scale = 1.0 + 0.09 * math.sin(self.pulse_phase)
        new_w = max(1, int(base_surf.get_width() * scale))
        new_h = max(1, int(base_surf.get_height() * scale))
        scaled_surf = pygame.transform.smoothscale(base_surf, (new_w, new_h))

        cx = SPLIT_X // 2 + shake_x
        cy = 78 + shake_y
        draw_additive_glow(cx, cy, 130, glow_col, intensity=50)
        c.screen.blit(scaled_surf, scaled_surf.get_rect(center=(cx, cy)))

    def _get_char_color(self):
        col = gd.selected_char["color"]
        if col == "rainbow":
            t = pygame.time.get_ticks() * 0.005
            return (int(128 + 127 * math.sin(t)), int(128 + 127 * math.sin(t + 2)), int(128 + 127 * math.sin(t + 4)))
        return col

    def update_and_draw(self, mouse_clicked=False):
        vfx.bg.update_and_draw(arena_only=False)
        self._draw_animated_title()

        # Интерактивное уничтожение ботов кликом мыши в меню
        if mouse_clicked:
            mx, my = pygame.mouse.get_pos()
            for e in list(self.enemies):
                if math.hypot(mx - e.x, my - e.y) <= e.radius + 8:
                    vfx.spawn_explosion(e.x, e.y, e.color, 20, 55)
                    self.enemies.remove(e)
                    self.respawn_timers.append(60)
                    break

        new_timers = []
        for t in self.respawn_timers:
            if t - 1 == 0:
                if len(self.enemies) != MAX_MENU_ENEMIES:
                    self.enemies.append(MenuDemoEnemy())
            else:
                new_timers.append(t - 1)
        self.respawn_timers = new_timers

        for e in self.enemies:
            e.update(self.bullets)
            e.draw()

        p_spd = gd.selected_char["speed"]
        self.px += math.copysign(p_spd, self.pvx)
        if self.px <= SPLIT_X // 2 + 60:
            self.px, self.pvx = float(SPLIT_X // 2 + 60), abs(self.pvx)
        elif self.px >= SPLIT_X - 60:
            self.px, self.pvx = float(SPLIT_X - 60), -abs(self.pvx)

        self.py += self.pvy
        if self.py <= 180:
            self.py, self.pvy = 180.0, abs(self.pvy)
        elif self.py >= c.H - 90:
            self.py, self.pvy = float(c.H - 90), -abs(self.pvy)

        p_col = self._get_char_color()
        self.shoot_timer += 1
        if self.shoot_timer >= 14:
            self.shoot_timer = 0
            self.bullets.append(MenuDemoBullet(self.px - 22, self.py, -8.5, p_col, is_player=True, dmg=gd.selected_char["damage"]))

        alive_bullets = []
        for b in self.bullets:
            b.update(self.flashes)
            if not b.alive:
                continue
            if b.is_player:
                hit_enemy = next((e for e in self.enemies if math.hypot(b.x - e.x, b.y - e.y) <= e.radius + b.radius), None)
                if hit_enemy:
                    b.alive = False
                    vfx.spawn_hit(b.x, b.y, hit_enemy.color, 5)
                    hit_enemy.hp = max(0, hit_enemy.hp - b.dmg)
                    if hit_enemy.hp == 0:
                        vfx.spawn_explosion(hit_enemy.x, hit_enemy.y, hit_enemy.color, 20, 55)
                        self.enemies.remove(hit_enemy)
                        self.respawn_timers.append(60)
                    continue
            b.draw()
            alive_bullets.append(b)
        self.bullets = alive_bullets

        vfx.update_and_draw_fx()
        draw_neon_player_model(int(self.px), int(self.py), p_col, 18)

        pygame.draw.line(c.screen, (0, 0, 0), (SPLIT_X, 0), (SPLIT_X, c.H), 8)
        self.flashes = [f for f in self.flashes if f.update()]
        for f in self.flashes:
            f.draw()


demo_arena = MenuBattleArena()
