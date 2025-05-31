import pygame
import sys
import random
import time

# --- CONFIGURACIÓN DE PYGAME ---
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 30
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Bynarium Prototipo")
reloj = pygame.time.Clock()
fuente = pygame.font.Font(None, 30)

# --- SIMULACIÓN SIMPLE DE 4 NEURONAS BYNARIUM ---
class NeuronaBynarium:
    def __init__(self, id, bits):
        self.id = id
        self.bits = bits
        self.valor_decimal = 0
        self.max_almacenamiento = self.calcular_max_almacenamiento_simplificado(bits)
        self.activacion = 0
        self.conectada_a = []

    def calcular_max_almacenamiento_simplificado(self, bits):
        # Simulación simplificada del almacenamiento (de 2 en 2)
        if bits == 2: return 1
        elif bits == 3: return 2
        elif bits == 4: return 4
        elif bits == 5: return 6
        return 0

    def recibir_activacion(self):
        if self.activacion < self.bits * 2: # Límite temporal simple
            self.activacion += 1

    def set_valor(self, valor):
        if 0 <= valor <= self.max_almacenamiento:
            self.valor_decimal = valor

    def conectar(self, otra_neurona):
        if otra_neurona not in self.conectada_a:
            self.conectada_a.append(otra_neurona)

    def __repr__(self):
        return f"Neurona(ID={self.id}, Bits={self.bits}, Valor={self.valor_decimal}, Activacion={self.activacion})"

# Crear las 4 neuronas
neurona2 = NeuronaBynarium("N2", 2)
neurona3 = NeuronaBynarium("N3", 3)
neurona4 = NeuronaBynarium("N4", 4)
neurona5 = NeuronaBynarium("N5", 5)

neuronas = {
    "N2": neurona2,
    "N3": neurona3,
    "N4": neurona4,
    "N5": neurona5,
}

# Establecer conexiones simples (por ahora, lineal)
neurona2.conectar(neurona3)
neurona3.conectar(neurona4)
neurona4.conectar(neurona5)

# --- REPRESENTACIÓN VISUAL EN PYGAME ---
class NeuronaVisual:
    def __init__(self, neurona, x, y, color_inactivo):
        self.neurona = neurona
        self.x = x
        self.y = y
        self.radio = neurona.bits * 10  # Radio basado en el número de bits
        self.color_inactivo = color_inactivo
        self.color_activo = VERDE
        self.color_valor = AZUL

    def dibujar(self, superficie):
        color = self.color_inactivo
        if self.neurona.activacion > 0:
            color = self.color_activo
        pygame.draw.circle(superficie, color, (self.x, self.y), self.radio)
        # Mostrar ID
        texto_id = fuente.render(self.neurona.id, True, NEGRO)
        texto_rect_id = texto_id.get_rect(center=(self.x, self.y - self.radio - 15))
        superficie.blit(texto_id, texto_rect_id)
        # Mostrar Valor
        texto_valor = fuente.render(f"V:{self.neurona.valor_decimal}", True, self.color_valor)
        texto_rect_valor = texto_valor.get_rect(center=(self.x, self.y + self.radio + 15))
        superficie.blit(texto_valor, texto_rect_valor)
        # Mostrar Activación
        texto_activacion = fuente.render(f"A:{self.neurona.activacion}", True, ROJO)
        texto_rect_activacion = texto_activacion.get_rect(center=(self.x, self.y + self.radio + 35))
        superficie.blit(texto_activacion, texto_rect_activacion)

# Posicionar las neuronas visualmente
posiciones = {
    "N2": (150, ALTO_PANTALLA // 2),
    "N3": (300, ALTO_PANTALLA // 2),
    "N4": (450, ALTO_PANTALLA // 2),
    "N5": (600, ALTO_PANTALLA // 2),
}

neuronas_visuales = {}
for id, pos in posiciones.items():
    bits = neuronas.get(id).bits
    color = GRIS
    if bits == 2: color = AZUL
    elif bits == 3: color = ROJO
    elif bits == 4: color = AMARILLO
    elif bits == 5: color = VERDE
    neuronas_visuales.update({id: NeuronaVisual(neuronas.get(id), pos [0], pos [1], color)})

# --- BUCLE PRINCIPAL DE PYGAME ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Activar la primera neurona al presionar ESPACIO
                neurona2.recibir_activacion()
            if event.key == pygame.K_v:
                # Establecer valores de demostración
                neurona2.set_valor(1)
                neurona3.set_valor(2)
                neurona4.set_valor(4)
                neurona5.set_valor(6)
            if event.key == pygame.K_c:
                # Simulación simple de propagación (un solo paso)
                for id_origen, neurona_o in neuronas.items():
                    if neurona_o.activacion > 0:
                        neurona_o.activacion -= 1
                        for otra_id in neurona_o.conectada_a:
                            if otra_id in neuronas:
                                neuronas [otra_id].recibir_activacion()

    # --- DIBUJO ---
    pantalla.fill(BLANCO)

    # Dibujar conexiones
    for id_origen, neurona_o in neuronas.items():
        if id_origen in neuronas_visuales:
            inicio = (neuronas_visuales [id_origen].x, neuronas_visuales [id_origen].y)
            for id_destino in neurona_o.conectada_a:
                if id_destino in neuronas_visuales:
                    fin = (neuronas_visuales [id_destino].x, neuronas_visuales [id_destino].y)
                    pygame.draw.line(pantalla, GRIS, inicio, fin, 3)

    # Dibujar neuronas
    for visual_neurona in neuronas_visuales.values():
        visual_neurona.dibujar(pantalla)

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
sys.exit()
