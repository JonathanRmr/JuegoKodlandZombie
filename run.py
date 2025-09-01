import pygame
import random
import math
import time


from player import Jugador, Bala
from zombie import Zombie
from boss import Boss, BossProjectile


pygame.init()
pygame.mixer.init()


PANTALLA_ANCHO = 800
PANTALLA_ALTO = 600
pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("Zombie Survival")


BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)


fuente_titulo = pygame.font.Font(None, 72)
fuente_menu = pygame.font.Font(None, 48)
fuente_hud = pygame.font.Font(None, 36)


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
    jugador = Jugador(sonido_disparo)
    grupo_sprites.add(jugador)
    oleada_actual = 1
    velocidad_zombies = 1.0
    num_zombies_en_oleada = 5
    zombis_eliminados = 0
    boss_activo = False
    for _ in range(num_zombies_en_oleada):
        nuevo_zombie = Zombie(velocidad_zombies, PANTALLA_ANCHO, PANTALLA_ALTO)
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
    
    jugador = Jugador(sonido_disparo)
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
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    jugador.disparar(grupo_balas)
        
        
        if estado_juego == "JUGANDO":
            if boss_activo:
                boss.update(jugador.rect.center)
                grupo_proyectiles_boss.update()
            jugador.mover(PANTALLA_ANCHO, PANTALLA_ALTO)
            grupo_balas.update(PANTALLA_ANCHO, PANTALLA_ALTO)
            
            
            if boss_activo:
                colisiones_boss = pygame.sprite.spritecollide(boss, grupo_balas, True)
                if colisiones_boss:
                    boss.salud -= len(colisiones_boss)
            
           
            if boss_activo and pygame.sprite.spritecollide(jugador, grupo_proyectiles_boss, True):
                jugador.salud -= 10
            
           
            if not boss_activo:
                grupo_zombies.update(jugador.rect.center)
                colisiones = pygame.sprite.groupcollide(grupo_zombies, grupo_balas, True, True)
                if colisiones:
                    zombis_eliminados += len(colisiones)
                if pygame.sprite.spritecollide(jugador, grupo_zombies, False):
                    jugador.salud -= 1
            
           
            if boss_activo and pygame.sprite.collide_rect(jugador, boss):
                jugador.salud -= 40
            
            
            if jugador.salud <= 0:
                estado_juego = "FIN_DEL_JUEGO"
                musica_fondo.stop()
                if boss_activo:
                    sonido_base_boss.stop()
            elif boss_activo and boss.salud <= 0:
                estado_juego = "GANASTE"
                musica_fondo.stop()
                sonido_base_boss.stop()
            
           
            if len(grupo_zombies) == 0 and not boss_activo:
                
                if oleada_actual == 9 and zombis_eliminados == num_zombies_en_oleada:
                    pygame.time.wait(2000)
                    sonido_intro_boss.play()
                    pygame.time.wait(int(sonido_intro_boss.get_length() * 1000))
                    boss = Boss(PANTALLA_ANCHO, PANTALLA_ALTO, grupo_proyectiles_boss)
                    grupo_sprites.add(boss)
                    sonido_base_boss.play(loops=-1)
                    boss_activo = True
                else:
                    zombis_eliminados = 0
                    oleada_actual += 1
                    num_zombies_en_oleada += 3
                    velocidad_zombies += 0.2
                    for _ in range(num_zombies_en_oleada):
                        nuevo_zombie = Zombie(velocidad_zombies, PANTALLA_ANCHO, PANTALLA_ALTO)
                        grupo_zombies.add(nuevo_zombie)
                        grupo_sprites.add(nuevo_zombie)
        
    
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

if __name__ == "__main__":
    juego()