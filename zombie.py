import pygame
import random
import math

class Zombie(pygame.sprite.Sprite):
    def __init__(self, velocidad, PANTALLA_ANCHO, PANTALLA_ALTO):
        super().__init__()
        self.imagen_original = pygame.image.load('./images/zombie.png').convert_alpha()
        self.imagen_original = pygame.transform.scale(self.imagen_original, (64, 64))
        self.image = self.imagen_original
        self.rect = self.image.get_rect()
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.rect.bottomleft = (random.randint(0, PANTALLA_ANCHO), 0)
        elif side == 'bottom':
            self.rect.topleft = (random.randint(0, PANTALLA_ANCHO), PANTALLA_ALTO)
        elif side == 'left':
            self.rect.topright = (0, random.randint(0, PANTALLA_ALTO))
        elif side == 'right':
            self.rect.topleft = (PANTALLA_ANCHO, random.randint(0, PANTALLA_ALTO))
        self.velocidad = velocidad

    def update(self, jugador_pos):
        dx_rotacion = jugador_pos[0] - self.rect.centerx
        dy_rotacion = jugador_pos[1] - self.rect.centery
        angulo = math.degrees(math.atan2(-dy_rotacion, dx_rotacion)) + 90
        self.image = pygame.transform.rotate(self.imagen_original, angulo)
        self.rect = self.image.get_rect(center=self.rect.center)
        dx = jugador_pos[0] - self.rect.centerx
        dy = jugador_pos[1] - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            self.rect.x += (dx / dist) * self.velocidad
            self.rect.y += (dy / dist) * self.velocidad