"""Главное меню, универсальные анимированные кнопки и экран подтверждения выхода."""
import pygame
import random
import math
from play import constants as c
from play import game_data as gd
from play import menu_scene as mscene
from play import menu_subscreens as msub
from play.vfx import vfx, draw_glow_rect
from play.game_data import (
    stats, session_enemies, session_bosses, session_waves, session_bullets,
    characters, selected_char, difficulty, load_stats, save_stats, check_unlocks
)

mouse_clicked = False
_exit_btn_x = None
_exit_btn_y = None


def anim_btn(txt, x, y, base_w, base_h, act=None, active_color=None, shake=False):
    """Рисует интерактивную кнопку с неоновым свечением и увеличением при наведении."""
    mx, my = pygame.mouse.get_pos()
    is_hover = (x <= mx <= x + base_w) and (y <= my <= y + base_h)
    if is_hover:
        w, h = int(base_w * 1.15), int(base_h * 1.15)
        sx = random.randint(-4, 4) if shake else 0
        sy = random.randint(-4, 4) if shake else 0
        cx, cy = x - (w - base_w) // 2 + sx, y - (h - base_h) // 2 + sy
        btn_rect = pygame.Rect(cx, cy, w, h)
        draw_glow_rect(btn_rect, c.C_RED, border_radius=8, glow_size=12, alpha_max=70)
        pygame.draw.rect(c.screen, (180, 24, 36), btn_rect, border_radius=8)
        pygame.draw.rect(c.screen, c.C_WHITE, btn_rect, 2, border_radius=8)
        ts = c.F_SUB.render(txt, True, c.C_WHITE)
        c.screen.blit(ts, ts.get_rect(center=(cx + w // 2, cy + h // 2)))
        if mouse_clicked and act:
            act()
    else:
        btn_rect = pygame.Rect(x, y, base_w, base_h)
        bg_col = active_color if active_color else (22, 27, 44)
        border_col = active_color if active_color else (65, 80, 120)
        txt_col = c.C_BLACK if active_color else c.C_LIGHT_GRAY
        if active_color:
            draw_glow_rect(btn_rect, active_color, border_radius=8, glow_size=8, alpha_max=45)
        pygame.draw.rect(c.screen, bg_col, btn_rect, border_radius=8)
        pygame.draw.rect(c.screen, border_col, btn_rect, 2, border_radius=8)
        ts = c.F_SUB.render(txt, True, txt_col)
        c.screen.blit(ts, ts.get_rect(center=(x + base_w // 2, y + base_h // 2)))


def _draw_char_icon_left_of_btn(btn_left_x, btn_center_y):
    """Отображает модельку выбранного персонажа слева от подсвеченной кнопки меню."""
    col = gd.selected_char["color"]
    if col == "rainbow":
        t = pygame.time.get_ticks() * 0.005
        col = (int(128 + 127 * math.sin(t)), int(128 + 127 * math.sin(t + 2)), int(128 + 127 * math.sin(t + 4)))
    mscene.draw_neon_player_model(int(btn_left_x - 32), int(btn_center_y), col, 18)


def _menu_btn_15x(txt, center_x, center_y, base_w, base_h, act=None, is_exit=False):
    """Кнопка правой панели главного меню с увеличением в 1.5 раза при наведении."""
    mx, my = pygame.mouse.get_pos()
    bx = center_x - base_w // 2
    by = center_y - base_h // 2
    is_hover = (bx <= mx <= bx + base_w) and (by <= my <= by + base_h)

    if is_hover:
        w, h = int(base_w * 1.5), int(base_h * 1.5)
        shake_x = random.randint(-4, 4) if is_exit else 0
        shake_y = random.randint(-4, 4) if is_exit else 0
        draw_cx, draw_cy = center_x + shake_x, center_y + shake_y
        rx, ry = draw_cx - w // 2, draw_cy - h // 2
        btn_rect = pygame.Rect(rx, ry, w, h)

        bg_col = (170, 20, 20) if is_exit else (34, 40, 62)
        txt_col = c.C_WHITE if is_exit else c.C_RED

        draw_glow_rect(btn_rect, c.C_RED, border_radius=10, glow_size=14, alpha_max=75)
        pygame.draw.rect(c.screen, bg_col, btn_rect, border_radius=10)
        pygame.draw.rect(c.screen, c.C_RED, btn_rect, 3 if is_exit else 2, border_radius=10)
        f_big = pygame.font.SysFont("Arial", 28, bold=True)
        ts = f_big.render(txt, True, txt_col)
        c.screen.blit(ts, ts.get_rect(center=(draw_cx, draw_cy)))
        _draw_char_icon_left_of_btn(rx, draw_cy)
        if mouse_clicked and act:
            act()
    else:
        btn_rect = pygame.Rect(bx, by, base_w, base_h)
        pygame.draw.rect(c.screen, (20, 24, 38), btn_rect, border_radius=10)
        pygame.draw.rect(c.screen, (60, 72, 105), btn_rect, 2, border_radius=10)
        ts = c.F_SUB.render(txt, True, c.C_LIGHT_GRAY)
        c.screen.blit(ts, ts.get_rect(center=(center_x, center_y)))


def draw_menu(change_state_cb, quit_cb, start_game_cb):
    """Отрисовывает главное меню с демонстрационной ареной слева и кнопками справа."""
    global _exit_btn_x, _exit_btn_y
    _exit_btn_x = None
    _exit_btn_y = None
    mscene.demo_arena.update_and_draw(mouse_clicked)

    split_x = mscene.SPLIT_X
    right_w = c.W - split_x
    pygame.draw.rect(c.screen, (11, 14, 24), (split_x + 4, 0, right_w - 4, c.H))
    pygame.draw.rect(c.screen, (32, 42, 68), (split_x + 16, 16, right_w - 32, c.H - 32), 2, border_radius=12)

    panel_cx = split_x + right_w // 2
    start_y = c.H // 2 - 165
    step_y = 110

    _menu_btn_15x("НАЧАТЬ ИГРУ", panel_cx, start_y, 260, 52, start_game_cb)
    _menu_btn_15x("ВЫБОР ПЕРСОНАЖА", panel_cx, start_y + step_y, 260, 52, lambda: change_state_cb("char"))
    _menu_btn_15x("СТАТИСТИКА", panel_cx, start_y + step_y * 2, 260, 52, lambda: change_state_cb("stats"))
    _menu_btn_15x("ВЫХОД", panel_cx, start_y + step_y * 3, 260, 52, lambda: change_state_cb("ask_exit"), is_exit=True)


def draw_ask_exit(change_state_cb, quit_cb):
    """Экран подтверждения выхода с убегающей от курсора кнопкой «ДА»."""
    global _exit_btn_x, _exit_btn_y
    vfx.bg.update_and_draw(arena_only=False)
    t = c.F_MAIN.render("ТОЧНО ХОТИТЕ ВЫЙТИ?", True, c.C_WHITE)
    c.screen.blit(t, t.get_rect(center=(c.W // 2, c.H // 3)))

    btn_w, btn_h = 180, 60
    if _exit_btn_x is None or _exit_btn_y is None:
        _exit_btn_x = float(c.W // 2 - 240)
        _exit_btn_y = float(c.H // 2)

    mx, my = pygame.mouse.get_pos()
    dx = (_exit_btn_x + btn_w / 2.0) - mx
    dy = (_exit_btn_y + btn_h / 2.0) - my
    dist = math.hypot(dx, dy)

    if int(dist) in range(170):
        if dist == 0:
            dx, dy, dist = -1.0, 0.0, 1.0
        _exit_btn_x = max(50.0, min(float(c.W - btn_w - 50), _exit_btn_x + (dx / dist) * 7.0))
        _exit_btn_y = max(120.0, min(float(c.H - btn_h - 50), _exit_btn_y + (dy / dist) * 7.0))

    anim_btn("ДА (Выйти)", int(_exit_btn_x), int(_exit_btn_y), btn_w, btn_h, quit_cb, shake=True)
    anim_btn("НЕТ (Вернуться)", c.W // 2 + 60, c.H // 2, 180, 60, lambda: change_state_cb("menu"))


def draw_select_diff(start_game_cb, change_state_cb):
    msub.render_select_diff(start_game_cb, change_state_cb, anim_btn, mouse_clicked)


def draw_char_select(change_state_cb):
    global selected_char
    msub.render_char_select(change_state_cb, anim_btn, mouse_clicked)
    selected_char = gd.selected_char


def draw_stats_screen(change_state_cb):
    msub.render_stats_screen(change_state_cb, anim_btn, session_enemies, session_bosses, session_waves, session_bullets)
