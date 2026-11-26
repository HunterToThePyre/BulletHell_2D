"""Логика автоматической стрельбы всех персонажей и расчёт вектора наведения."""
import pygame
from play import menu_screens as ms, projectiles as p_mod, constants as c


def get_homing_dir(origin_pos):
    """Вычисляет нормализованный вектор до ближайшего врага или активного босса."""
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
                d = pygame.math.Vector2(enemy.rect.center) - pygame.math.Vector2(origin_pos)
                if d.length() < min_dist:
                    min_dist = d.length()
                    target_pos = enemy.rect.center

    if target_pos:
        dir_vec = pygame.math.Vector2(target_pos) - pygame.math.Vector2(origin_pos)
        return dir_vec.normalize() if dir_vec.length() > 0 else pygame.math.Vector2(0, -1)
    return pygame.math.Vector2(0, -1)


def handle_auto_shoot(player):
    """Выполняет регулярную стрельбу с учётом особенностей персонажа и активных клонов."""
    player.cooldown += 1
    shoot_delay = 6 if (player.char_id == 5 and getattr(player, 'swamp_b_active', False)) else 30

    if player.cooldown >= shoot_delay:
        player.cooldown = 0
        shoot_positions = [player.rect.center]

        # Добавляем позиции живых клонов для 6-го персонажа
        if player.char_id == 6 and getattr(player, 'rainbow_clones_active', False):
            for sprite in c.player_bullets:
                if sprite.__class__.__name__ == 'PlayerClone' and sprite.alive():
                    shoot_positions.append(sprite.rect.center)

        for pos in shoot_positions:
            if player.char_id == 1:
                c.player_bullets.add(p_mod.PlayerBullet((pos[0] - 8, pos[1]), pygame.math.Vector2(0, -1), player.damage))
                c.player_bullets.add(p_mod.PlayerBullet((pos[0] + 8, pos[1]), pygame.math.Vector2(0, -1), player.damage))
                ms.session_bullets += 2
            elif player.char_id == 2:
                player.blue_normal_queue, player.blue_normal_delay = 3, 0
            elif player.char_id == 3:
                c.player_bullets.add(p_mod.PlayerBullet(pos, pygame.math.Vector2(0, -1), player.damage, is_purple_base=True))
                ms.session_bullets += 1
            elif player.char_id == 4:
                curr = 3 if player.brown_v_active else player.brown_satellites_count
                c.player_bullets.add(p_mod.PlayerBullet(pos, pygame.math.Vector2(0, -1), player.damage, is_brown_main=True, satellite_count=curr))
                ms.session_bullets += 1
            elif player.char_id == 5:
                d_spawn = get_homing_dir(pos)
                perp = pygame.math.Vector2(-d_spawn.y, d_spawn.x) * 12
                c.player_bullets.add(p_mod.PlayerBullet(pygame.math.Vector2(pos) + d_spawn * 15, d_spawn, 1, is_small=True))
                c.player_bullets.add(p_mod.PlayerBullet(pygame.math.Vector2(pos) - perp, d_spawn, 1, is_small=True))
                c.player_bullets.add(p_mod.PlayerBullet(pygame.math.Vector2(pos) + perp, d_spawn, 1, is_small=True))
                ms.session_bullets += 3
            elif player.char_id == 6:
                d_spawn = get_homing_dir(pos)
                c.player_bullets.add(p_mod.PlayerBullet(pos, d_spawn, player.damage, is_rainbow_diamond=True))
                ms.session_bullets += 1

        if player.char_id == 4 and not player.brown_v_active:
            player.brown_satellites_count = 1 if player.brown_satellites_count >= 3 else player.brown_satellites_count + 1

    # Очередь из 3 выстрелов для Штурмовика (char_id == 2)
    if player.char_id == 2 and player.blue_normal_queue > 0:
        player.blue_normal_delay += 1
        if player.blue_normal_delay >= 5:
            player.blue_normal_delay, player.blue_normal_queue = 0, player.blue_normal_queue - 1
            c.player_bullets.add(p_mod.PlayerBullet(player.rect.center, pygame.math.Vector2(0, -1), player.damage))
            ms.session_bullets += 1
