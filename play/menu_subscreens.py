"""Подэкраны меню: выбор сложности, сетка персонажей и статистика с настройками."""
import pygame
import math
from play import constants as c
from play import game_data as gd
from play import menu_scene as mscene
from play.vfx import vfx, draw_glow_rect
from play.sfx import sfx

_reset_confirm_timer = 0


def _wrap_lines(text, font, max_w):
    """Разбивает длинную строку на список строк под заданную ширину в пикселях."""
    words = text.split(" ")
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


def render_select_diff(start_game_cb, change_state_cb, anim_btn_fn, is_clicked):
    """Экран выбора сложности с последовательной разблокировкой за победы."""
    vfx.bg.update_and_draw(arena_only=False)
    t = c.F_MAIN.render("ВЫБЕРИТЕ СЛОЖНОСТЬ", True, c.C_WHITE)
    c.screen.blit(t, t.get_rect(center=(c.W // 2, c.H // 7)))

    if gd.dev_mode:
        dev_t = c.F_SUB.render("[РЕЖИМ РАЗРАБОТЧИКА: ВСЕ СЛОЖНОСТИ ОТКРЫТЫ]", True, c.C_GREEN)
        c.screen.blit(dev_t, dev_t.get_rect(center=(c.W // 2, c.H // 7 + 42)))

    diffs = [
        ("normal", "Стандартный", True, ""),
        ("hard", "Сложная", gd.stats.get("wins_normal", 0) != 0, "Пройдите Стандартный"),
        ("infernum", "Инфернум", gd.stats.get("wins_hard", 0) != 0, "Пройдите Сложный"),
        ("masochist", "Мазохист", gd.stats.get("wins_infernum", 0) != 0, "Пройдите Инфернум"),
    ]

    mx, my = pygame.mouse.get_pos()
    btn_w, btn_h = 380, 52
    cx = c.W // 2 - btn_w // 2
    start_y = c.H // 2 - 195

    for idx, (diff_id, label, unlocked, req_txt) in enumerate(diffs):
        by = start_y + idx * 74
        if unlocked or gd.dev_mode:
            anim_btn_fn(label, cx, by, btn_w, btn_h, lambda d=diff_id: start_game_cb(d))
        else:
            lock_rect = pygame.Rect(cx, by, btn_w, btn_h)
            is_hov = lock_rect.collidepoint(mx, my)
            pygame.draw.rect(c.screen, (16, 16, 24), lock_rect, border_radius=8)
            pygame.draw.rect(c.screen, c.C_RED if is_hov else (80, 35, 45), lock_rect, 2, border_radius=8)
            lock_lbl = c.F_SUB.render(f"{label} — [{req_txt}]", True, (150, 95, 105))
            c.screen.blit(lock_lbl, lock_lbl.get_rect(center=lock_rect.center))
            if is_hov and is_clicked:
                sfx.play("player_hit")

    anim_btn_fn("Обучение / Тренировка", cx, start_y + 315, btn_w, 54, lambda: change_state_cb("training_menu"), c.C_YELLOW)
    anim_btn_fn("Назад", c.W // 2 - 100, start_y + 395, 200, 45, lambda: change_state_cb("menu"))


def render_char_select(change_state_cb, anim_btn_fn, is_clicked):
    """Сетка выбора из 6 персонажей с карточкой подробных характеристик."""
    vfx.bg.update_and_draw(arena_only=False)
    t = c.F_MAIN.render("ВЫБОР ПЕРСОНАЖА", True, c.C_WHITE)
    c.screen.blit(t, t.get_rect(center=(c.W // 2, 45)))
    mx, my = pygame.mouse.get_pos()
    hovered_char = None

    for i, ch in enumerate(gd.characters):
        row, col = i // 3, i % 3
        bx, by = c.W // 2 - 360 + col * 240, 95 + row * 140
        card_rect = pygame.Rect(bx, by, 180, 115)
        is_sel = (gd.selected_char["id"] == ch["id"])

        if ch["unlocked"]:
            p_color = (int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.005)), 150, 200) if ch["color"] == "rainbow" else ch["color"]
            border_c = c.C_GREEN if is_sel else (75, 90, 130)
            if is_sel:
                draw_glow_rect(card_rect, c.C_GREEN, border_radius=10, glow_size=12, alpha_max=60)
        else:
            p_color, border_c = (40, 40, 50), c.C_RED

        pygame.draw.rect(c.screen, (18, 22, 36), card_rect, border_radius=10)
        pygame.draw.rect(c.screen, border_c, card_rect, 3 if is_sel else 2, border_radius=10)
        mscene.draw_neon_player_model(bx + 90, by + 48, p_color, 24)
        name_t = c.F_MINI.render(ch["name"] if ch["unlocked"] else "[ЗАБЛОКИРОВАН]", True, c.C_WHITE)
        c.screen.blit(name_t, name_t.get_rect(center=(bx + 90, by + 96)))

        if bx <= mx <= bx + 180 and by <= my <= by + 115:
            hovered_char = ch
            if is_clicked and ch["unlocked"]:
                gd.selected_char = ch

    if hovered_char:
        box_w = min(1150, c.W - 120)
        raw_lines = [
            f"Имя: {hovered_char['name']}",
            f"HP: {hovered_char['hp']}  |  Урон: {hovered_char['damage']}  |  Скорость: {hovered_char['speed']}",
            f"Щит: {hovered_char['shield_time']} (Перезарядка: {hovered_char['shield_cd']})",
            f"Способности: {hovered_char['ability']}",
            f"Условие открытия: {hovered_char['cond_desc']}"
        ]
        wrapped = []
        for raw in raw_lines:
            wrapped.extend(_wrap_lines(raw, c.F_SUB, box_w - 48))

        line_h = 34
        box_h = max(210, len(wrapped) * line_h + 32)
        box_rect = pygame.Rect(c.W // 2 - box_w // 2, c.H - box_h - 68, box_w, box_h)

        draw_glow_rect(box_rect, c.C_CYAN, border_radius=12, glow_size=12, alpha_max=45)
        pygame.draw.rect(c.screen, (16, 20, 34), box_rect, border_radius=12)
        pygame.draw.rect(c.screen, c.C_CYAN, box_rect, 2, border_radius=12)

        for idx, text_l in enumerate(wrapped):
            c.screen.blit(c.F_SUB.render(text_l, True, c.C_WHITE), (box_rect.x + 24, box_rect.y + 16 + idx * line_h))

    anim_btn_fn("Назад в меню", c.W // 2 - 110, c.H - 52, 220, 38, lambda: change_state_cb("menu"))


def _handle_reset_click():
    """Двухэтапное подтверждение сброса сохранения."""
    global _reset_confirm_timer
    if _reset_confirm_timer == 0:
        _reset_confirm_timer = 180
        sfx.play("hit")
    else:
        _reset_confirm_timer = 0
        gd.reset_all_progress()
        sfx.play("boss_kill")


def render_stats_screen(change_state_cb, anim_btn_fn, sess_e, sess_b, sess_w, sess_bul):
    """Экран статистики, регулировки громкости звука, читов и сброса прогресса."""
    global _reset_confirm_timer
    if _reset_confirm_timer:
        _reset_confirm_timer -= 1

    vfx.bg.update_and_draw(arena_only=False)
    t = c.F_MAIN.render("СТАТИСТИКА И НАСТРОЙКИ", True, c.C_WHITE)
    c.screen.blit(t, t.get_rect(center=(c.W // 2, 50)))

    panel_rect = pygame.Rect(c.W // 2 - 260, 88, 520, 420)
    draw_glow_rect(panel_rect, c.C_BLUE, border_radius=12, glow_size=12, alpha_max=40)
    pygame.draw.rect(c.screen, (16, 20, 34), panel_rect, border_radius=12)
    pygame.draw.rect(c.screen, (65, 85, 135), panel_rect, 2, border_radius=12)

    opened_count = sum(1 for ch in gd.characters if ch["unlocked"])
    stat_lines = [
        f"Убито врагов: {gd.stats['enemies_killed'] + sess_e}",
        f"Убито боссов: {gd.stats['bosses_killed'] + sess_b}",
        f"Пройдено волн: {gd.stats['waves_cleared'] + sess_w}",
        f"Выпущено пуль: {gd.stats['bullets_shot'] + sess_bul}",
        f"Открыто персонажей: {opened_count} из 6",
        f"Побед на Стандартном: {gd.stats['wins_normal']}",
        f"Побед на Сложном: {gd.stats['wins_hard']}",
        f"Побед на Инфернуме: {gd.stats.get('wins_infernum', 0)}",
        f"Побед на Мазохисте: {gd.stats.get('wins_masochist', 0)}",
        f"Время в игре: {int(gd.stats['time_played'])} сек."
    ]
    for idx, s_txt in enumerate(stat_lines):
        c.screen.blit(c.F_SUB.render(s_txt, True, c.C_WHITE), (c.W // 2 - 210, 102 + idx * 39))

    vol_y = c.H - 235
    vol_pct = int(sfx.volume * 100)
    vol_txt = c.F_SUB.render(f"Громкость: {vol_pct}%", True, c.C_YELLOW)
    c.screen.blit(vol_txt, vol_txt.get_rect(center=(c.W // 2, vol_y + 22)))
    anim_btn_fn("- 10%", c.W // 2 - 260, vol_y, 110, 44, lambda: sfx.change_volume(-0.1))
    anim_btn_fn("+ 10%", c.W // 2 + 150, vol_y, 110, 44, lambda: sfx.change_volume(0.1))

    btn_y = c.H - 170
    dev_txt = "Режим разработчика: ВКЛ" if gd.dev_mode else "Режим разработчика: ВЫКЛ"
    god_txt = "Бессмертие: ВКЛ" if gd.god_mode else "Бессмертие: ВЫКЛ"
    anim_btn_fn(dev_txt, c.W // 2 - 340, btn_y, 320, 46, gd.enable_dev_mode, c.C_GREEN if gd.dev_mode else None)
    anim_btn_fn(god_txt, c.W // 2 + 20, btn_y, 320, 46, gd.toggle_god_mode, c.C_CYAN if gd.god_mode else None)

    reset_lbl = "ТОЧНО СБРОСИТЬ?" if _reset_confirm_timer else "СБРОС СОХРАНЕНИЯ"
    reset_col = c.C_RED if _reset_confirm_timer else (220, 70, 80)
    anim_btn_fn(reset_lbl, c.W // 2 - 340, c.H - 95, 290, 46, _handle_reset_click, reset_col, shake=bool(_reset_confirm_timer))
    anim_btn_fn("Назад", c.W // 2 + 50, c.H - 95, 290, 46, lambda: change_state_cb("menu"))
