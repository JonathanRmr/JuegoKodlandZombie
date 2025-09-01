import pygame
import random
import math
import time

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

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

# --- Tipografía ---
fuente_titulo = pygame.font.Font(None, 72)
fuente_menu = pygame.font.Font(None, 48)
fuente_hud = pygame.font.Font(None, 36)

# --- Sonidos ---
sonido_disparo = pygame.mixer.Sound('./sounds/shot.mp3')
sonido_disparo.set_volume(0.2)
try:
    musica_fondo = pygame.mixer.Sound('./sounds/sountrack.mp3')
    musica_fondo.set_volume(0.6)
    sonido_intro_boss = pygame.mixer.Sound('./sounds/intro_boss.mp3')
    sonido_base_boss = pygame.mixer.Sound('./sounds/base_boss.mp3')
    sonido_intro_boss.set_volume(0.7)
    sonido_base_boss.set_volume(0.6)
except pygame.error:
    print("Advertencia: No se pudieron cargar los archivos de sonido. Asegúrate de que estén en la carpeta 'sounds'.")

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
        sonido_disparo.play()

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

class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.image.load('./images/bullet_boss.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect(center=pos)
        self.velocidad = 7
        self.dir_x = math.cos(math.radians(angle))
        self.dir_y = math.sin(math.radians(angle))

    def update(self):
        self.rect.x += self.dir_x * self.velocidad
        self.rect.y += self.dir_y * self.velocidad
        if self.rect.left <= 0 or self.rect.right >= PANTALLA_ANCHO:
            self.dir_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= PANTALLA_ALTO:
            self.dir_y *= -1

class Boss(pygame.sprite.Sprite):
    def __init__(self):
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
            proyectil = BossProjectile(self.rect.center, angulo)
            grupo_proyectiles_boss.add(proyectil)

# --- Funciones de juego ---

def mostrar_hud(salud, oleada, zombis_restantes, boss_activo=False):
    salud_texto = fuente_hud.render(f"Salud: {salud}", True, BLANCO)
    pantalla.blit(salud_texto, (10, 10))
    if boss_activo:
        estado_texto = fuente_hud.render("¡BOSS FIGHT!", True, ROJO)
        pantalla.blit(estado_texto, (10, 50))
    else:
        oleada_texto = fuente_hud.render(f"Oleada: {oleada}", True, BLANCO)
        zombis_texto = fuente_hud.render(f"Zombis: {zombis_restantes}", True, BLANCO)
        pantalla.blit(oleada_texto, (10, 50))
        pantalla.blit(zombis_texto, (10, 90))

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

def mostrar_ganaste():
    fondo_menu = pygame.image.load('./images/fondo_menu.png').convert()
    fondo_menu = pygame.transform.scale(fondo_menu, (PANTALLA_ANCHO, PANTALLA_ALTO))
    pantalla.blit(fondo_menu, (0, 0))
    ganaste_texto = fuente_titulo.render("¡Felicitaciones, ganaste!", True, VERDE)
    instrucciones = fuente_menu.render("Presiona ESPACIO o ENTER para reiniciar", True, BLANCO)
    ganaste_rect = ganaste_texto.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50))
    instrucciones_rect = instrucciones.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 + 50))
    pantalla.blit(ganaste_texto, ganaste_rect)
    pantalla.blit(instrucciones, instrucciones_rect)

def reiniciar_juego():
    global grupo_sprites, grupo_zombies, grupo_balas, jugador, oleada_actual, velocidad_zombies, num_zombies_en_oleada, zombis_eliminados, boss_activo, boss, grupo_proyectiles_boss
    grupo_sprites.empty()
    grupo_zombies.empty()
    grupo_balas.empty()
    grupo_proyectiles_boss.empty()
    jugador = Jugador()
    grupo_sprites.add(jugador)
    oleada_actual = 1
    velocidad_zombies = 1.0
    num_zombies_en_oleada = 5
    zombis_eliminados = 0
    boss_activo = False
    for _ in range(num_zombies_en_oleada):
        nuevo_zombie = Zombie(velocidad_zombies)
        grupo_zombies.add(nuevo_zombie)
        grupo_sprites.add(nuevo_zombie)
    return "JUGANDO"

def juego():
    global grupo_sprites, grupo_zombies, grupo_balas, jugador, oleada_actual, velocidad_zombies, num_zombies_en_oleada, zombis_eliminados, boss_activo, boss, grupo_proyectiles_boss
    grupo_sprites = pygame.sprite.Group()
    grupo_zombies = pygame.sprite.Group()
    grupo_balas = pygame.sprite.Group()
    grupo_proyectiles_boss = pygame.sprite.Group()
    boss_activo = False
    
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
            if estado_juego == "MENU" or estado_juego == "FIN_DEL_JUEGO" or estado_juego == "GANASTE":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                        estado_juego = reiniciar_juego()
                        musica_fondo.play(loops=-1)
            elif estado_juego == "JUGANDO":
                # La condición para disparar se ha simplificado para que funcione en cualquier momento del juego
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    jugador.disparar(grupo_balas)
        
        # Lógica de juego
        if estado_juego == "JUGANDO":
            if boss_activo:
                boss.update(jugador.rect.center)
                grupo_proyectiles_boss.update()
            jugador.mover()
            grupo_balas.update()
            
            # Daño al jefe por colisión con balas
            if boss_activo:
                colisiones_boss = pygame.sprite.spritecollide(boss, grupo_balas, True)
                if colisiones_boss:
                    boss.salud -= len(colisiones_boss)
            
            # Daño al jugador por proyectil del jefe
            if boss_activo and pygame.sprite.spritecollide(jugador, grupo_proyectiles_boss, True):
                jugador.salud -= 10
            
            # Colisión de zombies con el jugador
            if not boss_activo:
                grupo_zombies.update(jugador.rect.center)
                colisiones = pygame.sprite.groupcollide(grupo_zombies, grupo_balas, True, True)
                if colisiones:
                    zombis_eliminados += len(colisiones)
                if pygame.sprite.spritecollide(jugador, grupo_zombies, False):
                    jugador.salud -= 1
            
            # Daño al jugador por colisión con el boss
            if boss_activo and pygame.sprite.collide_rect(jugador, boss):
                jugador.salud -= 40
            
            # Lógica de victoria/derrota
            if jugador.salud <= 0:
                estado_juego = "FIN_DEL_JUEGO"
                musica_fondo.stop()
                if boss_activo: # Se detiene el sonido del boss solo si estaba activo
                    sonido_base_boss.stop()
            elif boss_activo and boss.salud <= 0:
                estado_juego = "GANASTE"
                musica_fondo.stop()
                sonido_base_boss.stop()

            
            # Lógica de oleadas
            if len(grupo_zombies) == 0 and not boss_activo:
                if oleada_actual == 5 and zombis_eliminados == num_zombies_en_oleada:
                    pygame.time.wait(2000)
                    sonido_intro_boss.play()
                    pygame.time.wait(int(sonido_intro_boss.get_length() * 1000))
                    boss = Boss()
                    grupo_sprites.add(boss)
                    sonido_base_boss.play(loops=-1)
                    boss_activo = True
                else:
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
            grupo_proyectiles_boss.draw(pantalla)
            
            mostrar_hud(jugador.salud, oleada_actual, len(grupo_zombies), boss_activo)
        elif estado_juego == "FIN_DEL_JUEGO":
            mostrar_game_over()
        elif estado_juego == "GANASTE":
            mostrar_ganaste()
        
        pygame.display.flip()
        reloj.tick(60)
        
    pygame.quit()

# Iniciar el juego
if __name__ == "__main__":
    juego()