import pygame
pygame.init()

# Crear ventana
pantalla = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Test de Pygame")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

# Bucle principal
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    pantalla.fill(NEGRO)
    pygame.draw.circle(pantalla, BLANCO, (200, 150), 50)
    pygame.display.flip()

pygame.quit()
