import pygame
import sys
import random
import time
import math # Necesario para calcular distancia en el tooltip

# --- CONFIGURACIÓN DE PYGAME ---
ANCHO_PANTALLA = 1000 # Aumentado para acomodar más neuronas
ALTO_PANTALLA = 700  # Aumentado
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
pygame.display.set_caption("Bynarium Prototipo Extendido")
reloj = pygame.time.Clock()
fuente = pygame.font.Font(None, 30)
fuente_pequena = pygame.font.Font(None, 20)
fuente_tooltip = pygame.font.Font(None, 22)

# --- DESCRIPCIONES DE NEURONAS PARA TOOLTIP ---
NEURON_DESCRIPTIONS = {
    "NS": "Sensor",
    "NA": "Análisis",
    "NP": "Profundidad y Contexto",
    "NM": "Memoria"
}

# --- SIMULACIÓN BYNARIUM ---
class NeuronaBynarium:
    def __init__(self, id, bits):
        self.id = id # Ej: "NS1", "NA1"
        self.tipo = id[:2] # Ej: "NS", "NA"
        self.bits = bits
        self.valor_decimal = 0
        self.max_almacenamiento = self.calcular_max_almacenamiento_simplificado(bits)
        self.activacion = 0
        self.conectada_a = [] # Almacena objetos NeuronaBynarium

    def calcular_max_almacenamiento_simplificado(self, bits):
        # Simulación simplificada del almacenamiento
        if bits == 2: return 1
        elif bits == 3: return 2
        elif bits == 4: return 4
        elif bits == 5: return 6
        elif bits == 6: return 9 # Un ejemplo para demostrar que no es lineal 2 en 2
        return 0

    def recibir_activacion(self):
        if self.activacion < self.max_almacenamiento:
            self.activacion += 1
            return True
        return False

    def set_valor(self, valor):
        if 0 <= valor <= self.max_almacenamiento:
            self.valor_decimal = valor
            return True
        return False

    def conectar(self, otra_neurona):
        if otra_neurona not in self.conectada_a:
            self.conectada_a.append(otra_neurona)

    def __repr__(self):
        return f"Neurona(ID={self.id}, Tipo={self.tipo}, Bits={self.bits}, Valor={self.valor_decimal}, Act={self.activacion})"

# --- CREAR Y CONECTAR NEURONAS ---
# 4 NS (bits=2)
ns1 = NeuronaBynarium("NS1", 2)
ns2 = NeuronaBynarium("NS2", 2)
ns3 = NeuronaBynarium("NS3", 2)
ns4 = NeuronaBynarium("NS4", 2)

# 2 NA (bits=3)
na1 = NeuronaBynarium("NA1", 3)
na2 = NeuronaBynarium("NA2", 3)

# 1 NP (bits=4)
np1 = NeuronaBynarium("NP1", 4)

# 2 NM (bits=5 y 6, para variar)
nm1 = NeuronaBynarium("NM1", 5) # Memoria 1
nm2 = NeuronaBynarium("NM2", 6) # Memoria 2 (con max_almacenamiento 9)

neuronas = {
    "NS1": ns1, "NS2": ns2, "NS3": ns3, "NS4": ns4,
    "NA1": na1, "NA2": na2,
    "NP1": np1,
    "NM1": nm1, "NM2": nm2
}

# Conexiones (unidireccionales)
# 4 NS -> 2 NA
ns1.conectar(na1); ns1.conectar(na2)
ns2.conectar(na1); ns2.conectar(na2)
ns3.conectar(na1); ns3.conectar(na2)
ns4.conectar(na1); ns4.conectar(na2)

# 2 NA -> 1 NP
na1.conectar(np1)
na2.conectar(np1)

# NM1 conectado a NA1 y NP1 (interpretado como NA1 -> NM1, NP1 -> NM1)
na1.conectar(nm1)
np1.conectar(nm1)

# NM2 conectado a los 4 NS y NA2 (interpretado como NSx -> NM2, NA2 -> NM2)
ns1.conectar(nm2)
ns2.conectar(nm2)
ns3.conectar(nm2)
ns4.conectar(nm2)
na2.conectar(nm2)


# --- REPRESENTACIÓN VISUAL EN PYGAME ---
class NeuronaVisual:
    def __init__(self, neurona, x, y, color_inactivo):
        self.neurona = neurona
        self.x = x
        self.y = y
        self.radio = neurona.bits * 7  # Radio basado en el número de bits, ajustado
        self.color_inactivo = color_inactivo
        self.color_activo = VERDE
        self.color_valor = AZUL
        self.color_max_almacenamiento = PURPURA

        self.flash_start_time = 0
        self.flash_duration = 0.2
        self.flash_color = AMARILLO

    def trigger_flash(self):
        self.flash_start_time = time.time()

    def dibujar(self, superficie):
        current_time = time.time()
        is_flashing = (current_time - self.flash_start_time) < self.flash_duration

        color_base = self.color_inactivo
        if self.neurona.activacion > 0:
            color_base = self.color_activo
        
        display_color = self.flash_color if is_flashing else color_base

        pygame.draw.circle(superficie, display_color, (self.x, self.y), self.radio)
        pygame.draw.circle(superficie, NEGRO, (self.x, self.y), self.radio, 2)

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

# Posicionar las neuronas visualmente (ajustado para más espacio)
posiciones = {
    "NS1": (100, 150), "NS2": (100, 300), "NS3": (100, 450), "NS4": (100, 600),
    "NA1": (350, 250), "NA2": (350, 500),
    "NP1": (600, 375),
    "NM1": (850, 200), "NM2": (850, 550)
}

neuronas_visuales = {}
for id, pos in posiciones.items():
    neurona_obj = neuronas.get(id)
    color = GRIS
    if neurona_obj.tipo == "NS": color = AZUL
    elif neurona_obj.tipo == "NA": color = ROJO
    elif neurona_obj.tipo == "NP": color = NARANJA
    elif neurona_obj.tipo == "NM": color = CIAN
    neuronas_visuales.update({id: NeuronaVisual(neurona_obj, pos[0], pos[1], color)})

# --- FUNCIONES DE AYUDA ---
def dibujar_tooltip(superficie, mouse_pos, neurona_visual_obj):
    tooltip_text = f"{neurona_visual_obj.neurona.id}: {NEURON_DESCRIPTIONS[neurona_visual_obj.neurona.tipo]}"
    texto_tooltip = fuente_tooltip.render(tooltip_text, True, BLANCO)
    
    # Calcular tamaño del fondo del tooltip
    padding = 10
    tooltip_width = texto_tooltip.get_width() + 2 * padding
    tooltip_height = texto_tooltip.get_height() + 2 * padding
    
    # Posicionar tooltip (encima y a la derecha del cursor)
    tooltip_x = mouse_pos[0] + 15
    tooltip_y = mouse_pos[1] - tooltip_height - 5
    
    # Ajustar si se sale de la pantalla
    if tooltip_x + tooltip_width > ANCHO_PANTALLA:
        tooltip_x = ANCHO_PANTALLA - tooltip_width - 5
    if tooltip_y < 0:
        tooltip_y = mouse_pos[1] + 15 # Debajo del cursor si no cabe arriba

    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    
    pygame.draw.rect(superficie, NEGRO, tooltip_rect, 0, 5) # Fondo negro con bordes redondeados
    pygame.draw.rect(superficie, GRIS, tooltip_rect, 2, 5) # Borde gris
    superficie.blit(texto_tooltip, (tooltip_x + padding, tooltip_y + padding))

# --- BUCLE PRINCIPAL DE PYGAME ---
running = True
while running:
    # Reiniciar la lista de neuronas a propagar en cada fotograma
    # Esto es una lista de IDs de neuronas que tienen activación y que pueden propagar
    active_neurons_for_propagation = [n for n in neuronas.values() if n.activacion > 0]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Activar una NS aleatoria para iniciar el proceso
                random_ns = random.choice([ns1, ns2, ns3, ns4])
                if random_ns.recibir_activacion():
                    neuronas_visuales[random_ns.id].trigger_flash()
            if event.key == pygame.K_v:
                # Establecer valores de demostración y hacer que parpadeen
                for neurona_obj in neuronas.values():
                    # Valores arbitrarios para demostración
                    random_val = random.randint(1, neurona_obj.max_almacenamiento)
                    if neurona_obj.set_valor(random_val):
                        neuronas_visuales[neurona_obj.id].trigger_flash()
            if event.key == pygame.K_c:
                # Simulación de propagación de 1 en 1
                neurons_to_process_this_step = list(active_neurons_for_propagation) # Tomar una instantánea
                
                for neurona_o in neurons_to_process_this_step:
                    if neurona_o.activacion > 0:
                        neurona_o.activacion -= 1 # La neurona origen "gasta" una activación
                        neuronas_visuales[neurona_o.id].trigger_flash() # Origen parpadea al enviar

                        posibles_destinos = []
                        if neurona_o.tipo == "NS":
                            # NS puede propagar a NA o NM
                            targets_na = [n for n in neurona_o.conectada_a if n.tipo == "NA"]
                            targets_nm = [n for n in neurona_o.conectada_a if n.tipo == "NM"]
                            posibles_destinos = targets_na + targets_nm
                        elif neurona_o.tipo == "NA":
                            # NA puede propagar a NP o NM
                            targets_np = [n for n in neurona_o.conectada_a if n.tipo == "NP"]
                            targets_nm = [n for n in neurona_o.conectada_a if n.tipo == "NM"]
                            posibles_destinos = targets_np + targets_nm
                        elif neurona_o.tipo == "NP":
                            # NP solo propaga a NM en este modelo
                            targets_nm = [n for n in neurona_o.conectada_a if n.tipo == "NM"]
                            posibles_destinos = targets_nm
                        # Otras neuronas (NM) no propagan en este modelo simple (son terminales)
                        
                        # Elegir hasta 2 caminos aleatorios si hay destinos posibles
                        if posibles_destinos:
                            # Asegurarse de elegir destinos únicos
                            num_choices = min(2, len(posibles_destinos))
                            destinos_elegidos = random.sample(posibles_destinos, num_choices)
                            
                            for otra_neurona_obj in destinos_elegidos:
                                if otra_neurona_obj.recibir_activacion(): # Si la destino puede recibir
                                    neuronas_visuales[otra_neurona_obj.id].trigger_flash() # Destino parpadea al recibir
            if event.key == pygame.K_r: # Reset con tecla R
                for neurona_obj in neuronas.values():
                    neurona_obj.activacion = 0
                    neurona_obj.valor_decimal = 0
                    neuronas_visuales[neurona_obj.id].trigger_flash()

    # --- DIBUJO ---
    pantalla.fill(BLANCO)

    # Dibujar conexiones
    for id_origen, neurona_o in neuronas.items():
        if id_origen in neuronas_visuales:
            inicio = (neuronas_visuales[id_origen].x, neuronas_visuales[id_origen].y)
            for neurona_destino_obj in neurona_o.conectada_a:
                id_destino = neurona_destino_obj.id
                if id_destino in neuronas_visuales:
                    fin = (neuronas_visuales[id_destino].x, neuronas_visuales[id_destino].y)
                    pygame.draw.line(pantalla, GRIS, inicio, fin, 3)

    # Dibujar neuronas
    hovered_neuron_visual = None
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for visual_neurona in neuronas_visuales.values():
        visual_neurona.dibujar(pantalla)
        # Verificar si el cursor está sobre esta neurona para el tooltip
        dist_a_neurona = math.hypot(mouse_x - visual_neurona.x, mouse_y - visual_neurona.y)
        if dist_a_neurona <= visual_neurona.radio:
            hovered_neuron_visual = visual_neurona
    
    # Dibujar tooltip si hay una neurona bajo el cursor
    if hovered_neuron_visual:
        dibujar_tooltip(pantalla, (mouse_x, mouse_y), hovered_neuron_visual)

    # Indicar al usuario qué teclas usar (en pantalla)
    texto_ayuda = fuente_pequena.render("ESPACIO: Activar NS aleatoria | V: Set valores | C: Propagar 1 paso | R: Reset", True, NEGRO)
    pantalla.blit(texto_ayuda, (20, 20))

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
sys.exit()
