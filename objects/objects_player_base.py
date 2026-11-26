"""Базовый класс игрока: управление движением, щитом (C) и таймерами."""
import pygame
import math
from play import constants as c
from play.sfx import sfx


class Player(pygame.sprite.Sprite):
    def __init__(self, s):
        super().__init__()
        self.char_id = s["id"]
        self.base_speed = 4 if self.char_id == 6 else s["speed"]
        self.speed = self.base_speed

        self.damage = s["damage"]
        self.hp = s["hp"]
        self.max_hp = s["hp"]
        self.color_type = s["color"]
        self.has_ability = True

        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(c.PLAY_RECT.centerx, c.H - 100))
        self.radius = 4  # Малый радиус хитбокса в центре для точного уклонения
        self.cooldown = 0

        # Длительность и откат щита (клавиша C) для каждого из 6 персонажей
        shield_cfg = {1: (36, 300), 2: (30, 420), 3: (48, 240), 4: (24, 480), 5: (60, 300), 6: (78, 240)}
        self.shield_duration, self.shield_max_cd = shield_cfg.get(self.char_id, (36, 300))

        self.invulnerable = False
        self.invuln_timer = 0
        self.dash_cooldown = 0
        self.c_was_pressed = False

        # Таймеры и очереди способностей (V / B)
        self.v_cooldown, self.b_cooldown = 0, 0
        self.speed_buff_timer = 0
        self.red_v_burst_count, self.red_v_burst_delay = 0, 0
        self.blue_normal_queue, self.blue_normal_delay = 0, 0
        self.blue_v_queue, self.blue_v_delay = 0, 0

        self.orbit_shields = pygame.sprite.Group()
        self.orbit_angle = 0.0
        self.purple_life_timer = 0

        self.brown_satellites_count = 1
        self.brown_v_active, self.brown_v_timer = False, 0
        self.yellow_shield_active, self.yellow_shield_timer = False, 0

        self.swamp_v_speed_timer = 0
        self.swamp_b_active, self.swamp_b_timer = False, 0

    def update(self):
        """Обновляет отрисовку, перемещение, кулдауны и вызов модулей стрельбы/скиллов."""
        k = pygame.key.get_pressed()
        self.image.fill((0, 0, 0, 0))

        current_color = (
            int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.005)), 100, 200
        ) if self.color_type == "rainbow" else self.color_type
        pygame.draw.circle(self.image, current_color, (16, 16), 16)
        pygame.draw.circle(self.image, c.C_WHITE, (16, 16), 4)

        if self.char_id == 4 and self.yellow_shield_active:
            self.yellow_shield_timer -= 1
            pygame.draw.circle(c.screen, (255, 215, 0), self.rect.center, 28, 3)
            if self.yellow_shield_timer <= 0:
                self.yellow_shield_active = False

        if self.char_id == 5 and self.swamp_b_active:
            self.swamp_b_timer -= 1
            if self.swamp_b_timer <= 0:
                self.swamp_b_active = False

        # Замедление при удержании Shift для точного маневрирования
        self.speed = max(1, self.base_speed // 2) if (k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT]) else self.base_speed

        from player import player_skills as skills
        from player import player_shooting as shooting
        skills.apply_speed_buffs(self)

        # Активация неуязвимости на клавишу C
        if k[pygame.K_c]:
            if not self.c_was_pressed and self.dash_cooldown == 0:
                self.invulnerable = True
                self.invuln_timer = self.shield_duration
                self.dash_cooldown = self.shield_max_cd
                self.c_was_pressed = True
                sfx.play("pickup")
        else:
            self.c_was_pressed = False

        if self.invuln_timer > 0:
            self.invuln_timer -= 1
            if self.invuln_timer == 0:
                self.invulnerable = False

        self.dash_cooldown = max(0, self.dash_cooldown - 1)
        self.v_cooldown = max(0, self.v_cooldown - 1)
        self.b_cooldown = max(0, self.b_cooldown - 1)

        if k[pygame.K_LEFT] or k[pygame.K_a]:
            self.rect.x -= self.speed
        if k[pygame.K_RIGHT] or k[pygame.K_d]:
            self.rect.x += self.speed
        if k[pygame.K_UP] or k[pygame.K_w]:
            self.rect.y -= self.speed
        if k[pygame.K_DOWN] or k[pygame.K_s]:
            self.rect.y += self.speed
        self.rect.clamp_ip(c.PLAY_RECT)

        # Мерцание спрайта во время действия щита
        is_shielded = self.invulnerable or (self.char_id == 4 and self.yellow_shield_active) or (self.char_id == 5 and self.swamp_b_active)
        self.image.set_alpha(100 if (is_shielded and pygame.time.get_ticks() % 100 < 50) else 255)

        prev_v, prev_b = self.v_cooldown, self.b_cooldown
        skills.handle_purple_orbits(self)
        shooting.handle_auto_shoot(self)
        skills.handle_active_abilities(self, k)
        if (prev_v == 0 and self.v_cooldown > 0) or (prev_b == 0 and self.b_cooldown > 0):
            sfx.play("pickup")
