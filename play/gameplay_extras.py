"""Дополнительные механики: грейз, выпадающие бонусы, комбо-счёт и всплывающий урон."""
import pygame
import random
import math
from play import constants as c
from play.vfx import vfx, draw_additive_glow
from play.sfx import sfx


class FloatingText:
    """Всплывающий текст над объектами (урон, грейз, подбор бонуса)."""

    def __init__(self, x, y, text, color, life=36):
        self.x = float(x) + random.uniform(-10, 10)
        self.y = float(y)
        self.vy = -1.35
        self.text = str(text)
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.y += self.vy
        self.vy *= 0.96
        self.life -= 1
        return self.life != 0

    def draw(self):
        surf = c.F_MINI.render(self.text, True, self.color)
        surf.set_alpha(int(255 * (self.life / self.max_life)))
        c.screen.blit(surf, surf.get_rect(center=(int(self.x), int(self.y))))


class PowerupOrb:
    """Магнитная капсула усиления, выпадающая из побеждённых врагов."""

    TYPES = {
        "hp": ("+1 HP", c.C_GREEN),
        "cd": ("-КД", c.C_CYAN),
        "rapid": ("ТЕМП", c.C_ORANGE),
    }

    def __init__(self, x, y, kind):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.label, self.color = self.TYPES[kind]
        self.vy = 1.6
        self.life = 480

    def update(self, player):
        """Двигает сферу вниз или притягивает к игроку в радиусе 150 пикселей."""
        self.life -= 1
        if player:
            dx = player.rect.centerx - self.x
            dy = player.rect.centery - self.y
            dist = math.hypot(dx, dy)
            if int(dist) in range(150):
                spd = 5.5
                self.x += (dx / max(1.0, dist)) * spd
                self.y += (dy / max(1.0, dist)) * spd
            else:
                self.y += self.vy
        else:
            self.y += self.vy
        return self.life != 0 and self.y in range(c.H + 30)

    def draw(self):
        ix, iy = int(self.x), int(self.y)
        draw_additive_glow(ix, iy, 22, self.color, intensity=80)
        pygame.draw.circle(c.screen, (14, 18, 30), (ix, iy), 13)
        pygame.draw.circle(c.screen, self.color, (ix, iy), 13, 2)
        t = c.F_MINI.render(self.label, True, c.C_WHITE)
        c.screen.blit(t, t.get_rect(center=(ix, iy)))


class ExtrasManager:
    """Управляет очками, множителем комбо, проверкой грейза и бонусами."""

    def __init__(self):
        self.texts = []
        self.orbs = []
        self.grazed_ids = set()
        self.score = 0
        self.combo = 1
        self.combo_timer = 0
        self.rapid_timer = 0

    def reset(self):
        self.texts.clear()
        self.orbs.clear()
        self.grazed_ids.clear()
        self.score = 0
        self.combo = 1
        self.combo_timer = 0
        self.rapid_timer = 0

    def spawn_damage_text(self, x, y, amount, color=c.C_WHITE):
        self.texts.append(FloatingText(x, y, f"-{amount}", color, 30))

    def add_kill_score(self, x, y, base_pts=100):
        """Начисляет очки с учётом комбо и с шансом 24% создаёт сферу бонуса."""
        self.combo = min(10, self.combo + 1)
        self.combo_timer = 180
        self.score += base_pts * self.combo
        if random.random() < 0.24:
            kind = random.choice(("hp", "cd", "rapid"))
            self.orbs.append(PowerupOrb(x, y, kind))

    def _apply_orb(self, orb, player):
        """Применяет эффект подобранной сферы к игроку."""
        sfx.play("pickup")
        vfx.spawn_hit(orb.x, orb.y, orb.color, 10)
        if orb.kind == "hp":
            player.hp = min(player.max_hp, player.hp + 1)
            self.texts.append(FloatingText(player.rect.centerx, player.rect.top - 10, "+1 HP!", c.C_GREEN, 40))
        elif orb.kind == "cd":
            player.dash_cooldown = max(0, player.dash_cooldown - 180)
            player.v_cooldown = max(0, player.v_cooldown - 180)
            player.b_cooldown = max(0, player.b_cooldown - 300)
            self.texts.append(FloatingText(player.rect.centerx, player.rect.top - 10, "ОТКАТ СКИЛЛОВ!", c.C_CYAN, 40))
        elif orb.kind == "rapid":
            self.rapid_timer = 300
            self.texts.append(FloatingText(player.rect.centerx, player.rect.top - 10, "УСКОРЕНИЕ 5с!", c.C_ORANGE, 40))

    def update(self):
        if self.combo_timer:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo = 1

        p = c.player_group.sprite
        if p:
            if self.rapid_timer:
                self.rapid_timer -= 1
                p.v_cooldown = max(0, p.v_cooldown - 1)
                p.b_cooldown = max(0, p.b_cooldown - 1)

            # Проверка пролёта вражеских пуль вплотную к игроку (Грейз)
            px, py = p.rect.center
            for b in c.enemy_bullets:
                bid = id(b)
                if bid not in self.grazed_ids:
                    dist = math.hypot(b.rect.centerx - px, b.rect.centery - py)
                    if int(dist) in range(14, 42):
                        self.grazed_ids.add(bid)
                        self.score += 25 * self.combo
                        p.v_cooldown = max(0, p.v_cooldown - 18)
                        p.b_cooldown = max(0, p.b_cooldown - 25)
                        sfx.play("graze")
                        vfx.spawn_hit(px, py, c.C_YELLOW, 3)
                        self.texts.append(FloatingText(px, py - 24, "ГРЕЙЗ!", c.C_YELLOW, 24))

        alive_orbs = []
        for orb in self.orbs:
            if not orb.update(p):
                continue
            if p and math.hypot(orb.x - p.rect.centerx, orb.y - p.rect.centery) in range(34):
                self._apply_orb(orb, p)
                continue
            alive_orbs.append(orb)
        self.orbs = alive_orbs
        self.texts = [t for t in self.texts if t.update()]

    def draw(self):
        for orb in self.orbs:
            orb.draw()
        for t in self.texts:
            t.draw()


extras = ExtrasManager()
