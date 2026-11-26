import pygame
import math
from play import projectiles as p_mod, constants as c


def apply_speed_buffs(player):
    if player.char_id == 1 and player.speed_buff_timer > 0:
        player.speed_buff_timer -= 1
        player.speed = int(player.base_speed * 2.2)
    elif player.char_id == 4 and player.brown_v_active:
        player.brown_v_timer -= 1
        player.speed = int(player.base_speed * 1.5)
        if player.brown_v_timer <= 0: player.brown_v_active = False

def handle_purple_orbits(player):
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

def handle_auto_shoot(player):
    player.cooldown += 1
    if player.cooldown >= 30:
        player.cooldown = 0
        from play import menu_screens as ms
        if player.char_id == 1:
            c.player_bullets.add(p_mod.PlayerBullet((player.rect.centerx - 10, player.rect.centery), pygame.math.Vector2(0, -1), player.damage))
            c.player_bullets.add(p_mod.PlayerBullet((player.rect.centerx + 10, player.rect.centery), pygame.math.Vector2(0, -1), player.damage))
            ms.session_bullets += 2
        elif player.char_id == 2:
            player.blue_normal_queue, player.blue_normal_delay = 3, 0
        elif player.char_id == 3:
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), player.damage, is_purple_base=True))
            ms.session_bullets += 1
        elif player.char_id == 4:
            curr = 4 if player.brown_v_active else player.brown_satellites_count
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), player.damage, is_brown_main=True, satellite_count=curr))
            ms.session_bullets += 1
            if not player.brown_v_active:
                player.brown_satellites_count += 1
                if player.brown_satellites_count > 4: player.brown_satellites_count = 1
        else:
            for a in [-15, 0, 15]:
                r = math.radians(-90 + a)
                c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(math.cos(r), math.sin(r)), player.damage))
                ms.session_bullets += 1

    if player.char_id == 2 and player.blue_normal_queue > 0:
        player.blue_normal_delay += 1
        if player.blue_normal_delay >= 5:
            player.blue_normal_delay, player.blue_normal_queue = 0, player.blue_normal_queue - 1
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), player.damage))
            ms.session_bullets += 1

def handle_active_abilities(player, k):
    from play import menu_screens as ms
    if player.char_id == 1:
        if k[pygame.K_v] and player.v_cooldown == 0 and player.red_v_burst_count == 0:
            player.v_cooldown, player.red_v_burst_count, player.red_v_burst_delay = 300, 2, 0
        if player.red_v_burst_count > 0:
            player.red_v_burst_delay += 1
            if player.red_v_burst_delay >= 10 or player.red_v_burst_delay == 1:
                if player.red_v_burst_delay >= 10: player.red_v_burst_delay = 1
                player.red_v_burst_count -= 1
                for angle in [-20, -10, 0, 10, 20]:
                    c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(math.cos(math.radians(-90 + angle)), math.sin(math.radians(-90 + angle))), 1, max_lifetime=24, is_small=True))
                    ms.session_bullets += 1
        if k[pygame.K_b] and player.b_cooldown == 0: player.b_cooldown, player.speed_buff_timer = 900, 180

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

    elif player.char_id == 3:
        if k[pygame.K_v] and player.v_cooldown == 0:
            player.v_cooldown = 300
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), player.damage, is_purple_base=True))
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(1, 0), player.damage, is_purple_base=True))
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(-1, 0), player.damage, is_purple_base=True))
            ms.session_bullets += 3
        if k[pygame.K_b] and player.b_cooldown == 0:
            player.b_cooldown, player.purple_life_timer = 1200, 360
            player.orbit_shields.empty()
            for _ in range(6): player.orbit_shields.add(p_mod.OrbitShield())

    elif player.char_id == 4:
        if k[pygame.K_v] and player.v_cooldown == 0 and not player.brown_v_active:
            player.v_cooldown, player.brown_v_active, player.brown_v_timer = 540, True, 240
        if k[pygame.K_b]:
            if player.brown_v_active:
                player.brown_v_active, player.brown_v_timer = False, 0
                c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), 0, max_lifetime=60, is_clearing_wave=True))
            elif player.b_cooldown == 0 and not player.yellow_shield_active:
                player.b_cooldown, player.yellow_shield_active, player.yellow_shield_timer = 1620, True, 420
