"""Экран выбора режима тренировки: манекен, волны врагов или спарринг с боссами."""
import pygame
from play import constants as c
from play import menu_screens as ms
from play.vfx import vfx, draw_glow_rect


def draw_training_select(start_bot_cb, start_boss_cb, change_state_cb):
    """Отрисовывает две колонки выбора тренировочного режима и кнопку возврата."""
    vfx.bg.update_and_draw(arena_only=False)

    title = c.F_MAIN.render("ОБУЧЕНИЕ И ТРЕНИРОВКА", True, c.C_WHITE)
    c.screen.blit(title, title.get_rect(center=(c.W // 2, 65)))

    col_w = 320
    left_x = c.W // 2 - col_w - 45
    right_x = c.W // 2 + 45
    header_y = 135
    start_y = 190
    step_y = 74

    # Неоновые подложки для разделения категорий
    left_panel = pygame.Rect(left_x - 20, header_y - 15, col_w + 40, 345)
    right_panel = pygame.Rect(right_x - 20, header_y - 15, col_w + 40, 275)
    draw_glow_rect(left_panel, c.C_CYAN, border_radius=12, glow_size=10, alpha_max=30)
    draw_glow_rect(right_panel, c.C_PURPLE, border_radius=12, glow_size=10, alpha_max=30)
    pygame.draw.rect(c.screen, (16, 20, 34), left_panel, border_radius=12)
    pygame.draw.rect(c.screen, (60, 80, 125), left_panel, 2, border_radius=12)
    pygame.draw.rect(c.screen, (16, 20, 34), right_panel, border_radius=12)
    pygame.draw.rect(c.screen, (95, 65, 130), right_panel, 2, border_radius=12)

    sub_l = c.F_SUB.render("МАНИКЕН И ВОЛНЫ", True, c.C_CYAN)
    c.screen.blit(sub_l, sub_l.get_rect(center=(left_x + col_w // 2, header_y + 12)))

    ms.anim_btn("Манекен (Тест урона)", left_x, start_y, col_w, 50, lambda: start_bot_cb(0))
    ms.anim_btn("Волна 1 (Треугольники)", left_x, start_y + step_y, col_w, 50, lambda: start_bot_cb(1))
    ms.anim_btn("Волна 2 (Квадраты)", left_x, start_y + step_y * 2, col_w, 50, lambda: start_bot_cb(2))
    ms.anim_btn("Волна 3 (Шестиугольники)", left_x, start_y + step_y * 3, col_w, 50, lambda: start_bot_cb(3))

    sub_r = c.F_SUB.render("ТРЕНИРОВКА С БОССАМИ", True, c.C_PURPLE)
    c.screen.blit(sub_r, sub_r.get_rect(center=(right_x + col_w // 2, header_y + 12)))

    ms.anim_btn("Босс 1: Синий круг", right_x, start_y, col_w, 50, lambda: start_boss_cb("blue"))
    ms.anim_btn("Босс 2: Фиолетовый круг", right_x, start_y + step_y, col_w, 50, lambda: start_boss_cb("purple"))
    ms.anim_btn("Босс 3: Красный круг", right_x, start_y + step_y * 2, col_w, 50, lambda: start_boss_cb("red"))

    hint = c.F_SUB.render("В режиме тренировки игрок бессмертен. Выход: клавиша R, К или кнопка «В МЕНЮ»", True, c.C_YELLOW)
    c.screen.blit(hint, hint.get_rect(center=(c.W // 2, c.H - 135)))

    ms.anim_btn("Назад", c.W // 2 - 110, c.H - 85, 220, 48, lambda: change_state_cb("select_diff"))
