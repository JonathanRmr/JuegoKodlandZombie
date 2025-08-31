import pygame
import random
import math

# Inicializar Pygame
pygame.init()

# --- Configuración de la pantalla ---
PANTALLA_ANCHO = 800
PANTALLA_ALTO = 600
pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("Zombie Survival")

# --- Colores ---
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)

# --- Clases del juego ---

class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.imagen_original = pygame.image.load('./images/player.png').convert_alpha() # Carga la imagen del jugador
        # Cambia el tamaño de la imagen (por ejemplo, 64x64 píxeles)
        self.imagen_original = pygame.transform.scale(self.imagen_original, (64, 64))
        self.image = self.imagen_original
        self.rect = self.image.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2))
        self.velocidad = 5
        self.salud = 100
        self.max_salud = 100
        self.angulo = 0  # Ángulo de rotación actual

    def mover(self):
        # Obtener la posición del mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calcular el ángulo entre el jugador y el mouse
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        self.angulo = math.degrees(math.atan2(-dy, dx)) - 90
        
        # Rotar la imagen
        self.image = pygame.transform.rotate(self.imagen_original, self.angulo)
        self.rect = self.image.get_rect(center=self.rect.center)
        # Movimiento normal con WASD
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
        
        # Normalizar la velocidad para el movimiento diagonal
        if mov_x != 0 and mov_y != 0:
            mov_x /= math.sqrt(2)
            mov_y /= math.sqrt(2)

        self.rect.x += mov_x * self.velocidad
        self.rect.y += mov_y * self.velocidad

        # Mantener al jugador dentro de la pantalla
        self.rect.clamp_ip(pantalla.get_rect())

    def disparar(self, grupo_balas):
        # La bala se crea en la posición del jugador y se mueve hacia el mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        nueva_bala = Bala(self.rect.center, mouse_x, mouse_y)
        grupo_balas.add(nueva_bala)

class Bala(pygame.sprite.Sprite):
    def __init__(self, pos, target_x, target_y):
        super().__init__()
        self.image = pygame.image.load('./images/bullet.png').convert_alpha() # Carga la imagen de la bala
        self.image = pygame.transform.scale(self.image, (16, 16))
        self.rect = self.image.get_rect(center=pos)
        self.velocidad = 10

        # Calcular dirección y normalizar
        dx = target_x - pos[0]
        dy = target_y - pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            dist = 1
        self.dir_x = dx / dist
        self.dir_y = dy / dist

    def update(self):
        self.rect.x += self.dir_x * self.velocidad
        self.rect.y += self.dir_y * self.velocidad
        
        # Eliminar la bala si sale de la pantalla
        if not pantalla.get_rect().colliderect(self.rect):
            self.kill()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, velocidad):
        super().__init__()
        self.image = pygame.image.load('./images/zombie.png').convert_alpha() # Carga la imagen del zombie
        # Posicionar el zombie aleatoriamente fuera de la pantalla
        self.image = pygame.transform.scale(self.image, (64, 64))
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.rect = self.image.get_rect(bottomleft=(random.randint(0, PANTALLA_ANCHO), 0))
        elif side == 'bottom':
            self.rect = self.image.get_rect(topleft=(random.randint(0, PANTALLA_ANCHO), PANTALLA_ALTO))
        elif side == 'left':
            self.rect = self.image.get_rect(topright=(0, random.randint(0, PANTALLA_ALTO)))
        elif side == 'right':
            self.rect = self.image.get_rect(topleft=(PANTALLA_ANCHO, random.randint(0, PANTALLA_ALTO)))

        self.velocidad = velocidad

    def update(self, jugador_pos):
        # IA básica: seguir al jugador
        dx = jugador_pos[0] - self.rect.centerx
        dy = jugador_pos[1] - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            self.rect.x += (dx / dist) * self.velocidad
            self.rect.y += (dy / dist) * self.velocidad

# --- Funciones y bucle principal del juego ---

def mostrar_hud(salud, oleada, zombis_restantes):
    fuente = pygame.font.Font(None, 36)
    salud_texto = fuente.render(f"Salud: {salud}", True, BLANCO)
    oleada_texto = fuente.render(f"Oleada: {oleada}", True, BLANCO)
    zombis_texto = fuente.render(f"Zombis: {zombis_restantes}", True, BLANCO)

    pantalla.blit(salud_texto, (10, 10))
    pantalla.blit(oleada_texto, (10, 50))
    pantalla.blit(zombis_texto, (10, 90))

def juego():
    # Grupos de sprites
    grupo_sprites = pygame.sprite.Group()
    grupo_zombies = pygame.sprite.Group()
    grupo_balas = pygame.sprite.Group()

    jugador = Jugador()
    grupo_sprites.add(jugador)

    # Variables del juego
    oleada_actual = 1
    velocidad_zombies = 1.0
    num_zombies_en_oleada = 5
    zombis_eliminados = 0

    # Bucle principal del juego
    corriendo = True
    reloj = pygame.time.Clock()

    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                jugador.disparar(grupo_balas)

        # Lógica del juego
        jugador.mover()
        grupo_balas.update()
        grupo_zombies.update(jugador.rect.center)

        # Colisiones de balas con zombies
        colisiones = pygame.sprite.groupcollide(grupo_zombies, grupo_balas, True, True)
        if colisiones:
            zombis_eliminados += len(colisiones)

        # Colisiones de jugador con zombies (quitar salud)
        if pygame.sprite.spritecollide(jugador, grupo_zombies, False):
            jugador.salud -= 1 # Pequeño daño
            if jugador.salud <= 0:
                corriendo = False # Fin del juego

        # Lógica de oleadas
        if len(grupo_zombies) == 0:
            zombis_eliminados = 0
            # Aumentar la dificultad para la siguiente oleada
            oleada_actual += 1
            num_zombies_en_oleada += 3
            velocidad_zombies += 0.2

            # Generar los nuevos zombies
            for _ in range(num_zombies_en_oleada):
                nuevo_zombie = Zombie(velocidad_zombies)
                grupo_zombies.add(nuevo_zombie)
                grupo_sprites.add(nuevo_zombie)
        
        # TODO: Lógica para el Boss cada 5 oleadas

        # Renderizado
        # Cargar y mostrar la imagen de fondo
        fondo = pygame.image.load('./images/fondo.png').convert()
        fondo = pygame.transform.scale(fondo, (PANTALLA_ANCHO, PANTALLA_ALTO))
        pantalla.blit(fondo, (0, 0))
        
        grupo_sprites.draw(pantalla)
        grupo_balas.draw(pantalla)
        
        mostrar_hud(jugador.salud, oleada_actual, len(grupo_zombies))

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()

# Iniciar el juego
if __name__ == "__main__":
    juego()