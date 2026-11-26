"""Реализация 9 фаз атак финального Красного босса."""
import pygame
import random
import math
from play import constants as c
from play.enemy_projectiles import EnemyBullet, EnemyLaser
from play.red_boss_projectiles import (
    RedBossBullet, HomingMineBullet, ContractingRingBullet, RotatingBeamLaser, ChessHazardZone
)


def run_phase_1_to_5(boss):
    """Управляет первыми 5 фазами финального босса."""
    # Фаза 1: кровавый дождь сверху + прицельный веер из 5 снарядов
    if boss.phase == 1:
        boss.move_towards(boss.top_pos, 5.0)
        if boss.timer % 4 == 0:
            for _ in range(2):
                rx = random.randint(c.PLAY_RECT.left + 20, c.PLAY_RECT.right - 20)
                c.enemy_bullets.add(EnemyBullet((rx, 10), pygame.math.Vector2(0, 1), random.uniform(3.5, 6.5), c.C_RED, 1.0, 1))
        if boss.timer % 35 == 0:
            base_a = math.degrees(math.atan2(boss.dir_to_player().y, boss.dir_to_player().x))
            for off in [-24, -12, 0, 12, 24]:
                vec = pygame.math.Vector2(math.cos(math.radians(base_a + off)), math.sin(math.radians(base_a + off)))
                c.enemy_bullets.add(EnemyBullet(boss.rect.center, vec, 4.5, c.C_ORANGE, 1.3, 1))
        if boss.timer >= 360:
            c.enemy_bullets.empty()
            boss.next_phase(2)
            boss.hidden = boss.invulnerable = True
            boss.image = pygame.Surface((1, 1), pygame.SRCALPHA)
            cw, ch = c.GAME_W // 2, c.H // 4
            px, py = c.player_group.sprite.rect.center if c.player_group.sprite else c.PLAY_RECT.center
            col = 0 if px < c.PLAY_RECT.centerx else 1
            row = max(0, min(3, py // ch))
            boss.trap_rect = pygame.Rect(c.PLAY_RECT.left + col * cw, row * ch, cw, ch)

    # Фаза 2: запирание игрока в одном из 8 секторов + перекрёстные лазеры из углов
    elif boss.phase == 2:
        cw, ch = c.GAME_W // 2, c.H // 4
        for r in range(4):
            for col_i in range(2):
                pygame.draw.rect(c.screen, c.C_GRAY, pygame.Rect(c.PLAY_RECT.left + col_i * cw, r * ch, cw, ch), 1)
        if boss.trap_rect:
            pygame.draw.rect(c.screen, c.C_RED, boss.trap_rect, 4)
            if boss.timer % 36 == 1:
                corners = [boss.trap_rect.topleft, boss.trap_rect.topright, boss.trap_rect.bottomleft, boss.trap_rect.bottomright]
                for c_pos in random.sample(corners, 2):
                    sc = pygame.math.Vector2(c_pos)
                    rpt = pygame.math.Vector2(random.randint(boss.trap_rect.left + 20, boss.trap_rect.right - 20),
                                              random.randint(boss.trap_rect.top + 20, boss.trap_rect.bottom - 20))
                    anchor = type("Anchor", (), {"rect": pygame.Rect(sc.x, sc.y, 1, 1), "alive": lambda s: True})()
                    c.enemy_lasers.add(EnemyLaser(anchor, rpt - sc, 1, 22, 22, 10, c.C_RED, max_length=1500))
        if boss.timer >= 300:
            boss.next_phase(3)

    # Фаза 3: 4 вращающихся луча в центре арены + сжимающиеся и разлетающиеся сферы
    elif boss.phase == 3:
        if boss.move_towards(boss.center_pos, 7.0):
            if boss.sub_step == 0:
                boss.sub_step = 1
                for i in range(4):
                    c.enemy_lasers.add(RotatingBeamLaser(boss, i * 90, 0.65, reverse_every=120, life=330, dmg=1))

            cycle = boss.timer % 90
            if cycle == 5:
                boss.ring_bullets = []
                for i in range(18):
                    rad = math.radians(i * 20)
                    b = EnemyBullet(boss.pos + pygame.math.Vector2(math.cos(rad), math.sin(rad)) * 210, pygame.math.Vector2(0, 1), 0, c.C_ORANGE, 2.0, 1)
                    boss.ring_bullets.append((b, rad))
                    c.enemy_bullets.add(b)
            elif 5 < cycle < 50:
                r_now = 210 - (cycle - 5) * 3.55
                for b, rad in boss.ring_bullets:
                    if b.alive():
                        b.pos = boss.pos + pygame.math.Vector2(math.cos(rad), math.sin(rad)) * r_now
            elif cycle == 50:
                for b, rad in boss.ring_bullets:
                    if b.alive():
                        b.direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                        b.speed = 8.5

        if boss.timer >= 360:
            for b, rad in boss.ring_bullets:
                if b.alive() and b.speed == 0:
                    b.direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                    b.speed = 8.5
            boss.ring_bullets = []
            boss.next_phase(4)

    # Фаза 4: самонаводящиеся мины + шахматные опасные зоны
    elif boss.phase == 4:
        boss.move_towards(boss.top_pos, 6.0)
        if boss.timer >= 25 and (boss.timer - 25) % 32 == 0 and boss.sub_step < 9:
            boss.sub_step += 1
            for i in range(16):
                rad = math.radians(i * (360 / 16))
                c.enemy_bullets.add(HomingMineBullet(boss.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)), 1))
        if boss.timer in (30, 135, 240):
            parity = 1 if boss.timer == 135 else 0
            cw, ch = c.GAME_W // 4, c.H // 6
            for r in range(6):
                for col_i in range(4):
                    if (r + col_i) % 2 == parity:
                        c.enemy_lasers.add(ChessHazardZone(pygame.Rect(c.PLAY_RECT.left + col_i * cw, r * ch, cw, ch), 1))
        if boss.timer >= 330:
            boss.next_phase(5)

    # Фаза 5: синусоидальные волны + 4 орбитальных спутника вокруг босса
    elif boss.phase == 5:
        boss.move_towards(boss.top_pos, 5.0)
        boss.orbit_angle += 0.05
        for i in range(4):
            ang = boss.orbit_angle + i * (math.pi / 2)
            sx, sy = boss.pos.x + math.cos(ang) * 115, boss.pos.y + math.sin(ang) * 115
            pygame.draw.circle(c.screen, c.C_RED, (int(sx), int(sy)), 14)
            pygame.draw.circle(c.screen, c.C_WHITE, (int(sx), int(sy)), 5)
            if boss.timer % 90 == 0:
                c.enemy_bullets.add(EnemyBullet((sx, sy), boss.dir_to_player(pygame.math.Vector2(sx, sy)), 4.5, c.C_YELLOW, 1.1, 1))
        if boss.timer % 24 == 0:
            for off in [-25, 0, 25]:
                rad = math.radians(90 + off)
                c.enemy_bullets.add(RedBossBullet(boss.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)), 4.2, c.C_RED, 1.2, 1, mode="sine"))
        if boss.timer >= 360:
            boss.next_phase(6)


def run_phase_6_to_9(boss):
    """Управляет фазами 6–9 финального босса."""
    # Фаза 6: уход за верхний край, гравитационное притяжение и поток пуль снизу
    if boss.phase == 6:
        boss.invulnerable = boss.gravity_pull = True
        boss.move_towards(pygame.math.Vector2(c.PLAY_RECT.centerx, -110), 6.0)
        if boss.timer <= 280 and boss.timer % 4 == 0:
            for _ in range(2):
                rx = random.randint(c.PLAY_RECT.left + 20, c.PLAY_RECT.right - 20)
                c.enemy_bullets.add(RedBossBullet((rx, c.H - 10), pygame.math.Vector2(0, -1), random.uniform(2.5, 4.2), c.C_RED, random.uniform(1.0, 2.3), 1, mode="gravity"))
        if boss.timer >= 660:
            boss.next_phase(7)

    # Фаза 7: каскадные фейерверки + снайперские залпы с лазерным целеуказателем
    elif boss.phase == 7:
        boss.move_towards(boss.top_pos, 6.0)
        if boss.timer % 55 == 0:
            for off in [-30, 0, 30]:
                rad = math.radians(90 + off)
                c.enemy_bullets.add(RedBossBullet(boss.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)), 4.0, c.C_RED, 2.0, 1, mode="firework", split_y=c.H // 2))
        if boss.timer % 50 == 15 and boss.sub_step < 5:
            boss.sub_step += 1
            d = boss.dir_to_player()
            base_a = math.degrees(math.atan2(d.y, d.x))
            c.enemy_lasers.add(EnemyLaser(boss, d, 0, 14, 4, 2, c.C_YELLOW))
            c.enemy_bullets.add(EnemyBullet(boss.rect.center, d, 8.5, c.C_WHITE, 1.3, 1))
            for side in [-14, 14]:
                v_side = pygame.math.Vector2(math.cos(math.radians(base_a + side)), math.sin(math.radians(base_a + side)))
                c.enemy_bullets.add(EnemyBullet(boss.rect.center, v_side, 7.8, c.C_RED, 1.1, 1))
        if boss.timer >= 330:
            boss.next_phase(8)

    # Фаза 8: сжимающееся кольцо вокруг игрока с окном для выхода + маятник
    elif boss.phase == 8:
        boss.pos.y = boss.top_pos.y
        boss.pos.x = c.PLAY_RECT.centerx + math.sin(boss.timer * 0.05) * (c.GAME_W // 2 - 95)
        if boss.timer == 20 and c.player_group.sprite:
            p_center = c.player_group.sprite.rect.center
            gap_start = random.randint(0, 320)
            for deg in range(0, 360, 10):
                if not (gap_start <= deg <= gap_start + 45):
                    c.enemy_bullets.add(ContractingRingBullet(p_center, 340, deg, shrink_spd=1.35, rot_spd=0.65, dmg=1))
        if boss.timer % 8 == 0:
            c.enemy_bullets.add(EnemyBullet(boss.rect.center, pygame.math.Vector2(0, 1), 2.8, c.C_RED, 1.2, 1))
        if boss.timer >= 360:
            boss.next_phase(9)

    # Фаза 9: финальный катарсис — 3 вращающихся луча и круговые залпы
    elif boss.phase == 9:
        if boss.move_towards(boss.center_pos, 6.0):
            if boss.sub_step == 0:
                boss.sub_step = 1
                for i in range(3):
                    c.enemy_lasers.add(RotatingBeamLaser(boss, i * 120, 0.7, reverse_every=180, life=340, dmg=1))
            if boss.timer % 45 == 0:
                for i in range(20):
                    rad = math.radians(i * 18 + (boss.timer % 36))
                    c.enemy_bullets.add(EnemyBullet(boss.rect.center, pygame.math.Vector2(math.cos(rad), math.sin(rad)), 4.5, c.C_RED, 1.6, 1))
        if boss.timer >= 360:
            boss.next_phase(1)
