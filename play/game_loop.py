"""Обновление игрового процесса: спавн волн, призыв боссов и отрисовка арены."""
import pygame
import random
from play import menu_screens as ms, projectiles as p_mod, constants as c, tate_hud as hud
from play.vfx import vfx
from play.combat_fx import draw_entity_glows, process_combat_collisions, draw_boss_hp_bar
from play.gameplay_extras import extras

WAVE_POOLS = {
    1: ["yellow_tri", "orange_tri", "green_tri", "cyan_tri"],
    2: ["yellow_sq", "orange_sq", "green_sq", "cyan_sq"],
    3: ["yellow_hex", "orange_hex", "green_hex", "cyan_hex"],
}

WAVE_DURATIONS = {1: 1800, 2: 3600, 3: 3600}  # Длительность волн в кадрах (60 FPS)
SPAWN_INTERVAL = 110


def clear_regular_enemies():
    """Уничтожает обычных врагов перед появлением босса."""
    for e in c.enemies:
        vfx.spawn_explosion(e.rect.centerx, e.rect.centery, getattr(e, "color", c.C_CYAN), 22, 65)
    c.enemies.empty()
    c.enemy_lasers.empty()


def update_training(state, on_exit_menu=None):
    """Обновляет логику и отрисовку режима тренировки."""
    vfx.bg.update_and_draw(arena_only=True)
    state["timer"] += 1
    mode = state.get("train_mode", "dummy")

    if mode == "bots":
        pool = WAVE_POOLS.get(state.get("train_wave", 1), WAVE_POOLS)
        if state["timer"] % SPAWN_INTERVAL == 0:
            c.enemies.add(p_mod.Enemy(random.choice(pool), "normal"))
    elif mode == "boss" and state["active_boss"] is None:
        state["dummy_timer"] += 1
        if state["dummy_timer"] >= 90:
            state["dummy_timer"] = 0
            b_type = state.get("train_boss", "blue")
            boss_cls = {"blue": p_mod.BlueCircleBoss, "purple": p_mod.PurpleCircleBoss, "red": p_mod.RedCircleBoss}[b_type]
            state["active_boss"] = boss_cls("normal")
            c.enemies.add(state["active_boss"])

    c.player_group.update()
    c.player_bullets.update()
    c.enemies.update()
    c.enemy_bullets.update()
    c.enemy_lasers.update()
    extras.update()

    if mode == "dummy":
        dummy = state["dummy"]
        if dummy is not None and not dummy.alive():
            state["dummy_timer"] += 1
            if state["dummy_timer"] >= 60:
                state["dummy"] = p_mod.Dummy()
                c.enemies.add(state["dummy"])
                state["dummy_timer"] = 0
        for b in c.player_bullets:
            if state["dummy"] and state["dummy"].alive() and b.rect.colliderect(state["dummy"].rect):
                vfx.spawn_hit(b.rect.centerx, b.rect.centery, c.C_RED, 6)
                b.kill()
                state["dummy"].hp = max(0, state["dummy"].hp - b.damage)
                extras.spawn_damage_text(state["dummy"].rect.centerx, state["dummy"].rect.top, b.damage, c.C_YELLOW)
                if state["dummy"].hp == 0:
                    vfx.spawn_explosion(state["dummy"].rect.centerx, state["dummy"].rect.centery, c.C_RED, 26, 65)
                    state["dummy"].kill()
    else:
        process_combat_collisions(state, lambda win=False: None, is_training=True)

    draw_entity_glows(state["active_boss"])
    c.player_group.draw(c.screen)
    c.player_bullets.draw(c.screen)
    c.enemies.draw(c.screen)
    c.enemy_bullets.draw(c.screen)
    c.enemy_lasers.draw(c.screen)
    extras.draw()
    vfx.update_and_draw_fx()

    hud.draw_tate_panels("training", state["wave"], state["timer"], boss_active=(state["active_boss"] is not None), exit_to_menu_cb=on_exit_menu)
    draw_boss_hp_bar(state["active_boss"])


def update_game(state, on_game_over, on_exit_menu=None):
    """Обновляет основной игровой цикл: волны врагов, боссов и столкновения."""
    vfx.bg.update_and_draw(arena_only=True)
    if state["active_boss"] is None:
        state["timer"] += 1

    wave = state["wave"]
    if wave in WAVE_POOLS:
        if state["timer"] in range(WAVE_DURATIONS[wave]):
            if state["timer"] % SPAWN_INTERVAL == 0:
                c.enemies.add(p_mod.Enemy(random.choice(WAVE_POOLS[wave]), ms.difficulty))
        else:
            if wave == 1 and state["active_boss"] is None:
                clear_regular_enemies()
                state["active_boss"] = p_mod.BlueCircleBoss(ms.difficulty)
                c.enemies.add(state["active_boss"])
            elif wave == 2 and state["active_boss"] is None:
                clear_regular_enemies()
                state["active_boss"] = p_mod.PurpleCircleBoss(ms.difficulty)
                c.enemies.add(state["active_boss"])
            elif wave == 3 and state["active_boss"] is None:
                clear_regular_enemies()
                state["active_boss"] = p_mod.RedCircleBoss(ms.difficulty)
                state["boss_spawned"] = True
                c.enemies.add(state["active_boss"])

    c.player_group.update()
    c.player_bullets.update()
    c.enemies.update()
    c.enemy_bullets.update()
    c.enemy_lasers.update()
    extras.update()

    process_combat_collisions(state, on_game_over, is_training=False)

    draw_entity_glows(state["active_boss"])
    c.player_group.draw(c.screen)
    c.player_bullets.draw(c.screen)
    c.enemies.draw(c.screen)
    c.enemy_bullets.draw(c.screen)
    c.enemy_lasers.draw(c.screen)
    extras.draw()
    vfx.update_and_draw_fx()

    hud.draw_tate_panels("game", state["wave"], state["timer"], boss_active=(state["active_boss"] is not None), exit_to_menu_cb=on_exit_menu)
    draw_boss_hp_bar(state["active_boss"])
