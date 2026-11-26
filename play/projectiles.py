"""Единый реестр спрайтов проекта и класс тренировочного манекена."""
import pygame
from play import constants as c
from play.enemy_projectiles import EnemyBullet, ExpandingRingBullet, BulletTether, EnemyLaser
from play.enemies import Enemy
from play.boss import Boss, BlueCircleBoss
from play.purple_boss import PurpleCircleBoss
from play.red_boss import RedCircleBoss
from player.player_projectiles import PlayerBullet, OrbitShield, PlayerClone


class Dummy(pygame.sprite.Sprite):
    """Неподвижный тренировочный манекен с полосой HP для проверки урона."""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.image, c.C_RED, (30, 30), 30)
        self.rect = self.image.get_rect(center=(c.PLAY_RECT.centerx, c.H // 3))
        self.hp, self.max_hp = 10, 10

    def update(self):
        pygame.draw.rect(c.screen, c.C_GRAY, (self.rect.x, self.rect.y - 15, 60, 8))
        if self.hp > 0:
            w = int(60 * (self.hp / self.max_hp))
            pygame.draw.rect(c.screen, c.C_GREEN, (self.rect.x, self.rect.y - 15, w, 8))
