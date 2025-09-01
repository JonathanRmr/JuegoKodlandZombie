import pygame
import math


BLANCO = (255, 255, 255)

class Jugador(pygame.sprite.Sprite):
    def __init__(self, sonido_disparo):
        super().__init__()
        self.imagen_original = pygame.image.load('./images/player.png').convert_alpha()
        self.imagen_original = pygame.transform.scale(self.imagen_original, (64, 64))
        self.image = self.imagen_original
        self.rect = self.image.get_rect(center=(400, 300))
        self.velocidad = 5
        self.salud = 100
        self.max_salud = 100
        self.angulo = 0
        self.sonido_disparo = sonido_disparo

    def mover(self, PANTALLA_ANCHO, PANTALLA_ALTO):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        self.angulo = math.degrees(math.atan2(-dy, dx)) - 90
        self.image = pygame.transform.rotate(self.imagen_original, self.angulo)
        self.rect = self.image.get_rect(center=self.rect.center)
        teclas = pygame.key.get_pressed()
        mov_x, mov_y = 0, 0
        if teclas[pygame.K_w]:
            mov_y -= 1
        if teclas[pygame.K_s]:
            mov_y += 1
        if teclas[pygame.K_a]:
            mov_x -= 1
        if teclas[pygame.K_d]:
            mov_x += 1
        if mov_x != 0 and mov_y != 0:
            mov_x /= math.sqrt(2)
            mov_y /= math.sqrt(2)
        self.rect.x += mov_x * self.velocidad
        self.rect.y += mov_y * self.velocidad
        self.rect.clamp_ip(pygame.Rect(0, 0, PANTALLA_ANCHO, PANTALLA_ALTO))

    def disparar(self, grupo_balas):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        nueva_bala = Bala(self.rect.center, mouse_x, mouse_y)
        grupo_balas.add(nueva_bala)
        self.sonido_disparo.play()

class Bala(pygame.sprite.Sprite):
    def __init__(self, pos, target_x, target_y):
        super().__init__()
        self.image = pygame.image.load('./images/bullet.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (16, 16))
        self.rect = self.image.get_rect(center=pos)
        self.velocidad = 10
        dx = target_x - pos[0]
        dy = target_y - pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            dist = 1
        self.dir_x = dx / dist
        self.dir_y = dy / dist

    def update(self, PANTALLA_ANCHO, PANTALLA_ALTO):
        self.rect.x += self.dir_x * self.velocidad
        self.rect.y += self.dir_y * self.velocidad
        if not pygame.Rect(0, 0, PANTALLA_ANCHO, PANTALLA_ALTO).colliderect(self.rect):
            self.kill()