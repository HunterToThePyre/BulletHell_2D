"""Обработка боевых столкновений, урона, смерти врагов/боссов и неонового свечения."""
import pygame
import math
from play import menu_screens as ms, projectiles as p_mod, constants as c, game_data as gd
from play.vfx import vfx, draw_additive_glow
from play.sfx import sfx
from play.gameplay_extras import extras


def apply_player_hit(dmg, on_game_over, is_training=False):
    """Наносит урон игроку с учётом неуязвимости, щитов, режима бога и сложности."""
    p = c.player_group.sprite
    if not p or p.invulnerable or gd.god_mode or dmg in (0, None):
        return
    if p.char_id == 4 and getattr(p, "yellow_shield_active", False):
        return

    # На сложности Мазохист любое попадание мгновенно убивает игрока
    if not is_training and ms.difficulty == "masochist":
        p.hp = 0
    else:
        p.hp = max(0, p.hp - dmg)

    extras.combo = 1
    sfx.play("player_hit")
    vfx.trigger_damage_vignette(225)
    if p.hp == 0:
        vfx.spawn_player_death(p.rect.centerx, p.rect.centery)
        if is_training:
            p.hp = p.max_hp
            p.invulnerable = True
            p.invuln_timer = 90
        else:
            on_game_over(win=False)
    else:
        vfx.spawn_explosion(p.rect.centerx, p.rect.centery, c.C_RED, 22, 70)
        p.invulnerable = True
        p.invuln_timer = max(p.invuln_timer, 60)


def handle_enemy_kill(e, state, on_game_over):
    """Обрабатывает гибель врага или босса: начисляет счёт, спавнит взрыв и двигает волну."""
    col = getattr(e, "color", c.C_RED)
    if isinstance(e, (p_mod.Boss, p_mod.RedCircleBoss)):
        sfx.play("boss_kill")
        extras.add_kill_score(e.rect.centerx, e.rect.centery, 2500)
        vfx.spawn_boss_death(e.rect.centerx, e.rect.centery, c.C_RED, c.C_ORANGE)
        ms.session_bosses += 1
        ms.session_waves += 1
        on_game_over(win=True)
    elif isinstance(e, (p_mod.BlueCircleBoss, p_mod.PurpleCircleBoss)):
        sfx.play("boss_kill")
        extras.add_kill_score(e.rect.centerx, e.rect.centery, 1200)
        is_purp = isinstance(e, p_mod.PurpleCircleBoss)
        b_main = c.C_PURPLE if is_purp else c.C_BLUE
        b_sec = c.C_PINK if is_purp else c.C_CYAN
        vfx.spawn_boss_death(e.rect.centerx, e.rect.centery, b_main, b_sec)
        ms.session_bosses += 1
        ms.session_waves += 1
        state["active_boss"] = None
        state["wave"] += 1
        state["timer"] = 0
    else:
        sfx.play("kill")
        extras.add_kill_score(e.rect.centerx, e.rect.centery, 100)
        vfx.spawn_explosion(e.rect.centerx, e.rect.centery, col, 28, 70)
        ms.session_enemies += 1
    e.kill()


def draw_entity_glows(boss):
    """Отрисовывает точку хитбокса игрока, контур щита и аддитивное свечение пуль и босса."""
    p = c.player_group.sprite
    bullet_glow_col = c.C_CYAN
    if p:
        cx, cy = p.rect.center
        if p.color_type == "rainbow":
            t = pygame.time.get_ticks() * 0.005
            bullet_glow_col = (
                int(128 + 127 * math.sin(t)),
                int(128 + 127 * math.sin(t + 2)),
                int(128 + 127 * math.sin(t + 4))
            )
        else:
            bullet_glow_col = p.color_type

        pygame.draw.circle(c.screen, (255, 255, 255), (cx, cy), 4)
        if p.invulnerable or gd.god_mode:
            pulse = int(26 + 3 * math.sin(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(c.screen, bullet_glow_col, (cx, cy), pulse, 2)

    for b in c.player_bullets:
        if b.__class__.__name__ != "PlayerClone":
            draw_additive_glow(b.rect.centerx, b.rect.centery, 14, bullet_glow_col, intensity=65)

    if boss is not None and boss.alive() and not getattr(boss, "hidden", False):
        if isinstance(boss, p_mod.BlueCircleBoss):
            b_col = c.C_BLUE
        elif isinstance(boss, p_mod.PurpleCircleBoss):
            b_col = c.C_PURPLE
        else:
            b_col = c.C_RED
        pulse_r = int(115 + 12 * math.sin(pygame.time.get_ticks() * 0.008))
        draw_additive_glow(boss.rect.centerx, boss.rect.centery, pulse_r, b_col, intensity=95)


def process_combat_collisions(state, on_game_over, is_training=False):
    """Проверяет все попадания пуль, орбит и лазеров, а также особые зоны Красного босса."""
    boss = state["active_boss"]
    p = c.player_group.sprite
    if p and isinstance(boss, p_mod.RedCircleBoss):
        if boss.trap_rect is not None:
            p.rect.clamp_ip(boss.trap_rect)
        if boss.gravity_pull:
            p.rect.y -= 2
            p.rect.clamp_ip(c.PLAY_RECT)

    # Попадания пуль игрока по врагам
    for b in list(c.player_bullets):
        if b.__class__.__name__ == "PlayerClone" or getattr(b, "is_clearing_wave", False):
            continue
        for e in pygame.sprite.spritecollide(b, c.enemies, False):
            if isinstance(e, p_mod.Dummy) or getattr(e, "hidden", False):
                continue
            sfx.play("hit")
            vfx.spawn_hit(b.rect.centerx, b.rect.centery, getattr(e, "color", c.C_WHITE), 7)
            if not getattr(b, "is_big_destroyer", False):
                b.kill()
            if not getattr(e, "invulnerable", False):
                e.hp = max(0, e.hp - b.damage)
                extras.spawn_damage_text(e.rect.centerx, e.rect.top, b.damage, c.C_YELLOW)
                if e.hp == 0:
                    if is_training:
                        sfx.play("boss_kill")
                        vfx.spawn_explosion(e.rect.centerx, e.rect.centery, getattr(e, "color", c.C_CYAN), 28, 70)
                        state["active_boss"] = None
                        e.kill()
                    else:
                        handle_enemy_kill(e, state, on_game_over)
            break

    # Урон от орбитальных щитов Защитника (char_id == 3)
    if p and p.char_id == 3:
        for orb in list(p.orbit_shields):
            for e in pygame.sprite.spritecollide(orb, c.enemies, False):
                if isinstance(e, p_mod.Dummy) or getattr(e, "hidden", False):
                    continue
                sfx.play("hit")
                vfx.spawn_hit(orb.rect.centerx, orb.rect.centery, c.C_CYAN, 9)
                orb.kill()
                if not getattr(e, "invulnerable", False):
                    e.hp = max(0, e.hp - orb.damage)
                    extras.spawn_damage_text(e.rect.centerx, e.rect.top, orb.damage, c.C_CYAN)
                    if e.hp == 0:
                        if is_training:
                            state["active_boss"] = None
                            e.kill()
                        else:
                            handle_enemy_kill(e, state, on_game_over)
                break

    # Попадания вражеских пуль и лазеров по игроку
    if p:
        for bullet in pygame.sprite.spritecollide(p, c.enemy_bullets, True, pygame.sprite.collide_circle):
            apply_player_hit(bullet.damage, on_game_over, is_training)

    if p and not p.invulnerable and not gd.god_mode:
        for hazard in c.enemy_lasers:
            if getattr(hazard, "is_firing", False) and p.rect.clipline(hazard.start_pos, hazard.end_pos):
                apply_player_hit(hazard.damage, on_game_over, is_training)
                break
            if getattr(hazard, "player_hit", False):
                apply_player_hit(hazard.damage, on_game_over, is_training)
                break


def draw_boss_hp_bar(boss):
    """Рисует полосу здоровья активного босса в верхней части арены."""
    if boss is not None and boss.alive() and not getattr(boss, "hidden", False):
        bar_w = c.GAME_W - 80
        bar_x = c.PLAY_RECT.left + 40
        if isinstance(boss, p_mod.BlueCircleBoss):
            bar_col = c.C_BLUE
        elif isinstance(boss, p_mod.PurpleCircleBoss):
            bar_col = c.C_PURPLE
        else:
            bar_col = c.C_RED

        bg_rect = pygame.Rect(bar_x, 20, bar_w, 18)
        pygame.draw.rect(c.screen, (20, 22, 34), bg_rect, border_radius=6)
        ratio = max(0.0, min(1.0, boss.hp / max(1, boss.max_hp)))
        fill_w = int(bar_w * ratio)
        if fill_w:
            pygame.draw.rect(c.screen, bar_col, pygame.Rect(bar_x, 20, fill_w, 18), border_radius=6)
        pygame.draw.rect(c.screen, c.C_WHITE, bg_rect, 2, border_radius=6)
