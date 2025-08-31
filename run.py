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

# --- Tipografía ---
fuente_titulo = pygame.font.Font(None, 72)
fuente_menu = pygame.font.Font(None, 48)
fuente_hud = pygame.font.Font(None, 36)

# --- Clases del juego ---

class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.imagen_original = pygame.image.load('./images/player.png').convert_alpha()
        self.imagen_original = pygame.transform.scale(self.imagen_original, (64, 64))
        self.image = self.imagen_original
        self.rect = self.image.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2))
        self.velocidad = 5
        self.salud = 100
        self.max_salud = 100
        self.angulo = 0
        # Cargar el sonido de disparo
        self.sonido_disparo = pygame.mixer.Sound('./sounds/shot.mp3')
        self.sonido_disparo.set_volume(0.2)  # Ajustar volumen al 20%

    def mover(self):
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
        self.rect.clamp_ip(pantalla.get_rect())

    def disparar(self, grupo_balas):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        nueva_bala = Bala(self.rect.center, mouse_x, mouse_y)
        grupo_balas.add(nueva_bala)
        # Reproducir el sonido de disparo
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

    def update(self):
        self.rect.x += self.dir_x * self.velocidad
        self.rect.y += self.dir_y * self.velocidad
        if not pantalla.get_rect().colliderect(self.rect):
            self.kill()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, velocidad):
        super().__init__()
        self.image = pygame.image.load('./images/zombie.png').convert_alpha()
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
        dx = jugador_pos[0] - self.rect.centerx
        dy = jugador_pos[1] - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            self.rect.x += (dx / dist) * self.velocidad
            self.rect.y += (dy / dist) * self.velocidad

# --- Funciones de juego ---

def mostrar_hud(salud, oleada, zombis_restantes):
    salud_texto = fuente_hud.render(f"Salud: {salud}", True, BLANCO)
    oleada_texto = fuente_hud.render(f"Oleada: {oleada}", True, BLANCO)
    zombis_texto = fuente_hud.render(f"Zombis: {zombis_restantes}", True, BLANCO)

    pantalla.blit(salud_texto, (10, 10))
    pantalla.blit(oleada_texto, (10, 50))
    pantalla.blit(zombis_texto, (10, 90))

# --- Funciones para los estados del juego ---

def mostrar_menu():
    fondo_menu = pygame.image.load('./images/fondo_menu.png').convert()
    fondo_menu = pygame.transform.scale(fondo_menu, (PANTALLA_ANCHO, PANTALLA_ALTO))
    pantalla.blit(fondo_menu, (0, 0))
    
    titulo = fuente_titulo.render("Zombie Survival", True, ROJO)
    instrucciones = fuente_menu.render("Presiona ESPACIO o ENTER para empezar", True, BLANCO)
    
    titulo_rect = titulo.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50))
    instrucciones_rect = instrucciones.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 + 50))

    pantalla.blit(titulo, titulo_rect)
    pantalla.blit(instrucciones, instrucciones_rect)

def mostrar_game_over():
    fondo_menu = pygame.image.load('./images/fondo_menu.png').convert()
    fondo_menu = pygame.transform.scale(fondo_menu, (PANTALLA_ANCHO, PANTALLA_ALTO))
    pantalla.blit(fondo_menu, (0, 0))
    
    game_over_texto = fuente_titulo.render("Game Over", True, ROJO)
    instrucciones = fuente_menu.render("Presiona ESPACIO o ENTER para reiniciar", True, BLANCO)

    game_over_rect = game_over_texto.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50))
    instrucciones_rect = instrucciones.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 + 50))
    
    pantalla.blit(game_over_texto, game_over_rect)
    pantalla.blit(instrucciones, instrucciones_rect)

def reiniciar_juego():
    global grupo_sprites, grupo_zombies, grupo_balas, jugador, oleada_actual, velocidad_zombies, num_zombies_en_oleada, zombis_eliminados
    
    grupo_sprites.empty()
    grupo_zombies.empty()
    grupo_balas.empty()
    
    jugador = Jugador()
    grupo_sprites.add(jugador)
    
    oleada_actual = 1
    velocidad_zombies = 1.0
    num_zombies_en_oleada = 5
    zombis_eliminados = 0
    
    # Generar los zombies de la primera oleada al reiniciar
    for _ in range(num_zombies_en_oleada):
        nuevo_zombie = Zombie(velocidad_zombies)
        grupo_zombies.add(nuevo_zombie)
        grupo_sprites.add(nuevo_zombie)
    
    return "JUGANDO"

# --- Bucle principal del juego ---

def juego():
    global grupo_sprites, grupo_zombies, grupo_balas, jugador, oleada_actual, velocidad_zombies, num_zombies_en_oleada, zombis_eliminados
    
    # Inicializar la música
    pygame.mixer.init()
    musica_fondo = pygame.mixer.Sound('./sounds/sountrack.mp3')
    musica_fondo.set_volume(0.6)  # Ajustar volumen al 60%
    
    grupo_sprites = pygame.sprite.Group()
    grupo_zombies = pygame.sprite.Group()
    grupo_balas = pygame.sprite.Group()

    jugador = Jugador()

    oleada_actual = 1
    velocidad_zombies = 1.0
    num_zombies_en_oleada = 5
    zombis_eliminados = 0
    
    estado_juego = "MENU"

    corriendo = True
    reloj = pygame.time.Clock()

    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            if estado_juego == "MENU" or estado_juego == "FIN_DEL_JUEGO":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                        estado_juego = reiniciar_juego()
                        musica_fondo.play(loops=-1)  # Comenzar la música al iniciar el juego

            elif estado_juego == "JUGANDO":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    jugador.disparar(grupo_balas)

        # Lógica de juego, solo si estamos en estado JUGANDO
        if estado_juego == "JUGANDO":
            jugador.mover()
            grupo_balas.update()
            grupo_zombies.update(jugador.rect.center)

            colisiones = pygame.sprite.groupcollide(grupo_zombies, grupo_balas, True, True)
            if colisiones:
                zombis_eliminados += len(colisiones)

            if pygame.sprite.spritecollide(jugador, grupo_zombies, False):
                jugador.salud -= 1
                if jugador.salud <= 0:
                    estado_juego = "FIN_DEL_JUEGO"
                    musica_fondo.stop()  # Detener la música cuando el jugador muere

            if len(grupo_zombies) == 0:
                zombis_eliminados = 0
                oleada_actual += 1
                num_zombies_en_oleada += 3
                velocidad_zombies += 0.2
                for _ in range(num_zombies_en_oleada):
                    nuevo_zombie = Zombie(velocidad_zombies)
                    grupo_zombies.add(nuevo_zombie)
                    grupo_sprites.add(nuevo_zombie)
        
        # Renderizado
        if estado_juego == "MENU":
            mostrar_menu()
        elif estado_juego == "JUGANDO":
            fondo = pygame.image.load('./images/fondo.png').convert()
            fondo = pygame.transform.scale(fondo, (PANTALLA_ANCHO, PANTALLA_ALTO))
            pantalla.blit(fondo, (0, 0))
            
            grupo_sprites.draw(pantalla)
            grupo_balas.draw(pantalla)
            
            mostrar_hud(jugador.salud, oleada_actual, len(grupo_zombies))
        elif estado_juego == "FIN_DEL_JUEGO":
            mostrar_game_over()
        
        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()

# Iniciar el juego
if __name__ == "__main__":
    juego()