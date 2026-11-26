"""Глобальные настройки окна, палитра цветов, шрифты и группы спрайтов."""
import pygame

pygame.init()

# Инициализация полноэкранного режима и иконки окна
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
pygame.display.set_caption("Пулевой ад: ФОРМАция")
clock = pygame.time.Clock()

_win_icon = pygame.Surface((64, 64), pygame.SRCALPHA)
pygame.draw.rect(_win_icon, (8, 12, 24), (0, 0, 64, 64), border_radius=14)
pygame.draw.circle(_win_icon, (255, 50, 50, 80), (32, 32), 26)
pygame.draw.circle(_win_icon, (14, 14, 24), (32, 32), 20)
pygame.draw.circle(_win_icon, (255, 50, 50), (32, 32), 20, 3)
pygame.draw.circle(_win_icon, (255, 140, 0), (32, 32), 13, 2)
pygame.draw.circle(_win_icon, (255, 255, 255), (32, 32), 5)
pygame.display.set_icon(_win_icon)

# Палитра неоновых цветов
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_GRAY = (70, 75, 95)
C_LIGHT_GRAY = (185, 195, 215)
C_PANEL = (11, 14, 24)
C_RED = (255, 50, 50)
C_ORANGE = (255, 140, 0)
C_YELLOW = (255, 220, 40)
C_GREEN = (45, 230, 110)
C_CYAN = (40, 230, 255)
C_BLUE = (45, 115, 255)
C_PURPLE = (185, 65, 255)
C_PINK = (255, 85, 190)

# Вертикальная игровая арена (формат TATE) по центру экрана
GAME_W = min(int(H * 0.72), W - 560)
GAME_X = (W - GAME_W) // 2
PLAY_RECT = pygame.Rect(GAME_X, 0, GAME_W, H)

# Шрифты интерфейса
F_MAIN = pygame.font.SysFont("Arial", 36, bold=True)
F_SUB = pygame.font.SysFont("Arial", 22, bold=True)
F_MINI = pygame.font.SysFont("Arial", 16, bold=True)
F_LOC = pygame.font.SysFont("Arial", 64, bold=True)

# Группы спрайтов для обновления и проверки столкновений
player_group = pygame.sprite.GroupSingle()
player_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemy_lasers = pygame.sprite.Group()
