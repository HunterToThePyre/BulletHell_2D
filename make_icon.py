import struct
import pygame
from play import constants as c
from play.vfx_shapes import make_boss_surface

pygame.init()

size = 256
surf = pygame.Surface((size, size), pygame.SRCALPHA)

pygame.draw.rect(surf, (8, 12, 24), (0, 0, size, size), border_radius=48)
pygame.draw.rect(surf, c.C_RED, (4, 4, size - 8, size - 8), 6, border_radius=46)

boss_icon = make_boss_surface(82, c.C_RED, c.C_ORANGE)
surf.blit(boss_icon, boss_icon.get_rect(center=(size // 2, size // 2)))

pygame.image.save(surf, "icon.png")

with open("icon.png", "rb") as f:
    raw_png = f.read()

ico_header = struct.pack("<HHH", 0, 1, 1)
ico_entry = struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(raw_png), 22)

with open("icon.ico", "wb") as f:
    f.write(ico_header + ico_entry + raw_png)

pygame.quit()
print("Готово! Правильный файл icon.ico создан.")
