import pygame
import random
import math

class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, angle, PANTALLA_ANCHO, PANTALLA_ALTO):
        super().__init__()
        self.image = pygame.image.load('./images/bullet_boss.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect(center=pos)
        self.velocidad = 7
        self.dir_x = math.cos(math.radians(angle))
        self.dir_y = math.sin(math.radians(angle))
        self.PANTALLA_ANCHO = PANTALLA_ANCHO
        self.PANTALLA_ALTO = PANTALLA_ALTO

    def update(self):
        self.rect.x += self.dir_x * self.velocidad
        self.rect.y += self.dir_y * self.velocidad
        if self.rect.left <= 0 or self.rect.right >= self.PANTALLA_ANCHO:
            self.dir_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= self.PANTALLA_ALTO:
            self.dir_y *= -1

class Boss(pygame.sprite.Sprite):
    def __init__(self, PANTALLA_ANCHO, PANTALLA_ALTO, grupo_proyectiles_boss):
        super().__init__()
        self.imagen_original = pygame.image.load('./images/boss.png').convert_alpha()
        self.imagen_original = pygame.transform.scale(self.imagen_original, (128, 128))
        self.image = self.imagen_original
        self.rect = self.image.get_rect()
        self.rect.centerx = PANTALLA_ANCHO // 2
        self.rect.bottom = -self.rect.height
        self.salud = 30
        self.velocidad_descenso = 3
        self.descendiendo = True
        self.PANTALLA_ANCHO = PANTALLA_ANCHO
        self.PANTALLA_ALTO = PANTALLA_ALTO
        self.grupo_proyectiles_boss = grupo_proyectiles_boss
        
        self.last_shot = pygame.time.get_ticks()
        self.shot_delay = random.randint(3000, 5000)

        self.angulo_movimiento = 0
        self.radio_movimiento = 150
        self.velocidad_circular = 0.02
        self.centro_x = PANTALLA_ANCHO // 2
        self.centro_y = PANTALLA_ALTO // 2
        self.angulo = 0
        
    def update(self, jugador_pos):
        dx_rotacion = jugador_pos[0] - self.rect.centerx
        dy_rotacion = jugador_pos[1] - self.rect.centery
        self.angulo = math.degrees(math.atan2(-dy_rotacion, dx_rotacion)) + 90
        self.image = pygame.transform.rotate(self.imagen_original, self.angulo)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.descendiendo:
            self.rect.y += self.velocidad_descenso
            if self.rect.top >= 50:
                self.rect.top = 50
                self.descendiendo = False
        else:
            self.angulo_movimiento += self.velocidad_circular
            self.rect.centerx = self.centro_x + self.radio_movimiento * math.cos(self.angulo_movimiento)
            self.rect.centery = self.centro_y + self.radio_movimiento * math.sin(self.angulo_movimiento)
        
        now = pygame.time.get_ticks()
        if not self.descendiendo and now - self.last_shot > self.shot_delay:
            self.last_shot = now
            self.shot_delay = random.randint(3000, 5000)
            self.disparar_proyectiles_abanico(jugador_pos)

    def disparar_proyectiles_abanico(self, jugador_pos):
        num_proyectiles = 7
        
        dx = jugador_pos[0] - self.rect.centerx
        dy = jugador_pos[1] - self.rect.centery
        angulo_hacia_jugador = math.degrees(math.atan2(-dy, dx))
        
        angulo_inicial = angulo_hacia_jugador - 30
        incremento_angulo = 10
        
        for i in range(num_proyectiles):
            angulo = angulo_inicial + i * incremento_angulo
            proyectil = BossProjectile(self.rect.center, angulo, self.PANTALLA_ANCHO, self.PANTALLA_ALTO)
            self.grupo_proyectiles_boss.add(proyectil)