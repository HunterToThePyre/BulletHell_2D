"""Главный модуль: инициализация циклов, управление состояниями и переключение музыки."""
import pygame
import time
from objects import objects as obj
from play import menu_screens as ms, disclaimer_screen as ds, projectiles as p_mod, constants as c, game_data as gd, game_loop as gl, training_menu as tm
from play.gameplay_extras import extras
from play.music_engine import music

game_state = "disclaimer"
ds.disclaimer_frame_counter = 0
running = True
start_time = time.time()

# Состояние текущего забега (волна, таймеры, активный босс, параметры тренировки)
run_data = {
    "wave": 1, "timer": 0, "boss_spawned": False,
    "active_boss": None, "dummy": None, "dummy_timer": 0,
    "train_mode": "dummy", "train_wave": 1, "train_boss": "blue"
}


def change_state(new_state):
    global game_state
    game_state = new_state


def quit_game():
    global running
    running = False


def try_start_game():
    change_state("select_diff")


def _reset_arena():
    """Очищает все группы спрайтов на арене и спавнит выбранного игрока."""
    extras.reset()
    for g in [c.player_group, c.player_bullets, c.enemies, c.enemy_bullets, c.enemy_lasers]:
        g.empty()
    c.player_group.add(obj.Player(gd.selected_char))


def start_bot_training(wave_num):
    """Запускает тренировку с манекеном (wave_num=0) или волнами врагов (1..3)."""
    global game_state
    _reset_arena()
    game_state = "training"
    run_data.update({"wave": wave_num, "timer": 0, "active_boss": None, "dummy": None, "dummy_timer": 0})
    if wave_num == 0:
        run_data["train_mode"] = "dummy"
        run_data["dummy"] = p_mod.Dummy()
        c.enemies.add(run_data["dummy"])
    else:
        run_data["train_mode"] = "bots"
        run_data["train_wave"] = wave_num


def start_boss_training(boss_key):
    """Запускает тренировочный бой с выбранным боссом."""
    global game_state
    _reset_arena()
    game_state = "training"
    boss_cls = {"blue": p_mod.BlueCircleBoss, "purple": p_mod.PurpleCircleBoss, "red": p_mod.RedCircleBoss}[boss_key]
    boss_obj = boss_cls("normal")
    c.enemies.add(boss_obj)
    run_data.update({
        "wave": {"blue": 1, "purple": 2, "red": 3}[boss_key],
        "timer": 0, "active_boss": boss_obj, "dummy": None, "dummy_timer": 0,
        "train_mode": "boss", "train_boss": boss_key
    })


def start_game(diff_type):
    """Начинает новый основной забег на выбранной сложности."""
    global game_state
    ms.difficulty = gd.difficulty = diff_type
    game_state = "game"
    run_data.update({"wave": 1, "timer": 0, "boss_spawned": False, "active_boss": None})
    ms.session_enemies, ms.session_bosses, ms.session_waves, ms.session_bullets = 0, 0, 0, 0
    _reset_arena()


def game_over_process(win=False):
    """Сохраняет накопленную за сессию статистику и открывает экран победы/поражения."""
    global game_state
    gd.stats["enemies_killed"] += ms.session_enemies
    gd.stats["bosses_killed"] += ms.session_bosses
    gd.stats["waves_cleared"] += ms.session_waves
    gd.stats["bullets_shot"] += ms.session_bullets
    if win:
        key = f"wins_{ms.difficulty}"
        gd.stats[key] = gd.stats.get(key, 0) + 1
    gd.save_stats(gd.stats)
    game_state = "win" if win else "over"


def _sync_music():
    """Переключает фоновую музыку в зависимости от экрана и активного босса."""
    if game_state in ("game", "training"):
        boss = run_data.get("active_boss")
        if boss is not None and boss.alive():
            if isinstance(boss, p_mod.BlueCircleBoss):
                music.play_track("boss_1")
            elif isinstance(boss, p_mod.PurpleCircleBoss):
                music.play_track("boss_2")
            else:
                music.play_track("boss_3")
        else:
            music.play_track("wave")
    elif game_state != "disclaimer":
        music.play_track("menu")


# Основной цикл приложения (60 FPS)
while running:
    c.screen.fill(c.C_BLACK)
    gd.check_unlocks()
    _sync_music()
    now = time.time()
    if game_state == "game":
        gd.stats["time_played"] += now - start_time
    start_time = now

    ms.mouse_clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state = "ask_exit"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ms.mouse_clicked = True
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
            if game_state == "game":
                game_state = "pause"
            elif game_state == "pause":
                game_state = "game"

    # Маршрутизация экранов игры
    if game_state == "disclaimer":
        ds.draw_disclaimer_and_loading(change_state, ms)
    elif game_state == "menu":
        ms.draw_menu(change_state, quit_game, try_start_game)
    elif game_state == "ask_exit":
        ms.draw_ask_exit(change_state, quit_game)
    elif game_state == "select_diff":
        ms.draw_select_diff(start_game, change_state)
    elif game_state == "training_menu":
        tm.draw_training_select(start_bot_training, start_boss_training, change_state)
    elif game_state == "char":
        ms.draw_char_select(change_state)
    elif game_state == "stats":
        ms.draw_stats_screen(change_state)
    elif game_state == "training":
        gl.update_training(run_data, lambda: change_state("menu"))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_k] or keys[pygame.K_r]:
            pygame.time.delay(150)
            game_state = "training_menu"
    elif game_state == "game":
        gl.update_game(run_data, game_over_process, lambda: change_state("menu"))
    elif game_state == "pause":
        t = c.F_MAIN.render("ПАУЗА", True, c.C_CYAN)
        c.screen.blit(t, t.get_rect(center=(c.W // 2, c.H // 3)))
        ms.anim_btn("ПРОДОЛЖИТЬ [ESC]", c.W // 2 - 150, c.H // 2 - 40, 300, 48, lambda: change_state("game"))
        ms.anim_btn("НАЧАТЬ ЗАНОВО", c.W // 2 - 150, c.H // 2 + 30, 300, 48, lambda: start_game(ms.difficulty))
        ms.anim_btn("ВЫЙТИ В МЕНЮ", c.W // 2 - 150, c.H // 2 + 100, 300, 48, lambda: change_state("menu"))
    elif game_state in ["over", "win"]:
        is_win = (game_state == "win")
        msg = "ВЫ ПОБЕДИЛИ! БОСС ПОВЕРЖЕН!" if is_win else "ИГРА ОКОНЧЕНА! ВАС УБИЛИ."
        t = c.F_MAIN.render(msg, True, c.C_GREEN if is_win else c.C_RED)
        c.screen.blit(t, t.get_rect(center=(c.W // 2, c.H // 3 - 20)))
        sc = c.F_SUB.render(f"СЧЁТ ЗАБЕГА: {extras.score}", True, c.C_YELLOW)
        c.screen.blit(sc, sc.get_rect(center=(c.W // 2, c.H // 3 + 30)))

        retry_lbl = "СЫГРАТЬ СНОВА" if is_win else "ПОВТОРЯТЬ ПОПЫТКУ"
        ms.anim_btn(retry_lbl, c.W // 2 - 150, c.H // 2 - 20, 300, 45, lambda: start_game(ms.difficulty))
        ms.anim_btn("СМЕНИТЬ СЛОЖНОСТЬ", c.W // 2 - 150, c.H // 2 + 50, 300, 45, lambda: change_state("select_diff"))
        ms.anim_btn("ВЫЙТИ В МЕНЮ", c.W // 2 - 150, c.H // 2 + 120, 300, 45, lambda: change_state("menu"))

    pygame.display.flip()
    c.clock.tick(60)

pygame.quit()
