"""Боковые панели боевого интерфейса (формат TATE): шкалы HP, перезарядка скиллов и таймер волны."""
import pygame
import math
from play import constants as c, menu_screens as ms, game_data as gd
from play.vfx import vfx, draw_glow_rect

ABILITY_MAX_CD = {
    1: (300, 900), 2: (480, 1500), 3: (300, 1200),
    4: (540, 1620), 5: (720, 900), 6: (900, 2100),
}

WAVE_SECONDS = {1: 30, 2: 60, 3: 60}


def _brighten(col, add=60):
    r, g, b = col[:3]
    return (min(255, r + add), min(255, g + add), min(255, b + add))


def wrap_text(text, font, max_w):
    words = text.split(' ')
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        w_px, _ = font.size(test)
        if w_px <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_cd_bar(x, y, w, h, label, cd_frames, max_cd_frames, ready_color):
    """Отрисовывает шкалу перезарядки способности с подсветкой при готовности."""
    ratio = 1.0 if max_cd_frames == 0 else max(0.0, min(1.0, 1.0 - (cd_frames / max_cd_frames)))
    is_ready = (cd_frames == 0)
    status = "ГОТОВО" if is_ready else f"КД: {round(cd_frames / 60, 1)}с"
    col = ready_color if is_ready else c.C_YELLOW

    c.screen.blit(c.F_SUB.render(f"{label} — {status}", True, col), (x, y))

    bar_y = y + 30
    bar_rect = pygame.Rect(x, bar_y, w, h)
    if is_ready:
        draw_glow_rect(bar_rect, ready_color, border_radius=6, glow_size=8, alpha_max=45)

    pygame.draw.rect(c.screen, (18, 22, 36), bar_rect, border_radius=6)
    fill_w = int(w * ratio)
    if fill_w > 0:
        pygame.draw.rect(c.screen, col, (x, bar_y, fill_w, h), border_radius=6)
        pygame.draw.rect(c.screen, _brighten(col, 60), (x + 2, bar_y + 2, max(1, fill_w - 4), max(2, h // 3)), border_radius=4)
    pygame.draw.rect(c.screen, col if is_ready else (90, 100, 130), bar_rect, 2, border_radius=6)


def get_location_title(game_state, current_wave, boss_active=False):
    if game_state == "training":
        return "ТРЕНИРОВОЧНЫЙ ПОЛИГОН"
    if boss_active and current_wave == 3:
        return "ФИНАЛЬНЫЙ БОСС"
    if boss_active and current_wave in (1, 2):
        return f"СТРАЖ СЕКТОРА {current_wave}"
    return {1: "СЕКТОР 1: АВАНГАРД", 2: "СЕКТОР 2: ГВАРДИЯ"}.get(current_wave, "СЕКТОР 3: ЭЛИТА")


def draw_tate_panels(game_state, current_wave, wave_timer, boss_active=False, exit_to_menu_cb=None):
    """Отрисовывает виньетку урона, рамку арены и обе боковые панели HUD."""
    vfx.draw_vignette()

    left_w = c.GAME_X
    right_x = c.PLAY_RECT.right
    right_w = c.W - right_x

    pygame.draw.rect(c.screen, (11, 14, 24), (0, 0, left_w, c.H))
    pygame.draw.rect(c.screen, (11, 14, 24), (right_x, 0, right_w, c.H))

    accent_col = c.C_RED if boss_active else c.C_CYAN
    pygame.draw.line(c.screen, accent_col, (c.PLAY_RECT.left, 0), (c.PLAY_RECT.left, c.H), 2)
    pygame.draw.line(c.screen, accent_col, (c.PLAY_RECT.right, 0), (c.PLAY_RECT.right, c.H), 2)

    pygame.draw.rect(c.screen, (28, 36, 58), (14, 14, left_w - 28, c.H - 28), 2, border_radius=12)
    pygame.draw.rect(c.screen, (28, 36, 58), (right_x + 14, 14, right_w - 28, c.H - 28), 2, border_radius=12)

    # Диагональный заголовок текущего сектора на левой панели
    loc_name = get_location_title(game_state, current_wave, boss_active)
    loc_surf = c.F_LOC.render(loc_name, True, (110, 125, 160))
    loc_rotated = pygame.transform.rotate(loc_surf, 45)
    scale = min(max(40, left_w - 44) / loc_rotated.get_width(), max(40, c.H - 190) / loc_rotated.get_height())
    loc_scaled = pygame.transform.smoothscale(loc_rotated, (max(1, int(loc_rotated.get_width() * scale)), max(1, int(loc_rotated.get_height() * scale))))
    c.screen.blit(loc_scaled, loc_scaled.get_rect(center=(left_w // 2, (c.H - 100) // 2)))

    if exit_to_menu_cb:
        btn_w = min(220, left_w - 50)
        ms.anim_btn("В МЕНЮ", (left_w - btn_w) // 2, c.H - 85, btn_w, 48, exit_to_menu_cb)

    p = c.player_group.sprite
    if not p:
        return

    px = right_x + 36
    panel_inner_w = right_w - 72
    cur_y = 36

    char_info = gd.selected_char
    c_col = char_info["color"]
    if c_col == "rainbow":
        t = pygame.time.get_ticks() * 0.005
        c_col = (int(128 + 127 * math.sin(t)), int(128 + 127 * math.sin(t + 2)), int(128 + 127 * math.sin(t + 4)))

    header_rect = pygame.Rect(px - 8, cur_y - 6, panel_inner_w + 16, 86)
    draw_glow_rect(header_rect, c_col, border_radius=10, glow_size=8, alpha_max=30)
    pygame.draw.rect(c.screen, (18, 23, 38), header_rect, border_radius=10)
    pygame.draw.rect(c.screen, c_col, header_rect, 2, border_radius=10)

    c.screen.blit(c.F_MAIN.render(char_info["name"].upper(), True, c.C_WHITE), (px + 6, cur_y))
    cur_y += 42
    c.screen.blit(c.F_SUB.render(f"Режим: {ms.difficulty.upper()}", True, c_col), (px + 6, cur_y))
    cur_y += 58

    hp_ratio = max(0.0, min(1.0, p.hp / max(1, p.max_hp)))
    hp_col = c.C_GREEN if hp_ratio == 1.0 else (c.C_YELLOW if hp_ratio >= 0.5 else c.C_RED)
    c.screen.blit(c.F_MAIN.render(f"HP: {max(0, p.hp)} / {p.max_hp}", True, hp_col), (px, cur_y))
    cur_y += 42

    hp_rect = pygame.Rect(px, cur_y, panel_inner_w, 26)
    draw_glow_rect(hp_rect, hp_col, border_radius=8, glow_size=8, alpha_max=40)
    pygame.draw.rect(c.screen, (18, 22, 36), hp_rect, border_radius=8)
    fill_hp_w = int(panel_inner_w * hp_ratio)
    if fill_hp_w > 0:
        pygame.draw.rect(c.screen, hp_col, (px, cur_y, fill_hp_w, 26), border_radius=8)
        pygame.draw.rect(c.screen, _brighten(hp_col, 65), (px + 3, cur_y + 3, max(1, fill_hp_w - 6), 7), border_radius=4)
    pygame.draw.rect(c.screen, c.C_WHITE, hp_rect, 2, border_radius=8)
    cur_y += 60

    draw_cd_bar(px, cur_y, panel_inner_w, 22, "ЩИТ [Клавиша C]", p.dash_cooldown, p.shield_max_cd, c.C_CYAN)
    cur_y += 62
    for line in wrap_text(f"Неуязвимость на {char_info['shield_time']} (перезарядка {char_info['shield_cd']})", c.F_MINI, panel_inner_w):
        c.screen.blit(c.F_MINI.render(line, True, c.C_LIGHT_GRAY), (px, cur_y))
        cur_y += 21
    cur_y += 22

    raw_ab = char_info["ability"]
    v_desc, b_part = raw_ab.split(", B - ", 1) if ", B - " in raw_ab else (raw_ab, "")
    b_desc = ("B - " + b_part) if b_part else ""
    v_max_cd, b_max_cd = ABILITY_MAX_CD.get(p.char_id, (300, 900))

    draw_cd_bar(px, cur_y, panel_inner_w, 22, "СПОСОБНОСТЬ [Клавиша V]", p.v_cooldown, v_max_cd, c.C_GREEN)
    cur_y += 62
    for line in wrap_text(v_desc, c.F_MINI, panel_inner_w):
        c.screen.blit(c.F_MINI.render(line, True, c.C_WHITE), (px, cur_y))
        cur_y += 21
    cur_y += 22

    draw_cd_bar(px, cur_y, panel_inner_w, 22, "УЛЬТИМЕЙТ [Клавиша B]", p.b_cooldown, b_max_cd, c.C_PURPLE)
    cur_y += 62
    for line in wrap_text(b_desc, c.F_MINI, panel_inner_w):
        c.screen.blit(c.F_MINI.render(line, True, c.C_WHITE), (px, cur_y))
        cur_y += 21

    bottom_y = c.H - 125
    pygame.draw.line(c.screen, (45, 55, 85), (px, bottom_y - 18), (px + panel_inner_w, bottom_y - 18), 2)
    if game_state == "training":
        c.screen.blit(c.F_SUB.render("Режим обучения (Выход: R или К)", True, c.C_YELLOW), (px, bottom_y))
    elif boss_active and current_wave in (1, 2, 3):
        titles = {1: ("БОСС: СИНИЙ КРУГ", c.C_CYAN), 2: ("БОСС: ФИОЛЕТОВЫЙ КРУГ", c.C_PURPLE), 3: ("ФИНАЛ: КРАСНЫЙ КРУГ", c.C_RED)}
        b_title, b_col = titles[current_wave]
        c.screen.blit(c.F_MAIN.render(b_title, True, b_col), (px, bottom_y))
        c.screen.blit(c.F_SUB.render("Победите босса!", True, c.C_YELLOW), (px, bottom_y + 42))
    elif current_wave in (1, 2, 3):
        tl = max(0, WAVE_SECONDS.get(current_wave, 60) - (wave_timer // 60))
        wave_labels = {1: "Обычные враги", 2: "Редкие враги", 3: "Эпические враги"}
        c.screen.blit(c.F_MAIN.render(f"ВОЛНА {current_wave} / 3 ({tl} сек.)", True, c.C_WHITE), (px, bottom_y))
        c.screen.blit(c.F_SUB.render(f"Состав: {wave_labels[current_wave]}", True, c.C_YELLOW), (px, bottom_y + 42))
