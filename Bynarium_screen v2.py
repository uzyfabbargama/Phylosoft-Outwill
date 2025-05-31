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
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
CIAN = (0, 255, 255)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Bynarium Prototipo")
reloj = pygame.time.Clock()
fuente = pygame.font.Font(None, 30)
fuente_pequena = pygame.font.Font(None, 20) # Fuente más pequeña para info detallada

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
        # La regla de la sumatoria real se implementaría aquí para mayor precisión
        if bits == 2: return 1
        elif bits == 3: return 2
        elif bits == 4: return 4
        elif bits == 5: return 6
        return 0

    def recibir_activacion(self):
        # Limitar la activación a la capacidad máxima
        if self.activacion < self.max_almacenamiento:
            self.activacion += 1
            return True # Indica que se activó
        return False # Indica que no se pudo activar (ya estaba llena)

    def set_valor(self, valor):
        if 0 <= valor <= self.max_almacenamiento:
            self.valor_decimal = valor
            return True
        return False

    def conectar(self, otra_neurona):
        if otra_neurona not in self.conectada_a:
            self.conectada_a.append(otra_neurona)

    def __repr__(self):
        return f"Neurona(ID={self.id}, Bits={self.bits}, Valor={self.valor_decimal}, Activacion={self.activacion})"

# Crear las 4 neuronas con nombres simbólicos
neurona_sensor = NeuronaBynarium("NS", 2)
neurona_analisis = NeuronaBynarium("NA", 3)
neurona_profundo = NeuronaBynarium("NP", 4)
neurona_memoria = NeuronaBynarium("NM", 5)

neuronas = {
    "NS": neurona_sensor,
    "NA": neurona_analisis,
    "NP": neurona_profundo,
    "NM": neurona_memoria,
}

# Establecer conexiones simples (por ahora, lineal)
neurona_sensor.conectar(neurona_analisis)
neurona_analisis.conectar(neurona_profundo)
neurona_profundo.conectar(neurona_memoria)

# --- REPRESENTACIÓN VISUAL EN PYGAME ---
class NeuronaVisual:
    def __init__(self, neurona, x, y, color_inactivo):
        self.neurona = neurona
        self.x = x
        self.y = y
        self.radio = neurona.bits * 8  # Radio basado en el número de bits, ajustado para espacio
        self.color_inactivo = color_inactivo
        self.color_activo = VERDE
        self.color_valor = AZUL
        self.color_max_almacenamiento = PURPURA # Nuevo color para max_almacenamiento

        self.flash_start_time = 0 # Tiempo en que comenzó el parpadeo
        self.flash_duration = 0.2 # Duración del parpadeo en segundos
        self.flash_color = AMARILLO # Color del parpadeo

    def trigger_flash(self):
        self.flash_start_time = time.time()

    def dibujar(self, superficie):
        current_time = time.time()
        is_flashing = (current_time - self.flash_start_time) < self.flash_duration

        # Determinar el color base
        color_base = self.color_inactivo
        if self.neurona.activacion > 0:
            color_base = self.color_activo
        
        # Aplicar parpadeo si está activo
        if is_flashing:
            display_color = self.flash_color
        else:
            display_color = color_base

        pygame.draw.circle(superficie, display_color, (self.x, self.y), self.radio)
        pygame.draw.circle(superficie, NEGRO, (self.x, self.y), self.radio, 2) # Borde negro

        # Mostrar ID
        texto_id = fuente.render(self.neurona.id, True, NEGRO)
        texto_rect_id = texto_id.get_rect(center=(self.x, self.y - self.radio - 20))
        superficie.blit(texto_id, texto_rect_id)

        # Mostrar Valor
        texto_valor = fuente_pequena.render(f"V:{self.neurona.valor_decimal}", True, self.color_valor)
        texto_rect_valor = texto_valor.get_rect(center=(self.x, self.y + self.radio + 10))
        superficie.blit(texto_valor, texto_rect_valor)

        # Mostrar Activación
        texto_activacion = fuente_pequena.render(f"A:{self.neurona.activacion}", True, ROJO)
        texto_rect_activacion = texto_activacion.get_rect(center=(self.x, self.y + self.radio + 25))
        superficie.blit(texto_activacion, texto_rect_activacion)

        # Mostrar Max Almacenamiento
        texto_max = fuente_pequena.render(f"M:{self.neurona.max_almacenamiento}", True, self.color_max_almacenamiento)
        texto_rect_max = texto_max.get_rect(center=(self.x, self.y + self.radio + 40))
        superficie.blit(texto_max, texto_rect_max)


# Posicionar las neuronas visualmente con los nuevos IDs
posiciones = {
    "NS": (150, ALTO_PANTALLA // 2),
    "NA": (300, ALTO_PANTALLA // 2),
    "NP": (450, ALTO_PANTALLA // 2),
    "NM": (600, ALTO_PANTALLA // 2),
}

neuronas_visuales = {}
for id, pos in posiciones.items():
    bits = neuronas.get(id).bits
    color = GRIS # Color por defecto
    if id == "NS": color = AZUL
    elif id == "NA": color = ROJO
    elif id == "NP": color = NARANJA # Cambiado para más variedad
    elif id == "NM": color = CIAN # Cambiado para más variedad
    neuronas_visuales.update({id: NeuronaVisual(neuronas.get(id), pos[0], pos[1], color)})

# --- BUCLE PRINCIPAL DE PYGAME ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Activar la primera neurona al presionar ESPACIO
                if neurona_sensor.recibir_activacion():
                    neuronas_visuales["NS"].trigger_flash()
            if event.key == pygame.K_v:
                # Establecer valores de demostración y hacer que parpadeen
                if neurona_sensor.set_valor(1): neuronas_visuales["NS"].trigger_flash()
                if neurona_analisis.set_valor(2): neuronas_visuales["NA"].trigger_flash()
                if neurona_profundo.set_valor(4): neuronas_visuales["NP"].trigger_flash()
                if neurona_memoria.set_valor(6): neuronas_visuales["NM"].trigger_flash()
            if event.key == pygame.K_c:
                # Simulación simple de propagación (un solo paso)
                for id_origen, neurona_o in neuronas.items():
                    if neurona_o.activacion > 0:
                        neurona_o.activacion -= 1 # La neurona origen "gasta" una activación
                        neuronas_visuales[id_origen].trigger_flash() # Origen parpadea al enviar
                        for otra_neurona_obj in neurona_o.conectada_a: # Conectada_a ahora tiene objetos
                            if otra_neurona_obj.recibir_activacion(): # Si la destino puede recibir
                                neuronas_visuales[otra_neurona_obj.id].trigger_flash() # Destino parpadea al recibir
            if event.key == pygame.K_r: # Nuevo: Reset con tecla R
                for neurona_obj in neuronas.values():
                    neurona_obj.activacion = 0
                    neurona_obj.valor_decimal = 0
                    neuronas_visuales[neurona_obj.id].trigger_flash() # Parpadea al resetear

    # --- DIBUJO ---
    pantalla.fill(BLANCO)

    # Dibujar conexiones
    for id_origen, neurona_o in neuronas.items():
        if id_origen in neuronas_visuales:
            inicio = (neuronas_visuales[id_origen].x, neuronas_visuales[id_origen].y)
            for neurona_destino_obj in neurona_o.conectada_a: # Iterar sobre objetos de neurona
                id_destino = neurona_destino_obj.id # Obtener ID del objeto
                if id_destino in neuronas_visuales:
                    fin = (neuronas_visuales[id_destino].x, neuronas_visuales[id_destino].y)
                    pygame.draw.line(pantalla, GRIS, inicio, fin, 3)

    # Dibujar neuronas
    for visual_neurona in neuronas_visuales.values():
        visual_neurona.dibujar(pantalla)

    # Indicar al usuario qué teclas usar (en pantalla)
    texto_ayuda = fuente_pequena.render("ESPACIO: Activar NS | V: Set valores | C: Propagar | R: Reset", True, NEGRO)
    pantalla.blit(texto_ayuda, (20, 20))

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
sys.exit()
