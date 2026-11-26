"""Обработка активных способностей (клавиши V и B) и орбитальных щитов игрока."""
import pygame
import math
import random
from play import menu_screens as ms, projectiles as p_mod, constants as c
from player.player_projectiles import PlayerClone


def apply_speed_buffs(player):
    """Применяет временные бонусы скорости от активных способностей."""
    if player.char_id == 1 and player.speed_buff_timer > 0:
        player.speed_buff_timer -= 1
        player.speed = int(player.base_speed * 2.2)
    elif player.char_id == 4 and player.brown_v_active:
        player.brown_v_timer -= 1
        player.speed = int(player.base_speed * 1.5)
        if player.brown_v_timer <= 0:
            player.brown_v_active = False
    elif player.char_id == 5 and getattr(player, 'swamp_v_speed_timer', 0) > 0:
        player.swamp_v_speed_timer -= 1
        player.speed = int(player.base_speed * 2.0)


def handle_purple_orbits(player):
    """Вращает и обновляет орбитальные защитные сферы Защитника (char_id == 3)."""
    if player.char_id == 3 and len(player.orbit_shields) > 0:
        player.orbit_angle += 0.05
        player.purple_life_timer -= 1
        if player.purple_life_timer <= 0:
            player.orbit_shields.empty()
        else:
            for i, orb in enumerate(player.orbit_shields):
                angle = player.orbit_angle + (i * (math.pi * 2 / len(player.orbit_shields)))
                orb.rect.centerx = player.rect.centerx + int(math.cos(angle) * 55)
                orb.rect.centery = player.rect.centery + int(math.sin(angle) * 55)
            player.orbit_shields.update()
            player.orbit_shields.draw(c.screen)


def handle_active_abilities(player, k):
    """Активирует и поддерживает уникальные способности V и B для выбранного героя."""
    from player.player_shooting import get_homing_dir

    caster_positions = [player.rect.center]
    if player.char_id == 6 and getattr(player, 'rainbow_clones_active', False):
        for sprite in c.player_bullets:
            if sprite.__class__.__name__ == 'PlayerClone' and sprite.alive():
                caster_positions.append(sprite.rect.center)

    # 1. Стандарт: V — веер из 5 пуль, B — ускорение движения
    if player.char_id == 1:
        if k[pygame.K_v] and player.v_cooldown == 0 and player.red_v_burst_count == 0:
            player.v_cooldown, player.red_v_burst_count, player.red_v_burst_delay = 300, 2, 0
        if player.red_v_burst_count > 0:
            player.red_v_burst_delay += 1
            if player.red_v_burst_delay >= 10 or player.red_v_burst_delay == 1:
                if player.red_v_burst_delay >= 10:
                    player.red_v_burst_delay = 1
                player.red_v_burst_count -= 1
                for angle in [-20, -10, 0, 10, 20]:
                    vec = pygame.math.Vector2(math.cos(math.radians(-90 + angle)), math.sin(math.radians(-90 + angle)))
                    c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, vec, 1, max_lifetime=24, is_small=True))
                    ms.session_bullets += 1
        if k[pygame.K_b] and player.b_cooldown == 0:
            player.b_cooldown, player.speed_buff_timer = 900, 180

    # 2. Штурмовик: V — скоростная очередь, B — гигантский разрушающий снаряд
    elif player.char_id == 2:
        if k[pygame.K_v] and player.v_cooldown == 0 and player.blue_v_queue == 0:
            player.v_cooldown, player.blue_v_queue, player.blue_v_delay = 480, 8, 0
        if player.blue_v_queue > 0:
            player.blue_v_delay += 1
            if player.blue_v_delay >= 4:
                player.blue_v_delay, player.blue_v_queue = 0, player.blue_v_queue - 1
                bullet = p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), player.damage)
                bullet.speed = 20
                c.player_bullets.add(bullet)
                ms.session_bullets += 1
        if k[pygame.K_b] and player.b_cooldown == 0:
            player.b_cooldown = 1500
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), 10, is_big_destroyer=True))
            ms.session_bullets += 1

    # 3. Защитник: V — тройной залп, B — 6 орбитальных щитов
    elif player.char_id == 3:
        if k[pygame.K_v] and player.v_cooldown == 0:
            player.v_cooldown = 300
            for ox, oy in [(0, -25), (40, 0), (-40, 0)]:
                c.player_bullets.add(p_mod.PlayerBullet((player.rect.centerx + ox, player.rect.centery + oy), pygame.math.Vector2(0, -1), player.damage, is_purple_base=True))
            ms.session_bullets += 3
        if k[pygame.K_b] and player.b_cooldown == 0:
            player.b_cooldown, player.purple_life_timer = 1200, 360
            player.orbit_shields.empty()
            for _ in range(6):
                player.orbit_shields.add(p_mod.OrbitShield())

    # 4. Призрак: V — бафф спутников, B — золотой щит или очищающая волна
    elif player.char_id == 4:
        if k[pygame.K_v] and player.v_cooldown == 0 and not player.brown_v_active:
            player.v_cooldown, player.brown_v_active, player.brown_v_timer = 540, True, 240
        if k[pygame.K_b]:
            if player.brown_v_active:
                player.brown_v_active, player.brown_v_timer = False, 0
                c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), 0, max_lifetime=120, is_clearing_wave=True))
            elif player.b_cooldown == 0 and not player.yellow_shield_active:
                player.b_cooldown, player.yellow_shield_active, player.yellow_shield_timer = 1620, True, 420

    # 5. Спектр: V — фазовый рывок, B — шквал самонаводящихся игл
    elif player.char_id == 5:
        if k[pygame.K_v] and player.v_cooldown == 0:
            player.v_cooldown = 720
            dx = (-1 if (k[pygame.K_LEFT] or k[pygame.K_a]) else 0) + (1 if (k[pygame.K_RIGHT] or k[pygame.K_d]) else 0)
            dy = (-1 if (k[pygame.K_UP] or k[pygame.K_w]) else 0) + (1 if (k[pygame.K_DOWN] or k[pygame.K_s]) else 0)
            if dx == 0 and dy == 0:
                dy = -1
            player.rect.x += dx * 192
            player.rect.y += dy * 192
            player.rect.clamp_ip(c.PLAY_RECT)
            player.invulnerable = True
            player.invuln_timer = 60
            player.swamp_v_speed_timer = 180

        if k[pygame.K_b] and player.b_cooldown == 0 and not player.swamp_b_active:
            player.b_cooldown, player.swamp_b_active, player.swamp_b_timer = 900, True, 120
            player.invulnerable = True
            player.invuln_timer = 120
            player.rect.y += 45
            player.rect.clamp_ip(c.PLAY_RECT)

    # 6. Абсолют: V — веер ромбов, B — призыв 2 боевых клонов
    elif player.char_id == 6:
        if k[pygame.K_v] and player.v_cooldown == 0:
            player.v_cooldown = 900
            for center_pos in caster_positions:
                start_x = center_pos[0] - 150
                for i in range(6):
                    spawn_x = max(c.PLAY_RECT.left + 15, min(c.PLAY_RECT.right - 15, start_x + (i * 60)))
                    spawn_y = min(c.H - 20, center_pos[1] + random.randint(40, 80))
                    spawn_pos = (spawn_x, spawn_y)
                    c.player_bullets.add(p_mod.PlayerBullet(spawn_pos, get_homing_dir(spawn_pos), player.damage, is_rainbow_diamond=True, is_ability_diamond=True))
                    ms.session_bullets += 1

        if k[pygame.K_b] and player.b_cooldown == 0:
            player.b_cooldown = 2100
            player.invulnerable = True
            player.invuln_timer = 180
            setattr(player, 'rainbow_clones_active', True)
            setattr(player, 'rainbow_clones_timer', 600)
            c.player_bullets.add(PlayerClone(player, 'left'))
            c.player_bullets.add(PlayerClone(player, 'right'))

    if player.char_id == 6 and getattr(player, 'rainbow_clones_active', False):
        player.rainbow_clones_timer -= 1
        if player.rainbow_clones_timer <= 0:
            player.rainbow_clones_active = False
