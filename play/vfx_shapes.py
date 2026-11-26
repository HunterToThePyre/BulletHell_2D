"""Процедурная генерация неоновых спрайтов врагов, боссов, свечений и маски виньетки."""
import pygame
import math
from play import constants as c


def draw_additive_glow(x, y, radius, color, intensity=90):
    """Накладывает мягкое аддитивное свечение в указанной точке."""
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (radius, radius)
    rc, gc, bc = color[:3]
    for step in range(4, 0, -1):
        r = int(radius * (step / 4.0))
        alpha = int(intensity * (1.0 - (step - 1) / 4.0))
        c_step = (
            min(255, int(rc * alpha / 255)),
            min(255, int(gc * alpha / 255)),
            min(255, int(bc * alpha / 255))
        )
        pygame.draw.circle(surf, c_step, center, r)
    c.screen.blit(surf, (int(x - radius), int(y - radius)), special_flags=pygame.BLEND_RGB_ADD)


def draw_glow_rect(rect, color, border_radius=8, glow_size=14, alpha_max=65):
    """Рисует неоновый ореол вокруг прямоугольных кнопок и карточек меню."""
    r = pygame.Rect(rect)
    rc, gc, bc = color[:3]
    for i in range(3, 0, -1):
        pad = int(glow_size * (i / 3.0))
        al = int(alpha_max * (1.0 - (i - 1) / 3.0))
        g_surf = pygame.Surface((r.w + pad * 2, r.h + pad * 2), pygame.SRCALPHA)
        pygame.draw.rect(g_surf, (rc, gc, bc, al), (0, 0, r.w + pad * 2, r.h + pad * 2), border_radius=border_radius + pad // 2)
        c.screen.blit(g_surf, (r.x - pad, r.y - pad))


def build_vignette_mask():
    """Строит полноэкранную красную рамку-виньетку с плавным затуханием к центру."""
    surf = pygame.Surface((c.W, c.H), pygame.SRCALPHA)
    steps = 28
    for i in range(steps):
        t = 1.0 - (i / steps)
        alpha = int(255 * (t ** 2.2))
        thickness = max(2, int((min(c.W, c.H) * 0.24) / steps))
        inset = i * thickness
        pygame.draw.rect(surf, (220, 10, 20, alpha), (inset, inset, c.W - inset * 2, c.H - inset * 2), thickness)
    return surf


def make_glow_circle(radius, color, core_white=True):
    """Создаёт светящуюся энергетическую сферу-снаряд с белым ядром."""
    pad = max(7, int(radius * 0.65))
    full_r = radius + pad
    surf = pygame.Surface((full_r * 2, full_r * 2), pygame.SRCALPHA)
    center = (full_r, full_r)
    rc, gc, bc = color[:3]

    for i in range(4, 0, -1):
        r_step = radius + int(pad * (i / 4.0))
        alpha = int(70 * (1.0 - (i - 1) / 4.0))
        pygame.draw.circle(surf, (rc, gc, bc, alpha), center, r_step)

    pygame.draw.circle(surf, (rc, gc, bc), center, radius)
    if core_white and radius not in (0, 1, 2, 3):
        pygame.draw.circle(surf, (255, 255, 255), center, max(2, int(radius * 0.52)))
    return surf


def make_neon_shape(shape, color, size=44):
    """Генерирует неоновый спрайт врага (треугольник, квадрат или шестиугольник)."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    r = size // 2 - 6
    rc, gc, bc = color[:3]

    if shape == "tri":
        pts_outer = [(cx, size - 4), (size - 4, 5), (4, 5)]
        pts_inner = [(cx, size - 11), (size - 10, 10), (10, 10)]
    elif shape == "sq":
        pts_outer = [(5, 5), (size - 5, 5), (size - 5, size - 5), (5, size - 5)]
        pts_inner = [(10, 10), (size - 10, 10), (size - 10, size - 10), (10, size - 10)]
    else:
        pts_outer = [(cx + int(r * math.cos(math.radians(60 * i - 30))),
                      cy + int(r * math.sin(math.radians(60 * i - 30)))) for i in range(6)]
        pts_inner = [(cx + int((r - 5) * math.cos(math.radians(60 * i - 30))),
                      cy + int((r - 5) * math.sin(math.radians(60 * i - 30)))) for i in range(6)]

    pygame.draw.polygon(surf, (rc, gc, bc, 80), pts_outer)
    pygame.draw.polygon(surf, (rc, gc, bc), pts_outer, 3)
    pygame.draw.polygon(surf, (rc, gc, bc, 150), pts_inner)
    pygame.draw.polygon(surf, (255, 255, 255), pts_outer, 1)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 4)
    return surf


def make_boss_surface(radius, main_col, ring_col):
    """Генерирует многослойный неоновый корпус босса с энергетическим ядром."""
    pad = 22
    full = radius + pad
    surf = pygame.Surface((full * 2, full * 2), pygame.SRCALPHA)
    center = (full, full)
    rm, gm, bm = main_col[:3]
    rr, gr, br = ring_col[:3]

    for i in range(5, 0, -1):
        alpha = int(65 * (1.0 - (i - 1) / 5.0))
        pygame.draw.circle(surf, (rm, gm, bm, alpha), center, radius + int(pad * i / 5))

    pygame.draw.circle(surf, (14, 14, 24), center, radius)
    pygame.draw.circle(surf, (rm, gm, bm), center, radius, 5)
    pygame.draw.circle(surf, (rr, gr, br), center, int(radius * 0.72), 3)
    pygame.draw.circle(surf, (rm, gm, bm, 130), center, int(radius * 0.48))
    pygame.draw.circle(surf, (255, 255, 255), center, int(radius * 0.24))
    return surf
