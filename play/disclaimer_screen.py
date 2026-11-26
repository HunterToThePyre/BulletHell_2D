"""Стартовый экран с предупреждением (дисклеймером) и анимацией загрузки."""
import pygame
import math
import random
from play import constants as c

disclaimer_frame_counter = 0
loading_angle = 0


def draw_disclaimer_and_loading(on_finish_cb, ms_module):
    """Показывает дисклеймер (5 сек), затем вращающийся индикатор загрузки (3 сек)."""
    global disclaimer_frame_counter, loading_angle
    disclaimer_frame_counter += 1

    # 1 этап: предупреждение о вспышках (кадры 1..300)
    if disclaimer_frame_counter <= 300:
        shake_x = random.randint(-2, 2)
        shake_y = random.randint(-2, 2)

        title_surf = c.F_MAIN.render("ДИСКЛЕЙМЕР", True, c.C_RED)
        c.screen.blit(title_surf, title_surf.get_rect(center=(c.W // 2 + shake_x, c.H // 4 - 80 + shake_y)))

        lines_white = [
            "У небольшой части людей могут возникать эпилептические припадки или потеря сознания при",
            "воздействии определенных визуальных эффектов, включая вспышки света или мелькающие",
            "узоры, которые могут появиться в видеоиграх. Даже у людей, не имевших ранее в анамнезе",
            "приступов или эпилепсии, может быть недиагностированное состояние, способное вызывать",
            "подобные припадки. Если вы или кто-либо из ваших близких страдаете эпилепсией,",
            "проконсультируйтесь с врачом перед началом игры."
        ]
        lines_red = [
            "Если во время игры вы испытываете головокружение, помутнение зрения, подергивание глаз",
            "или мышц, потеря сознания, дезориентацию или непроизвольные движения, немедленно",
            "прекратите игру и обратитесь за медицинской помощью."
        ]
        line_gray = "(Зачем я это написал хз, все равно не кто не прочитает.)"

        for idx, line in enumerate(lines_white):
            surf = c.F_SUB.render(line, True, c.C_WHITE)
            c.screen.blit(surf, surf.get_rect(center=(c.W // 2, c.H // 4 + idx * 32)))

        for idx, line in enumerate(lines_red):
            surf = c.F_SUB.render(line, True, c.C_RED)
            c.screen.blit(surf, surf.get_rect(center=(c.W // 2, c.H // 4 + 220 + idx * 32)))

        surf_gray = c.F_MINI.render(line_gray, True, c.C_GRAY)
        c.screen.blit(surf_gray, surf_gray.get_rect(center=(c.W // 2, c.H // 4 + 330)))

    # 2 этап: орбитальная анимация загрузки (кадры 301..480)
    elif 300 < disclaimer_frame_counter <= 480:
        loading_angle += 0.06
        center_x, center_y = c.W // 2, c.H // 2
        for i in range(6):
            angle = loading_angle + (i * (math.pi / 3))
            kx = center_x + int(math.cos(angle) * 60)
            ky = center_y + int(math.sin(angle) * 60)
            pygame.draw.circle(c.screen, c.C_BLUE, (kx, ky), 10)

        load_t = c.F_SUB.render("Загрузка...", True, c.C_LIGHT_GRAY)
        c.screen.blit(load_t, load_t.get_rect(center=(c.W // 2, c.H // 2 + 120)))

    if disclaimer_frame_counter >= 480:
        ms_module.stats["disclaimer_shown"] = True
        ms_module.save_stats(ms_module.stats)
        on_finish_cb("menu")
