"""Управление сохранениями (JSON), статистикой игрока и характеристиками персонажей."""
import json
import os
from play import constants as c

SAVE_FILE = "save_data.json"

DEFAULT_STATS = {
    "disclaimer_shown": False,
    "enemies_killed": 0,
    "bosses_killed": 0,
    "waves_cleared": 0,
    "bullets_shot": 0,
    "wins_normal": 0,
    "wins_hard": 0,
    "wins_infernum": 0,
    "wins_masochist": 0,
    "time_played": 0.0
}


def load_stats():
    """Загружает статистику из файла или возвращает значения по умолчанию."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_STATS.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    return DEFAULT_STATS.copy()


def save_stats(data):
    """Сохраняет словарь статистики в JSON."""
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


stats = load_stats()

# Счётчики текущего забега
session_enemies = 0
session_bosses = 0
session_waves = 0
session_bullets = 0

difficulty = "normal"
dev_mode = False
god_mode = False

# Конфигурация всех 6 играбельных персонажей
characters = [
    {
        "id": 1, "name": "Стандарт", "color": c.C_WHITE,
        "hp": 3, "damage": 1, "speed": 5.0,
        "shield_time": "0.6 сек", "shield_cd": "5 сек",
        "ability": "V - Двойной веер из 5 пуль, B - Ускорение движения x2.2 на 3 сек",
        "cond_desc": "Доступен изначально", "unlocked": True
    },
    {
        "id": 2, "name": "Штурмовик", "color": c.C_RED,
        "hp": 4, "damage": 2, "speed": 4.5,
        "shield_time": "0.5 сек", "shield_cd": "7 сек",
        "ability": "V - Скоростная очередь из 8 пуль, B - Гигантский разрушительный снаряд",
        "cond_desc": "Убить 50 врагов", "unlocked": False
    },
    {
        "id": 3, "name": "Защитник", "color": c.C_CYAN,
        "hp": 5, "damage": 1, "speed": 4.0,
        "shield_time": "0.8 сек", "shield_cd": "4 сек",
        "ability": "V - Тройной залп, B - Призыв 6 орбитальных энерго-щитов на 6 сек",
        "cond_desc": "Пройти 5 волн", "unlocked": False
    },
    {
        "id": 4, "name": "Призрак", "color": c.C_PURPLE,
        "hp": 3, "damage": 2, "speed": 7.0,
        "shield_time": "0.4 сек", "shield_cd": "8 сек",
        "ability": "V - Усиление спутников и скорости (B во время V - очищающая волна), B - Золотой щит",
        "cond_desc": "Победить босса на Стандартной сложности", "unlocked": False
    },
    {
        "id": 5, "name": "Спектр", "color": c.C_GREEN,
        "hp": 4, "damage": 4, "speed": 5.5,
        "shield_time": "1.0 сек", "shield_cd": "5 сек",
        "ability": "V - Фазовый рывок с неуязвимостью и ускорением, B - Шквал самонаводящихся игл",
        "cond_desc": "Выпустить 1000 пуль", "unlocked": False
    },
    {
        "id": 6, "name": "Абсолют", "color": "rainbow",
        "hp": 2, "damage": 3, "speed": 6.5,
        "shield_time": "1.3 сек", "shield_cd": "4 сек",
        "ability": "V - Веер самонаводящихся ромбов, B - Призыв 2 боевых клонов",
        "cond_desc": "Победить на сложности Сложная или Инфернум", "unlocked": False
    }
]

selected_char = next(iter(characters))


def check_unlocks():
    """Проверяет выполнение условий открытия персонажей."""
    total_enemies = stats["enemies_killed"] + session_enemies
    total_waves = stats["waves_cleared"] + session_waves
    total_bullets = stats["bullets_shot"] + session_bullets

    for ch in characters:
        if dev_mode:
            ch["unlocked"] = True
            continue
        cid = ch["id"]
        if cid == 1:
            ch["unlocked"] = True
        elif cid == 2 and total_enemies >= 50:
            ch["unlocked"] = True
        elif cid == 3 and total_waves >= 5:
            ch["unlocked"] = True
        elif cid == 4 and stats.get("wins_normal", 0) >= 1:
            ch["unlocked"] = True
        elif cid == 5 and total_bullets >= 1000:
            ch["unlocked"] = True
        elif cid == 6 and (stats.get("wins_hard", 0) >= 1 or stats.get("wins_infernum", 0) >= 1):
            ch["unlocked"] = True


def enable_dev_mode():
    global dev_mode
    dev_mode = not dev_mode
    check_unlocks()


def toggle_god_mode():
    global god_mode
    god_mode = not god_mode


def reset_all_progress():
    """Полностью сбрасывает прогресс игрока и перезаписывает файл сохранения."""
    global stats, selected_char, dev_mode, god_mode
    dev_mode = False
    god_mode = False
    stats = DEFAULT_STATS.copy()
    stats["disclaimer_shown"] = True
    for ch in characters:
        ch["unlocked"] = (ch["id"] == 1)
    selected_char = next(iter(characters))
    save_stats(stats)
