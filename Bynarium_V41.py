import pygame
import sys
import random
import time
import math
import json
import os 

# --- CONFIGURACIÓN DE PYGAME ---
ANCHO_PANTALLA = 1000
ALTO_PANTALLA = 700
FPS = 30
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0) # Rojo + Verde
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
CIAN = (0, 255, 255) # Azul + Verde
BLANCO_APAGADO = (240, 240, 240) # Para el fondo del input
global neuronas, neuronas_visuales
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Bynarium Prototipo Extendido y Creador")
reloj = pygame.time.Clock()
fuente = pygame.font.Font(None, 30)
fuente_pequena = pygame.font.Font(None, 20)
fuente_tooltip = pygame.font.Font(None, 22)
fuente_grande = pygame.font.Font(None, 40)

# --- ESTADOS DE PANTALLA ---
SCREEN_NETWORK = 0
SCREEN_CREATOR = 1
current_screen = SCREEN_NETWORK

# --- VARIABLES DE ZOOM Y PANNING ---
zoom_level = 1.0
offset_x = 0
offset_y = 0
panning_active = False
pan_start_mouse_x, pan_start_mouse_y = 0, 0
pan_start_offset_x, pan_start_offset_y = 0, 0

# --- DESCRIPCIONES DE NEURONAS PARA TOOLTIP ---
NEURON_DESCRIPTIONS = {
    "NS": "Sensor",
    "NA": "Análisis",
    "NP": "Profundidad y Contexto",
    "NM": "Memoria"
}

# --- FUNCIONES DE SUMATORIA ---
def calcular_sumatoria_serie(limite_n):
    """
    Calcula la sumatoria de una serie (pares o impares) hasta el limite_n.
    Este 'limite_n' es el valor que se pasa a las fórmulas.
    """
    if limite_n <= 0:
        return 0 

    if limite_n % 2 == 0:  # Si el límite es par
        return limite_n * ((limite_n + 2) / 4)
    else:  # Si el límite es impar
        return ((limite_n + 1) / 2) ** 2

def generar_sumatoria_str(limite_n):
    """
    Genera la representación en cadena de la sumatoria de una serie (pares o impares)
    hasta el limite_n, para mostrarla simbólicamente.
    """
    if limite_n <= 0:
        return "0"

    serie_elementos = []
    if limite_n % 2 == 0:  # Serie de pares
        for i in range(2, limite_n + 1, 2):
            serie_elementos.append(str(i))
    else:  # Serie de impares
        for i in range(1, limite_n + 1, 2):
            serie_elementos.append(str(i))
    
    return "+".join(serie_elementos)

# --- SIMULACIÓN BYNARIUM ---
class NeuronaBynarium:
    def __init__(self, id, bits, valor_decimal=0, activacion=0, hi_score_activaciones=0, vida_util_restante=None):
        self.id = id 
        self.tipo = id[:2] 
        self.bits = bits
        self.valor_decimal = valor_decimal
        
        # Calcular max_almacenamiento usando la regla de sumatoria
        formula_limit_n = bits - 1
        if formula_limit_n < 0:
            formula_limit_n = 0
        self.max_almacenamiento = int(calcular_sumatoria_serie(formula_limit_n))
        
        self.activacion = activacion
        self.conectada_a = [] 
        self.conectada_desde = [] 
        
        self.hi_score_activaciones = hi_score_activaciones 

        # Lógica para vida_util_restante (resistencia/vida útil)
        # Si no se proporciona en el constructor (ej. al cargar), calcularla
        if vida_util_restante is None:
            self.vida_util_restante = abs(20 - self.bits) 
            if self.vida_util_restante == 0:
                self.vida_util_restante = 1
        else:
            self.vida_util_restante = vida_util_restante

    def recibir_activacion(self):
        if self.activacion < self.max_almacenamiento:
            self.activacion += 1
            self.hi_score_activaciones += 1 
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
            otra_neurona.conectada_desde.append(self) 
            return True
        return False 
    
    def desconectar(self, otra_neurona):
        if otra_neurona in self.conectada_a:
            self.conectada_a.remove(otra_neurona)
            otra_neurona.conectada_desde.remove(self)
            return True
        return False

    def __repr__(self):
        return f"Neurona(ID={self.id}, Tipo={self.tipo}, Bits={self.bits}, Valor={self.valor_decimal}, Act={self.activacion}, HiScore={self.hi_score_activaciones}, Vida={self.vida_util_restante})"

# --- FUNCIÓN PARA CALCULAR EL COLOR DE LA NEURONA SEGÚN LAS REGLAS ---
def get_neuron_color(bits):
    r, g, b = 0, 0, 0 

    # Colores base: par es rojo, impar es azul
    if bits % 2 == 0: # Par
        r = 255
        r = max(0, 255 - ((bits // 2) - 1) * 5)
    else: # Impar
        b = 255
        b = max(0, 255 - (((bits - 1) // 2) - 1) * 5)

    # Múltiplo de 3 es verde (se combina con el color base)
    if bits % 3 == 0:
        g = 255 

    r = min(255, max(0, r))
    g = min(255, max(0, g))
    b = min(255, max(0, b))

    return (r, g, b)


# --- REPRESENTACIÓN VISUAL EN PYGAME ---
class NeuronaVisual:
    def __init__(self, neurona, x, y, color_inactivo):
        self.neurona = neurona
        self.x = x
        self.y = y
        self.radio = neurona.bits * 7  
        self.color_inactivo = color_inactivo
        self.color_activo = VERDE
        self.color_valor = AZUL
        self.color_max_almacenamiento = PURPURA
        self.color_seleccion = AMARILLO 

        self.flash_start_time = 0
        self.flash_duration = 0.2
        self.flash_color = AMARILLO
        
    def trigger_flash(self): # <--- ¡Añade esta función de nuevo!
        self.flash_start_time = time.time()

    def dibujar(self, superficie, zoom, offset_x, offset_y, is_selected=False, is_dragging=False, is_delete_mode=False, is_rename_mode=False, is_disconnect_mode=False):
        current_time = time.time()
        is_flashing = (current_time - self.flash_start_time) < self.flash_duration

        color_base = self.color_inactivo
        if self.neurona.hi_score_activaciones > (self.neurona.max_almacenamiento * 0.7):
             color_base = NARANJA 
        if self.neurona.vida_util_restante <= 1: 
            color_base = (min(255, color_base[0] + 50), color_base[1], color_base[2]) 
        elif self.neurona.activacion > 0: 
            color_base = self.color_activo
        
        display_color = self.flash_color if is_flashing else color_base
        
        if is_delete_mode:
            display_color = ROJO 
        elif is_rename_mode: # Color especial para neurona seleccionada en modo renombrar
            display_color = PURPURA
        elif is_disconnect_mode: # Color especial para neurona seleccionada en modo desconectar
            display_color = CIAN


        # Aplicar zoom y offset para dibujar
        draw_x = int((self.x + offset_x) * zoom)
        draw_y = int((self.y + offset_y) * zoom)
        scaled_radio = int(self.radio * zoom)


        pygame.draw.circle(superficie, display_color, (draw_x, draw_y), scaled_radio)
        pygame.draw.circle(superficie, NEGRO, (draw_x, draw_y), scaled_radio, 2) 

        if is_selected: 
            pygame.draw.circle(superficie, self.color_seleccion, (draw_x, draw_y), scaled_radio + int(5 * zoom), int(3 * zoom))
        if is_dragging: 
            pygame.draw.circle(superficie, CIAN, (draw_x, draw_y), scaled_radio + int(5 * zoom), int(3 * zoom))


        # Ajustar tamaño de fuente con el zoom, pero dentro de límites razonables
        # Para que el texto no se vea demasiado grande o pequeño
        scaled_font_size = max(10, int(30 * zoom))
        scaled_font_pequena_size = max(8, int(20 * zoom))
        
        # Recargar fuentes para que el tamaño sea dinámico
        dynamic_fuente = pygame.font.Font(None, scaled_font_size)
        dynamic_fuente_pequena = pygame.font.Font(None, scaled_font_pequena_size)


        texto_id = dynamic_fuente.render(self.neurona.id, True, NEGRO)
        texto_rect_id = texto_id.get_rect(center=(draw_x, draw_y - scaled_radio - int(20 * zoom)))
        superficie.blit(texto_id, texto_rect_id)

        texto_valor = dynamic_fuente_pequena.render(f"V:{self.neurona.valor_decimal}", True, self.color_valor)
        texto_rect_valor = texto_valor.get_rect(center=(draw_x, draw_y + scaled_radio + int(10 * zoom)))
        superficie.blit(texto_valor, texto_rect_valor)

        texto_activacion = dynamic_fuente_pequena.render(f"A:{self.neurona.activacion}", True, ROJO)
        texto_rect_activacion = texto_activacion.get_rect(center=(draw_x, draw_y + scaled_radio + int(25 * zoom)))
        superficie.blit(texto_activacion, texto_rect_activacion)

        texto_max = dynamic_fuente_pequena.render(f"M:{self.neurona.max_almacenamiento}", True, self.color_max_almacenamiento)
        texto_rect_max = texto_max.get_rect(center=(draw_x, draw_y + scaled_radio + int(40 * zoom)))
        superficie.blit(texto_max, texto_rect_max)

        texto_hi_score = dynamic_fuente_pequena.render(f"HS:{self.neurona.hi_score_activaciones}", True, NARANJA)
        texto_rect_hi_score = texto_hi_score.get_rect(center=(draw_x, draw_y + scaled_radio + int(55 * zoom)))
        superficie.blit(texto_hi_score, texto_rect_hi_score)

        texto_vida_util = dynamic_fuente_pequena.render(f"VU:{self.neurona.vida_util_restante}", True, CIAN) 
        texto_rect_vida_util = texto_vida_util.get_rect(center=(draw_x, draw_y + scaled_radio + int(70 * zoom))) 
        pantalla.blit(texto_vida_util, texto_rect_vida_util)


# --- CREAR Y CONECTAR NEURONAS INICIALES ---
neuronas = {}
neuronas_visuales = {}

def inicializar_red_predeterminada():
    global neuronas, neuronas_visuales
    neuronas.clear()
    neuronas_visuales.clear()

    ns1 = NeuronaBynarium("NS1", 2)
    ns2 = NeuronaBynarium("NS2", 2)
    ns3 = NeuronaBynarium("NS3", 2)
    ns4 = NeuronaBynarium("NS4", 2)

    na1 = NeuronaBynarium("NA1", 3)
    na2 = NeuronaBynarium("NA2", 3)

    np1 = NeuronaBynarium("NP1", 4)

    nm1 = NeuronaBynarium("NM1", 5) 
    nm2 = NeuronaBynarium("NM2", 6) 

    neuronas = {
        "NS1": ns1, "NS2": ns2, "NS3": ns3, "NS4": ns4,
        "NA1": na1, "NA2": na2,
        "NP1": np1,
        "NM1": nm1, "NM2": nm2
    }

    ns1.conectar(na1); ns1.conectar(na2)
    ns2.conectar(na1); ns2.conectar(na2)
    ns3.conectar(na1); ns3.conectar(na2)
    ns4.conectar(na1); ns4.conectar(na2)

    na1.conectar(np1)
    na2.conectar(np1)

    na1.conectar(nm1)
    np1.conectar(nm1)

    ns1.conectar(nm2)
    ns2.conectar(nm2)
    ns3.conectar(nm2)
    ns4.conectar(nm2)
    na2.conectar(nm2)

    posiciones = {
        "NS1": (100, 150), "NS2": (100, 300), "NS3": (100, 450), "NS4": (100, 600),
        "NA1": (350, 250), "NA2": (350, 500),
        "NP1": (600, 375),
        "NM1": (850, 200), "NM2": (850, 550)
    }

    for id, pos in posiciones.items():
        neurona_obj = neuronas.get(id)
        initial_color = get_neuron_color(neurona_obj.bits) 
        neuronas_visuales.update({id: NeuronaVisual(neurona_obj, pos[0], pos[1], initial_color)})

inicializar_red_predeterminada() 

# --- FUNCIONES DE AYUDA ---
def dibujar_tooltip(superficie, mouse_pos, neurona_visual_obj):
    tooltip_text = f"{neurona_visual_obj.neurona.id}: {NEURON_DESCRIPTIONS.get(neurona_visual_obj.neurona.tipo, 'Desconocido')}"
    if neurona_visual_obj.neurona.bits > 0:
        tooltip_text += f"\nBits: {neurona_visual_obj.neurona.bits}"
        tooltip_text += f"\nMax Almacenamiento: {neurona_visual_obj.neurona.max_almacenamiento}"
        formula_limit_n = neurona_visual_obj.neurona.bits - 1
        if formula_limit_n < 0: formula_limit_n = 0
        tooltip_text += f"\nFórmula: Σ({generar_sumatoria_str(formula_limit_n)})"
        tooltip_text += f"\nFatiga (HS): {neurona_visual_obj.neurona.hi_score_activaciones}"
        tooltip_text += f"\nVida Útil (VU): {neurona_visual_obj.neurona.vida_util_restante}"


    lines = tooltip_text.split('\n')
    max_width = max(fuente_tooltip.render(line, True, BLANCO).get_width() for line in lines)
    
    padding = 10
    tooltip_width = max_width + 2 * padding
    tooltip_height = len(lines) * fuente_tooltip.get_height() + 2 * padding
    
    tooltip_x = mouse_pos[0] + 15
    tooltip_y = mouse_pos[1] - tooltip_height - 5
    
    if tooltip_x + tooltip_width > ANCHO_PANTALLA:
        tooltip_x = ANCHO_PANTALLA - tooltip_width - 5
    if tooltip_y < 0:
        tooltip_y = mouse_pos[1] + 15

    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    
    pygame.draw.rect(superficie, NEGRO, tooltip_rect, 0, 5)
    pygame.draw.rect(superficie, GRIS, tooltip_rect, 2, 5)
    
    for i, line in enumerate(lines):
        text_surface = fuente_tooltip.render(line, True, BLANCO)
        superficie.blit(text_surface, (tooltip_x + padding, tooltip_y + padding + i * fuente_tooltip.get_height()))

# --- FUNCIONES DE GUARDAR Y CARGAR ---
# Ruta absoluta para el directorio de guardado
SAVE_DIR = r"C:\BynariumData\bynarium_saves" # Usar r"" para raw string y evitar problemas con backslashes
SAVE_FILENAME = "red_bynarium.json"
FULL_SAVE_PATH = os.path.join(SAVE_DIR, SAVE_FILENAME)

# --- DEBUGGING INICIO ---
print(f"DEBUG: SCRIPT_DIR: {os.path.dirname(os.path.abspath(__file__))}") 
print(f"DEBUG: CURRENT_WORKING_DIR: {os.getcwd()}")
print(f"DEBUG: SAVE_DIR: {SAVE_DIR}")
print(f"DEBUG: FULL_SAVE_PATH: {FULL_SAVE_PATH}")
# --- FIN DEBUGGING INICIO ---

def guardar_red():
    # Paso 1: Asegurarse de que la carpeta de guardado exista
    try:
        print(f"DEBUG: Verificando/Creando directorio: '{SAVE_DIR}'")
        os.makedirs(SAVE_DIR, exist_ok=True)
        print(f"DEBUG: Directorio '{SAVE_DIR}' existe o fue creado exitosamente.")
        
        # Añadir un pequeño retraso para asegurar que el sistema de archivos esté listo
        time.sleep(0.1) 
        
        # Verificar de nuevo si el directorio existe y es un directorio
        if not os.path.isdir(SAVE_DIR):
            error_msg = f"ERROR CRÍTICO: El directorio '{SAVE_DIR}' no se encontró o no es un directorio válido después de la creación."
            print(error_msg)
            return False, f"Error al verificar la carpeta de guardado."

    except Exception as e:
        error_msg = f"ERROR CRÍTICO: Falló al asegurar/crear el directorio '{SAVE_DIR}': {e}"
        print(error_msg)
        return False, f"Error al preparar guardado: {e}"
    
    # Paso 2: Preparar los datos a guardar
    data_to_save = []
    for id, neurona_obj in neuronas.items():
        visual_obj = neuronas_visuales.get(id)
        if visual_obj:
            connected_to_ids = [n.id for n in neurona_obj.conectada_a]
            
            data_to_save.append({
                "id": neurona_obj.id,
                "bits": neurona_obj.bits,
                "valor_decimal": neurona_obj.valor_decimal,
                "activacion": neurona_obj.activacion,
                "hi_score_activaciones": neurona_obj.hi_score_activaciones,
                "vida_util_restante": neurona_obj.vida_util_restante,
                "pos_x": visual_obj.x,
                "pos_y": visual_obj.y,
                "conectada_a_ids": connected_to_ids 
            })
    
    # Paso 3: Intentar guardar el archivo
    try:
        print(f"Intentando guardar el archivo en '{FULL_SAVE_PATH}'...")
        with open(FULL_SAVE_PATH, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Éxito: Red guardada en '{FULL_SAVE_PATH}'.")
        return True, f"Red guardada en '{os.path.basename(SAVE_FILENAME)}'." 
    except Exception as e:
        error_msg = f"ERROR: Falló al guardar el archivo en '{FULL_SAVE_PATH}': {e}"
        print(error_msg)
        return False, f"Error al guardar: {e}"

def cargar_red():
    global neuronas, neuronas_visuales, zoom_level, offset_x, offset_y # Reset zoom/pan on load
    
    print(f"DEBUG: Intentando cargar desde '{FULL_SAVE_PATH}'. Verificando existencia...")
    if not os.path.exists(FULL_SAVE_PATH):
        print(f"ERROR: No se encontró el archivo de guardado en '{FULL_SAVE_PATH}'.")
        return False, f"Error: No se encontró '{os.path.basename(SAVE_FILENAME)}'."

    try:
        print(f"DEBUG: Archivo '{FULL_SAVE_PATH}' encontrado. Leyendo...")
        with open(FULL_SAVE_PATH, 'r') as f:
            loaded_data = json.load(f)
        
        neuronas.clear()
        neuronas_visuales.clear()

        temp_neuronas_by_id = {}
        temp_visuals_by_id = {}

        for item in loaded_data:
            neurona_obj = NeuronaBynarium(
                item["id"], 
                item["bits"], 
                item["valor_decimal"], 
                item["activacion"], 
                item["hi_score_activaciones"],
                item["vida_util_restante"] 
            )
            temp_neuronas_by_id[neurona_obj.id] = neurona_obj
            neuronas[neurona_obj.id] = neurona_obj 

            initial_color = get_neuron_color(neurona_obj.bits)
            visual_obj = NeuronaVisual(neurona_obj, item["pos_x"], item["pos_y"], initial_color)
            temp_visuals_by_id[neurona_obj.id] = visual_obj
            neuronas_visuales[neurona_obj.id] = visual_obj 

        for item in loaded_data:
            origen_id = item["id"]
            neurona_origen = temp_neuronas_by_id[origen_id]
            
            for destino_id in item["conectada_a_ids"]:
                if destino_id in temp_neuronas_by_id:
                    neurona_destino = temp_neuronas_by_id[destino_id]
                    neurona_origen.conectar(neurona_destino)
                else:
                    print(f"Advertencia: La neurona destino '{destino_id}' para '{origen_id}' no se encontró al cargar.")
        
        # Resetear zoom y pan al cargar una nueva red
        zoom_level = 1.0
        offset_x = 0
        offset_y = 0

        print(f"Éxito: Red cargada desde '{FULL_SAVE_PATH}'.")
        return True, f"Red cargada desde '{os.path.basename(SAVE_FILENAME)}'."
    except json.JSONDecodeError:
        print(f"ERROR: Archivo JSON inválido: '{FULL_SAVE_PATH}'.")
        return False, f"Error: El archivo '{os.path.basename(SAVE_FILENAME)}' no es un JSON válido."
    except Exception as e:
        print(f"ERROR: Falló al cargar la red: {e}") 
        return False, f"Error al cargar: {e}"

# --- INTERACCIÓN DE CONEXIÓN ---
first_clicked_neuron_visual = None
modo_conexion_activo = False
modo_conexion_tipo = "bidireccional"  
modo_eliminar_activo = False
modo_desconectar_activo = False # Nuevo: Modo para desconectar
activation_mode_active = False 
connection_message_display_time = 0
CONNECTION_MESSAGE_DURATION = 2 

# --- FUNCIONALIDAD DE RENOMBRAR NEURONAS ---
modo_renombrar_activo = False
selected_neuron_for_rename_visual = None
rename_input_active = False
rename_input_text = ""
rename_input_rect = None # Se establecerá dinámicamente

# Mensajes temporales en pantalla
message_display_time = 0
current_message = ""
MESSAGE_DEFAULT_DURATION = 3 
MESSAGE_CRITICAL_DURATION = 5 

def set_message(message, duration=MESSAGE_DEFAULT_DURATION):
    global current_message, message_display_time
    current_message = message
    message_display_time = time.time() + duration

# --- FUNCIONALIDAD DE ARRASTRAR NEURONAS ---
dragging_neuron_visual = None
drag_offset_x, drag_offset_y = 0, 0 

# --- CREADOR DE NEURONAS ---
# Ajustar posiciones para el nuevo input de nombre
input_name_rect = pygame.Rect(ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA // 2 - 100, 200, 40)
input_name_text = "" # Inicializar vacío
active_input_name_box = False

input_bits_rect = pygame.Rect(ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA // 2 - 50, 200, 40) # Ajustada posición
input_bits_text = '2' 
active_input_bits_box = False # Renombrada para claridad

create_button_rect = pygame.Rect(ANCHO_PANTALLA // 2 - 75, ALTO_PANTALLA // 2 + 10, 150, 50) # Ajustada posición
back_button_rect = pygame.Rect(50, 50, 100, 40) 

neuronas_a_eliminar = []

# --- BUCLE PRINCIPAL DE PYGAME ---
running = True
while running:
    neuronas_a_eliminar = [] 

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_screen == SCREEN_NETWORK:
            # --- MANEJO DE EVENTOS DE MOUSE EN PANTALLA DE RED ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Clic izquierdo
                    # Prioridad 1: Botones de control UI (no afectados por zoom/pan)
                    eliminar_button_rect = pygame.Rect(ANCHO_PANTALLA - 200, ALTO_PANTALLA - 70, 50, 50)
                    conexion_button_rect = pygame.Rect(ANCHO_PANTALLA - 140, ALTO_PANTALLA - 70, 50, 50)
                    rename_button_rect = pygame.Rect(ANCHO_PANTALLA - 260, ALTO_PANTALLA - 70, 50, 50)
                    disconnect_button_rect = pygame.Rect(ANCHO_PANTALLA - 320, ALTO_PANTALLA - 70, 50, 50) # Nuevo: Botón de desconexión
                    activate_nodes_button_rect = pygame.Rect(ANCHO_PANTALLA - 420, ALTO_PANTALLA - 70, 100, 50) # Ajustar posición
                    save_button_rect = pygame.Rect(ANCHO_PANTALLA - 480, ALTO_PANTALLA - 70, 50, 50) # Ajustar posición
                    load_button_rect = pygame.Rect(ANCHO_PANTALLA - 540, ALTO_PANTALLA - 70, 50, 50) # Ajustar posición
                    plus_button_rect = pygame.Rect(ANCHO_PANTALLA - 70, ALTO_PANTALLA - 70, 50, 50)

                    # Verificar clic en botones de control
                    if eliminar_button_rect.collidepoint(event.pos):
                        modo_eliminar_activo = not modo_eliminar_activo # Esto lo convierte en un toggle
                        # Desactivar todos los demás modos al activar uno nuevo
                        activation_mode_active = False ; modo_conexion_activo = False ; modo_renombrar_activo = False; modo_desconectar_activo = False
                        rename_input_active = False; selected_neuron_for_rename_visual = None; first_clicked_neuron_visual = None
                        connection_message_display_time = 0
                        set_message(f"Modo eliminar {'activado' if modo_eliminar_activo else 'desactivado'}.")
                        continue
                    elif conexion_button_rect.collidepoint(event.pos):
                        modo_conexion_activo = not modo_conexion_activo
                        activation_mode_active = False ; modo_eliminar_activo = False ; modo_renombrar_activo = False; modo_desconectar_activo = False
                        rename_input_active = False; selected_neuron_for_rename_visual = None; first_clicked_neuron_visual = None
                        connection_message_display_time = 0
                        set_message(f"Modo conexión {'activado' if modo_conexion_activo else 'desactivado'}.")
                        continue
                    elif rename_button_rect.collidepoint(event.pos):
                        modo_renombrar_activo = not modo_renombrar_activo
                        activation_mode_active = False; modo_conexion_activo = False; modo_eliminar_activo = False; modo_desconectar_activo = False
                        if not modo_renombrar_activo: 
                            rename_input_active = False; selected_neuron_for_rename_visual = None; rename_input_text = ""
                        set_message(f"Modo Renombrar {'activado' if modo_renombrar_activo else 'desactivado'}.")
                        continue
                    elif disconnect_button_rect.collidepoint(event.pos): # Nuevo: Lógica del botón de desconexión
                        modo_desconectar_activo = not modo_desconectar_activo
                        activation_mode_active = False; modo_conexion_activo = False; modo_eliminar_activo = False; modo_renombrar_activo = False
                        first_clicked_neuron_visual = None # Resetear la primera neurona seleccionada para desconexión
                        set_message(f"Modo desconectar {'activado' if modo_desconectar_activo else 'desactivado'}.")
                        continue
                    elif activate_nodes_button_rect.collidepoint(event.pos):
                        activation_mode_active = not activation_mode_active
                        modo_conexion_activo = False ; modo_eliminar_activo = False ; modo_renombrar_activo = False; modo_desconectar_activo = False
                        rename_input_active = False; selected_neuron_for_rename_visual = None; first_clicked_neuron_visual = None
                        connection_message_display_time = 0
                        set_message(f"Modo activación de nodos {'activado' if activation_mode_active else 'desactivado'}.")
                        continue
                    elif save_button_rect.collidepoint(event.pos):
                        success, msg = guardar_red()
                        set_message(msg, duration=MESSAGE_CRITICAL_DURATION) 
                        continue
                    elif load_button_rect.collidepoint(event.pos):
                        success, msg = cargar_red()
                        set_message(msg, duration=MESSAGE_CRITICAL_DURATION) 
                        if success: 
                            modo_conexion_activo = False; modo_eliminar_activo = False; activation_mode_active = False
                            modo_renombrar_activo = False; modo_desconectar_activo = False
                            rename_input_active = False; selected_neuron_for_rename_visual = None
                            first_clicked_neuron_visual = None; dragging_neuron_visual = None
                        continue
                    elif plus_button_rect.collidepoint(event.pos):
                        current_screen = SCREEN_CREATOR
                        input_name_text = ""; active_input_name_box = False
                        input_bits_text = '2'; active_input_bits_box = False
                        first_clicked_neuron_visual = None ; connection_message_display_time = 0
                        dragging_neuron_visual = None 
                        modo_conexion_activo = False ; modo_eliminar_activo = False
                        activation_mode_active = False; modo_renombrar_activo = False ; modo_desconectar_activo = False
                        rename_input_active = False; selected_neuron_for_rename_visual = None
                        set_message("Modo Creador activado.")
                        continue

                    # Prioridad 2: Interacción con Neuronas o Panning con clic izquierdo
                    # Convertir coordenadas del ratón a coordenadas "mundiales" (afectadas por zoom y pan)
                    transformed_mouse_x = (mouse_x / zoom_level) - offset_x
                    transformed_mouse_y = (mouse_y / zoom_level) - offset_y

                    clicked_on_neuron = False
                    for visual_neurona in list(neuronas_visuales.values()): 
                        dist_a_neurona = math.hypot(transformed_mouse_x - visual_neurona.x, transformed_mouse_y - visual_neurona.y)
                        if dist_a_neurona <= visual_neurona.radio: 
                            clicked_on_neuron = True
                            if modo_renombrar_activo:
                                selected_neuron_for_rename_visual = visual_neurona
                                rename_input_active = True
                                rename_input_text = visual_neurona.neurona.id
                                rename_input_rect = pygame.Rect(visual_neurona.x * zoom_level + offset_x * zoom_level - 75, 
                                                                visual_neurona.y * zoom_level + offset_y * zoom_level - visual_neurona.radio * zoom_level - 50, 
                                                                150, 30)
                                set_message(f"Selecciona '{visual_neurona.neurona.id}' para renombrar.")
                                break 
                            elif modo_eliminar_activo:
                                id_a_borrar = visual_neurona.neurona.id
                                if id_a_borrar in neuronas:
                                    neuronas_a_eliminar.append(id_a_borrar) 
                                    #modo_eliminar_activo = False  
                                    set_message(f"Neurona '{id_a_borrar}' marcada para eliminar.", duration=1.5)
                                    break
                            elif modo_desconectar_activo: # Nuevo: Lógica de desconexión al hacer clic en neuronas
                                if first_clicked_neuron_visual is None:
                                    first_clicked_neuron_visual = visual_neurona
                                    set_message(f"Neurona '{visual_neurona.neurona.id}' seleccionada para desconexión.")
                                elif first_clicked_neuron_visual.neurona.id == visual_neurona.neurona.id:
                                    first_clicked_neuron_visual = None
                                    set_message("Selección de desconexión cancelada.")
                                else:
                                    origen_desc = first_clicked_neuron_visual.neurona
                                    destino_desc = visual_neurona.neurona
                                    if destino_desc in origen_desc.conectada_a:
                                        origen_desc.desconectar(destino_desc)
                                        set_message(f"Desconectado: {origen_desc.id} de {destino_desc.id}")
                                    elif origen_desc in destino_desc.conectada_a: # Check inverse connection
                                        destino_desc.desconectar(origen_desc)
                                        set_message(f"Desconectado: {destino_desc.id} de {origen_desc.id}")
                                    else:
                                        set_message(f"No hay conexión entre {origen_desc.id} y {destino_desc.id}", duration=2)
                                    first_clicked_neuron_visual = None
                                    modo_desconectar_activo = False # Desactivar después de una desconexión
                                break
                            elif activation_mode_active:
                                if visual_neurona.neurona.recibir_activacion():
                                    visual_neurona.trigger_flash()
                                    set_message(f"'{visual_neurona.neurona.id}' activada. Act: {visual_neurona.neurona.activacion}", duration=1.5)
                                else:
                                    set_message(f"'{visual_neurona.neurona.id}' ya está al máximo de activación.", duration=1.5)
                                break 
                            elif modo_conexion_activo:
                                if first_clicked_neuron_visual is None:
                                    first_clicked_neuron_visual = visual_neurona
                                    connection_message_display_time = time.time()
                                    set_message(f"Neurona '{visual_neurona.neurona.id}' seleccionada para conexión.")
                                elif first_clicked_neuron_visual.neurona.id == visual_neurona.neurona.id:
                                    first_clicked_neuron_visual = None
                                    connection_message_display_time = 0
                                    set_message("Selección de conexión cancelada.")
                                else:
                                    origen = first_clicked_neuron_visual.neurona
                                    destino = visual_neurona.neurona
                                    if modo_conexion_tipo == "bidireccional":
                                        origen.conectar(destino)
                                        destino.conectar(origen)
                                        set_message(f"Conexión bidireccional: {origen.id} ⇆ {destino.id}")
                                    elif modo_conexion_tipo == "salida":
                                        origen.conectar(destino)
                                        set_message(f"Conexión de salida: {origen.id} → {destino.id}")
                                    elif modo_conexion_tipo == "entrada":
                                        destino.conectar(origen)
                                        set_message(f"Conexión de entrada: {destino.id} ← {origen.id}")
                                    first_clicked_neuron_visual = None
                                    connection_message_display_time = 0
                            else:
                                # Modo normal: arrastrar neurona
                                dragging_neuron_visual = visual_neurona
                                drag_offset_x = transformed_mouse_x - visual_neurona.x
                                drag_offset_y = transformed_mouse_y - visual_neurona.y
                                first_clicked_neuron_visual = None  
                                connection_message_display_time = 0
                                panning_active = False # Asegurarse de que el panning no esté activo si se arrastra una neurona
                            break 

                    # Si el clic no fue sobre una neurona NI sobre un botón de UI, iniciar panning con clic izquierdo
                    if not clicked_on_neuron:
                        if first_clicked_neuron_visual is not None and dragging_neuron_visual is None:
                            first_clicked_neuron_visual = None
                            set_message("Selección de conexión/desconexión cancelada (clic fuera).")
                        if modo_renombrar_activo and rename_input_active:
                            if rename_input_rect and not rename_input_rect.collidepoint(event.pos):
                                rename_input_active = False
                                selected_neuron_for_rename_visual = None
                                rename_input_text = ""
                                set_message("Renombrar cancelado (clic fuera).", duration=1.5)
                        
                        # Iniciar panning con clic izquierdo si no se interactuó con nada más
                        if not modo_eliminar_activo and not modo_desconectar_activo and \
                           not activation_mode_active and not modo_conexion_activo and \
                           not modo_renombrar_activo and not dragging_neuron_visual:
                            panning_active = True
                            pan_start_mouse_x, pan_start_mouse_y = event.pos
                            pan_start_offset_x, pan_start_offset_y = offset_x, offset_y

                elif event.button == 2: # Clic central del ratón para panning (ya existente)
                    panning_active = True
                    pan_start_mouse_x, pan_start_mouse_y = event.pos
                    pan_start_offset_x, pan_start_offset_y = offset_x, offset_y

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 or event.button == 2: # Cualquier botón arriba detiene arrastre o panning
                    dragging_neuron_visual = None
                    panning_active = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging_neuron_visual:
                    transformed_mouse_x = (mouse_x / zoom_level) - offset_x
                    transformed_mouse_y = (mouse_y / zoom_level) - offset_y
                    dragging_neuron_visual.x = transformed_mouse_x - drag_offset_x
                    dragging_neuron_visual.y = transformed_mouse_y - drag_offset_y
                elif panning_active:
                    dx = (mouse_x - pan_start_mouse_x) / zoom_level
                    dy = (mouse_y - pan_start_mouse_y) / zoom_level
                    offset_x = pan_start_offset_x + dx
                    offset_y = pan_start_offset_y + dy
            
            elif event.type == pygame.MOUSEWHEEL:
                zoom_factor = 1.1 if event.y > 0 else 1 / 1.1 
                
                world_x_before_zoom = (mouse_x / zoom_level) - offset_x
                world_y_before_zoom = (mouse_y / zoom_level) - offset_y

                zoom_level = max(0.2, min(5.0, zoom_level * zoom_factor)) 

                offset_x = (mouse_x / zoom_level) - world_x_before_zoom
                offset_y = (mouse_y / zoom_level) - world_y_before_zoom
                
                set_message(f"Zoom: {zoom_level:.2f}x", duration=1)

            # Manejo de teclado para renombrar
            if event.type == pygame.KEYDOWN:
                if rename_input_active:
                    if event.key == pygame.K_RETURN:
                        old_id = selected_neuron_for_rename_visual.neurona.id
                        new_id = rename_input_text.strip() 

                        if not new_id:
                            set_message("Error: El nombre no puede estar vacío.", duration=2)
                        elif new_id == old_id:
                            set_message("No se realizaron cambios en el nombre.", duration=1.5)
                        else:
                            is_unique = True
                            for neuron_key, _ in neuronas.items():
                                if neuron_key.lower() == new_id.lower() and neuron_key != old_id: 
                                    is_unique = False
                                    break
                            
                            if not is_unique:
                                set_message(f"Error: El nombre '{new_id}' ya está en uso.", duration=2)
                            else:
                                try:
                                    selected_neuron_for_rename_visual.neurona.id = new_id
                                  
                                    
                                    new_neuronas = {}
                                    for neuron_key, neuron_obj in neuronas.items():
                                        if neuron_key == old_id:
                                            new_neuronas[new_id] = neuron_obj
                                        else:
                                            new_neuronas[neuron_key] = neuron_obj
                                    neuronas = new_neuronas

                                    new_neuronas_visuales = {}
                                    for visual_key, visual_obj in neuronas_visuales.items():
                                        if visual_key == old_id:
                                            new_neuronas_visuales[new_id] = visual_obj
                                        else:
                                            new_neuronas_visuales[visual_key] = visual_obj
                                    neuronas_visuales = new_neuronas_visuales

                                    set_message(f"Neurona '{old_id}' renombrada a '{new_id}'.", duration=2)
                                except Exception as e:
                                    set_message(f"Error al renombrar: {e}", duration=3)
                        
                        rename_input_active = False
                        selected_neuron_for_rename_visual = None
                        rename_input_text = ""
                        modo_renombrar_activo = False 
                    
                    elif event.key == pygame.K_BACKSPACE:
                        rename_input_text = rename_input_text[:-1]
                    else:
                        if len(rename_input_text) < 20: 
                            rename_input_text += event.unicode
                
                # Otros atajos de teclado (fuera del modo renombrar o input activo)
                if not rename_input_active:
                    if event.key == pygame.K_TAB:
                        if modo_conexion_activo: 
                            if modo_conexion_tipo == "bidireccional":
                                modo_conexion_tipo = "salida"
                            elif modo_conexion_tipo == "salida":
                                modo_conexion_tipo = "entrada"
                            elif modo_conexion_tipo == "entrada":
                                modo_conexion_tipo = "bidireccional"
                            set_message(f"Tipo de conexión cambiado a: {modo_conexion_tipo}")
                    
                    if event.key == pygame.K_SPACE:
                        set_message("Activando neuronas de nivel 2...", duration=1) 
                        for id, neurona_obj in list(neuronas.items()): 
                            if neurona_obj.bits == 2: # NS
                                if neurona_obj.recibir_activacion(): 
                                    neuronas_visuales[id].trigger_flash()
                                    if neurona_obj.hi_score_activaciones >= neurona_obj.max_almacenamiento:
                                        neurona_obj.vida_util_restante -= 1 
                                        set_message(f"'{id}' alcanzó fatiga. VU: {neurona_obj.vida_util_restante}", duration=1.5)
                                        if neurona_obj.vida_util_restante <= 0:
                                            if random.random() < 0.5: 
                                                if id not in neuronas_a_eliminar: 
                                                    neuronas_a_eliminar.append(id)
                                                    set_message(f"'{id}' agotó vida útil y desapareció! (50%)", duration=1.5)
                                        else:
                                            neuronas_visuales[id].trigger_flash() 
                                else:
                                    set_message(f"'{id}' ya estaba al máximo.", duration=1.5)

                    if event.key == pygame.K_a: 
                        if neuronas: 
                            random_ns = random.choice(list(neuronas.values()))
                            if random_ns.recibir_activacion():
                                neuronas_visuales[random_ns.id].trigger_flash()
                                set_message(f"'{random_ns.id}' activada por 'A'.", duration=1.5)
                            else:
                                set_message(f"'{random_ns.id}' ya está al máximo.", duration=1.5)
                        else:
                            set_message("No hay neuronas para activar.", duration=1.5)

                    if event.key == pygame.K_v:
                        for neurona_obj in neuronas.values():
                            random_val = random.randint(0, neurona_obj.max_almacenamiento) 
                            if neurona_obj.set_valor(random_val):
                                neuronas_visuales[neurona_obj.id].trigger_flash()
                        set_message("Valores de neuronas seteados aleatoriamente.", duration=1.5)

                    if event.key == pygame.K_c:
                        neurons_to_propagate_this_cycle = []
                        for n in neuronas.values():
                            if n.activacion == n.max_almacenamiento:
                                neurons_to_propagate_this_cycle.append(n)

                        propagated_any = False
                        for neurona_origen in neurons_to_propagate_this_cycle:
                            if neurona_origen.id in neuronas:
                                neuronas_visuales[neurona_origen.id].trigger_flash() 

                                potential_destinations_sorted = sorted(
                                    [n for n in neurona_origen.conectada_a if n.activacion < n.max_almacenamiento and n.id in neuronas], 
                                    key=lambda n: n.bits
                                )
                                
                                for destino_neurona in potential_destinations_sorted:
                                    if destino_neurona.recibir_activacion(): 
                                        neuronas_visuales[destino_neurona.id].trigger_flash()
                                        set_message(f"Propagación: {neurona_origen.id} -> {destino_neurona.id}", duration=1.5)
                                        neurona_origen.activacion -= 1
                                        propagated_any = True
                                        break 
                            
                        if not propagated_any:
                            set_message("No se encontraron neuronas llenas para propagar o destinos vacíos.", duration=2)
                    
                    if event.key == pygame.K_r:
                        for neurona_obj in neuronas.values():
                            neurona_obj.activacion = 0
                            neurona_obj.valor_decimal = 0
                            neurona_obj.hi_score_activaciones = 0 
                            neurona_obj.vida_util_restante = abs(20 - neurona_obj.bits) 
                            if neurona_obj.vida_util_restante == 0: neurona_obj.vida_util_restante = 1 
                            neuronas_visuales[neurona_obj.id].trigger_flash()
                        set_message("Red de neuronas reiniciada.", duration=1.5)

        elif current_screen == SCREEN_CREATOR:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if back_button_rect.collidepoint(event.pos):
                        current_screen = SCREEN_NETWORK
                        set_message("Volviendo a la red.", duration=1.5)
                        continue
                    
                    if input_name_rect.collidepoint(event.pos):
                        active_input_name_box = True
                        active_input_bits_box = False 
                    elif input_bits_rect.collidepoint(event.pos):
                        active_input_bits_box = True
                        active_input_name_box = False 
                    else:
                        active_input_name_box = False
                        active_input_bits_box = False
                    
                    if create_button_rect.collidepoint(event.pos):
                        new_id = input_name_text.strip()
                        try:
                            new_bits = int(input_bits_text)
                            
                            if not new_id:
                                set_message("Error: El nombre de la neurona no puede estar vacío.", duration=2)
                            elif new_bits < 1:
                                set_message("Error: El NB debe ser >= 1.", duration=2)
                            else:
                                is_unique = True
                                for neuron_key in neuronas.keys():
                                    if neuron_key.lower() == new_id.lower():
                                        is_unique = False
                                        break
                                
                                if not is_unique:
                                    set_message(f"Error: La neurona '{new_id}' ya existe.", duration=2)
                                else:
                                    new_neuron_bynarium = NeuronaBynarium(new_id, new_bits)
                                    neuronas[new_id] = new_neuron_bynarium

                                    new_neuron_color = get_neuron_color(new_bits)

                                    new_x = ANCHO_PANTALLA // 2
                                    new_y = ALTO_PANTALLA // 2

                                    new_neuron_visual = NeuronaVisual(new_neuron_bynarium, new_x, new_y, new_neuron_color)
                                    neuronas_visuales[new_id] = new_neuron_visual
                                    
                                    set_message(f"Neurona '{new_id}' creada (NB: {new_bits}).", duration=2)
                                    input_name_text = "" 
                                    input_bits_text = '2' 
                                    current_screen = SCREEN_NETWORK 

                        except ValueError:
                            set_message("Error: Ingresa números válidos para Bits.", duration=2)

            if event.type == pygame.KEYDOWN:
                if active_input_name_box:
                    if event.key == pygame.K_RETURN:
                        active_input_name_box = False
                        active_input_bits_box = True 
                    elif event.key == pygame.K_BACKSPACE:
                        input_name_text = input_name_text[:-1]
                    else:
                        if len(input_name_text) < 20: 
                            input_name_text += event.unicode
                elif active_input_bits_box: 
                    if event.key == pygame.K_RETURN:
                        active_input_bits_box = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_bits_text = input_bits_text[:-1]
                    else:
                        if event.unicode.isdigit() and len(input_bits_text) < 3: 
                            input_bits_text += event.unicode


    # --- Lógica de Desaparición y Conexión Automática (Fatiga) ---
    for id_origen, neurona_origen in list(neuronas.items()): 
        if id_origen in neuronas_a_eliminar:
            continue

        if neurona_origen.hi_score_activaciones >= neurona_origen.max_almacenamiento:
            neurona_origen.vida_util_restante -= 1
            neurona_origen.hi_score_activaciones = 0 

            if neurona_origen.vida_util_restante <= 0:
                if random.random() < 0.5: 
                    if id_origen not in neuronas_a_eliminar: 
                        neuronas_a_eliminar.append(id_origen)
                else:
                    neuronas_visuales[id_origen].trigger_flash()


        if neurona_origen.hi_score_activaciones >= (neurona_origen.max_almacenamiento * 0.8):
            neuronas_sueltas_para_conexion = [
                n for n in neuronas.values() 
                if n.id != neurona_origen.id 
                and n not in neurona_origen.conectada_a
                and n.id not in neuronas_a_eliminar 
            ]
            if neuronas_sueltas_para_conexion:
                neuronas_sueltas_para_conexion.sort(key=lambda x: x.bits)
                
                for neurona_destino_aleatoria in neuronas_sueltas_para_conexion:
                    if neurona_origen.conectar(neurona_destino_aleatoria):
                        neurona_origen.hi_score_activaciones = 0 
                        neuronas_visuales[neurona_origen.id].trigger_flash() 
                        neuronas_visuales[neurona_destino_aleatoria.id].trigger_flash()
                        set_message(f"'{neurona_origen.id}' se conectó automáticamente a '{neurona_destino_aleatoria.id}'.", duration=1.5)
                        break 

    # Eliminar neuronas marcadas
    for id_eliminar in neuronas_a_eliminar:
        for n_obj in neuronas.values():
            n_obj.conectada_a = [target for target in n_obj.conectada_a if target.id != id_eliminar]
            n_obj.conectada_desde = [source for source in n_obj.conectada_desde if source.id != id_eliminar]

        if id_eliminar in neuronas:
            del neuronas[id_eliminar]
        if id_eliminar in neuronas_visuales:
            del neuronas_visuales[id_eliminar]


    # --- LÓGICA DE DIBUJO ---
    pantalla.fill(BLANCO)

    if current_screen == SCREEN_NETWORK:
        # Dibujar conexiones (aplicar zoom y offset)
        for id_origen, neurona_o in list(neuronas.items()): 
            if id_origen in neuronas_visuales:
                inicio_x = int((neuronas_visuales[id_origen].x + offset_x) * zoom_level)
                inicio_y = int((neuronas_visuales[id_origen].y + offset_y) * zoom_level)
                inicio = (inicio_x, inicio_y)
                for neurona_destino_obj in list(neurona_o.conectada_a):
                    id_destino = neurona_destino_obj.id
                    if id_destino in neuronas_visuales:
                        fin_x = int((neuronas_visuales[id_destino].x + offset_x) * zoom_level)
                        fin_y = int((neuronas_visuales[id_destino].y + offset_y) * zoom_level)
                        fin = (fin_x, fin_y)
                        pygame.draw.line(pantalla, GRIS, inicio, fin, max(1, int(3 * zoom_level))) # Grosor de línea también con zoom

        # Dibujar botones de control inferiores (sin zoom/pan)
        button_y = ALTO_PANTALLA - 70
        button_height = 50
        button_width = 50 
        
        plus_button_rect = pygame.Rect(ANCHO_PANTALLA - 70, button_y, button_width, button_height)
        conexion_button_rect = pygame.Rect(ANCHO_PANTALLA - 140, button_y, button_width, button_height)
        eliminar_button_rect = pygame.Rect(ANCHO_PANTALLA - 200, button_y, button_width, button_height)
        rename_button_rect = pygame.Rect(ANCHO_PANTALLA - 260, button_y, button_width, button_height) 
        disconnect_button_rect = pygame.Rect(ANCHO_PANTALLA - 320, button_y, button_width, button_height) # Nuevo botón
        activate_nodes_button_rect = pygame.Rect(ANCHO_PANTALLA - 420, button_y, 100, button_height) # Posición ajustada
        save_button_rect = pygame.Rect(ANCHO_PANTALLA - 480, button_y, button_width, button_height) # Posición ajustada
        load_button_rect = pygame.Rect(ANCHO_PANTALLA - 540, button_y, button_width, button_height) # Posición ajustada


        # Dibujar botón "�️"
        color_boton_eliminar = ROJO if modo_eliminar_activo else GRIS
        pygame.draw.rect(pantalla, color_boton_eliminar, eliminar_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, eliminar_button_rect, 2, 5)
        texto_eliminar = fuente.render("🗑️", True, NEGRO)
        pantalla.blit(texto_eliminar, (eliminar_button_rect.x + 10, eliminar_button_rect.y + 8))
                   
        # Dibujar botón "⇆" (Modo Conexión)
        color_boton = VERDE if modo_conexion_activo else GRIS
        pygame.draw.rect(pantalla, color_boton, conexion_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, conexion_button_rect, 2, 5)
        simbolo = {"bidireccional": "⇆", "salida": "→", "entrada": "←"}[modo_conexion_tipo]
        texto_conectar = fuente.render(simbolo, True, NEGRO)
        pantalla.blit(texto_conectar, (conexion_button_rect.x + 15, conexion_button_rect.y + 10))

        # Dibujar botón "✍️" (Renombrar)
        color_rename_button = PURPURA if modo_renombrar_activo else GRIS
        pygame.draw.rect(pantalla, color_rename_button, rename_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, rename_button_rect, 2, 5)
        texto_renombrar = fuente.render("✍️", True, NEGRO)
        pantalla.blit(texto_renombrar, (rename_button_rect.x + 10, rename_button_rect.y + 8))

        # Dibujar botón "🔗" (Desconectar)
        color_disconnect_button = CIAN if modo_desconectar_activo else GRIS
        pygame.draw.rect(pantalla, color_disconnect_button, disconnect_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, disconnect_button_rect, 2, 5)
        texto_desconectar = fuente.render("🔗", True, NEGRO)
        pantalla.blit(texto_desconectar, (disconnect_button_rect.x + 10, disconnect_button_rect.y + 8))


        # Dibujar botón "Activar Nodos"
        color_activate_button = VERDE if activation_mode_active else GRIS
        pygame.draw.rect(pantalla, color_activate_button, activate_nodes_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, activate_nodes_button_rect, 2, 5)
        texto_activate = fuente_pequena.render("Activar", True, NEGRO)
        texto_activate_rect = texto_activate.get_rect(center=activate_nodes_button_rect.center)
        pantalla.blit(texto_activate, texto_activate_rect)

        # Dibujar botón "Guardar"
        pygame.draw.rect(pantalla, AMARILLO, save_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, save_button_rect, 2, 5)
        texto_guardar = fuente.render("💾", True, NEGRO)
        pantalla.blit(texto_guardar, (save_button_rect.x + 10, save_button_rect.y + 8))

        # Dibujar botón "Cargar"
        pygame.draw.rect(pantalla, CIAN, load_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, load_button_rect, 2, 5)
        texto_cargar = fuente.render("📂", True, NEGRO)
        pantalla.blit(texto_cargar, (load_button_rect.x + 10, load_button_rect.y + 8))


        # Dibujar neuronas (aplicar zoom y offset)
        hovered_neuron_visual = None
        for visual_neurona in list(neuronas_visuales.values()): 
            if visual_neurona != dragging_neuron_visual:
                is_selected = (first_clicked_neuron_visual == visual_neurona)
                is_renaming_this = (selected_neuron_for_rename_visual == visual_neurona and rename_input_active)
                is_disconnecting_this = (first_clicked_neuron_visual == visual_neurona and modo_desconectar_activo)
                visual_neurona.dibujar(pantalla, zoom_level, offset_x, offset_y, is_selected, False, modo_eliminar_activo, is_renaming_this, is_disconnecting_this) 
                
                # Colisión para tooltip, usando coordenadas transformadas inversas
                transformed_mouse_x = (mouse_x / zoom_level) - offset_x
                transformed_mouse_y = (mouse_y / zoom_level) - offset_y
                dist_a_neurona = math.hypot(transformed_mouse_x - visual_neurona.x, transformed_mouse_y - visual_neurona.y)
                if dist_a_neurona <= visual_neurona.radio and dragging_neuron_visual is None:
                    hovered_neuron_visual = visual_neurona
        
        if dragging_neuron_visual:
            dragging_neuron_visual.dibujar(pantalla, zoom_level, offset_x, offset_y, False, True, modo_eliminar_activo) 
            hovered_neuron_visual = dragging_neuron_visual 

        if hovered_neuron_visual:
            # Tooltip se dibuja en coordenadas de pantalla, así que no se aplica zoom/offset
            dibujar_tooltip(pantalla, (mouse_x, mouse_y), hovered_neuron_visual)

        # Dibujar Input Box de Renombrar si está activo
        if rename_input_active and selected_neuron_for_rename_visual:
            # Re-calcular la posición del input box en coordenadas de pantalla
            rename_input_rect = pygame.Rect(
                (selected_neuron_for_rename_visual.x + offset_x) * zoom_level - 75, 
                (selected_neuron_for_rename_visual.y + offset_y) * zoom_level - (selected_neuron_for_rename_visual.radio * zoom_level) - 50, 
                150, 30)

            pygame.draw.rect(pantalla, BLANCO_APAGADO, rename_input_rect, 0, 5)
            pygame.draw.rect(pantalla, AZUL, rename_input_rect, 2, 5) 
            text_surface = fuente_pequena.render(rename_input_text, True, NEGRO)
            pantalla.blit(text_surface, (rename_input_rect.x + 5, rename_input_rect.y + 5))


        # Indicar al usuario qué teclas usar (en pantalla, sin zoom/pan)
        texto_ayuda_y_offset = 20
        texto_ayuda_teclas = [
            "ESPACIO: Activar NS de nivel 2", 
            "A: Activar neurona aleatoria", 
            "V: Set valores aleatorios", 
            "C: Propagar 1 paso (Sólo llenas, jerárquico)", 
            "R: Reiniciar Red"
        ]
        for i, linea in enumerate(texto_ayuda_teclas):
            texto_render = fuente_pequena.render(linea, True, NEGRO)
            pantalla.blit(texto_render, (20, texto_ayuda_y_offset + i * 15))

        texto_ayuda_drag = fuente_pequena.render("Clic y arrastrar para mover neuronas.", True, NEGRO)
        pantalla.blit(texto_ayuda_drag, (20, texto_ayuda_y_offset + len(texto_ayuda_teclas) * 15 + 5))
        texto_ayuda_connect = fuente_pequena.render("Clic 2 veces en neuronas para conectar (origen → destino). TAB: Cambiar tipo de conexión", True, NEGRO)
        pantalla.blit(texto_ayuda_connect, (20, texto_ayuda_y_offset + len(texto_ayuda_teclas) * 15 + 20))
        texto_ayuda_rename = fuente_pequena.render("Modo renombrar: Clic en neurona para editar ID. ENTER para confirmar.", True, NEGRO)
        pantalla.blit(texto_ayuda_rename, (20, texto_ayuda_y_offset + len(texto_ayuda_teclas) * 15 + 35))
        texto_ayuda_zoom_pan = fuente_pequena.render("Rueda del ratón: Zoom. Clic IZQ (fuera de neurona): Pan. Clic MEDIO: Pan.", True, NEGRO)
        pantalla.blit(texto_ayuda_zoom_pan, (20, texto_ayuda_y_offset + len(texto_ayuda_teclas) * 15 + 50))
        texto_ayuda_disconnect = fuente_pequena.render("Modo desconectar: Clic en 2 neuronas conectadas para desconectarlas.", True, NEGRO)
        pantalla.blit(texto_ayuda_disconnect, (20, texto_ayuda_y_offset + len(texto_ayuda_teclas) * 15 + 65))


        # Mensaje de conexión/desconexión (sin zoom/pan)
        if first_clicked_neuron_visual is not None and (time.time() - connection_message_display_time) < CONNECTION_MESSAGE_DURATION:
            msg_text = fuente.render(f"Haz clic en otra neurona para conectar/desconectar '{first_clicked_neuron_visual.neurona.id}'", True, AZUL)
            msg_rect = msg_text.get_rect(center=(ANCHO_PANTALLA // 2, 50))
            pantalla.blit(msg_text, msg_rect)
        
        # Dibujar botón '+' para ir al creador (sin zoom/pan)
        pygame.draw.circle(pantalla, GRIS, plus_button_rect.center, 25)
        pygame.draw.line(pantalla, NEGRO, (plus_button_rect.centerx - 10, plus_button_rect.centery), (plus_button_rect.centerx + 10, plus_button_rect.centery), 3)
        pygame.draw.line(pantalla, NEGRO, (plus_button_rect.centerx, plus_button_rect.centery - 10), (plus_button_rect.centerx, plus_button_rect.centery + 10), 3)

        # Mostrar mensajes temporales (Guardar/Cargar/Errores/Renombrar) (sin zoom/pan)
        if current_message and time.time() < message_display_time:
            msg_surface = fuente_grande.render(current_message, True, NEGRO)
            msg_rect = msg_surface.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
            bg_rect = msg_rect.inflate(40, 20)
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA) 
            s.fill((200, 200, 200, 180)) 
            pantalla.blit(s, (bg_rect.x, bg_rect.y))
            pygame.draw.rect(pantalla, NEGRO, bg_rect, 2, 5) 
            pantalla.blit(msg_surface, msg_rect)

    elif current_screen == SCREEN_CREATOR:
        # Los elementos del creador no tienen zoom/pan
        titulo = fuente_grande.render("Crear Nueva Neurona Bynarium", True, NEGRO)
        titulo_rect = titulo.get_rect(center=(ANCHO_PANTALLA // 2, 100))
        pantalla.blit(titulo, titulo_rect)

        pygame.draw.rect(pantalla, GRIS, back_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, back_button_rect, 2, 5)
        texto_back = fuente.render("Volver", True, NEGRO)
        texto_back_rect = texto_back.get_rect(center=back_button_rect.center)
        pantalla.blit(texto_back, texto_back_rect)

        # Input para el nombre de la neurona
        texto_name_label = fuente.render("Nombre de Neurona (ID):", True, NEGRO)
        pantalla.blit(texto_name_label, (input_name_rect.x - texto_name_label.get_width() - 10, input_name_rect.y + 5))
        color_input_name = BLANCO_APAGADO if active_input_name_box else BLANCO
        pygame.draw.rect(pantalla, color_input_name, input_name_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, input_name_rect, 2, 5)
        texto_input_name = fuente.render(input_name_text, True, NEGRO)
        pantalla.blit(texto_input_name, (input_name_rect.x + 5, input_name_rect.y + 5))

        # Input para el número de bits
        texto_bits_label = fuente.render("Número de Bits (NB):", True, NEGRO)
        pantalla.blit(texto_bits_label, (input_bits_rect.x - texto_bits_label.get_width() - 10, input_bits_rect.y + 5))
        color_input_bits = BLANCO_APAGADO if active_input_bits_box else BLANCO
        pygame.draw.rect(pantalla, color_input_bits, input_bits_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, input_bits_rect, 2, 5)
        texto_input_bits = fuente.render(input_bits_text, True, NEGRO)
        pantalla.blit(texto_input_bits, (input_bits_rect.x + 5, input_bits_rect.y + 5))

        try:
            preview_bits = int(input_bits_text)
            if preview_bits >= 1:
                preview_color = get_neuron_color(preview_bits)
                preview_center_y = ALTO_PANTALLA // 2 + 180 
                preview_radius = preview_bits * 7 
                
                formula_limit_n_preview = preview_bits - 1
                if formula_limit_n_preview < 0: formula_limit_n_preview = 0
                max_almacenamiento_preview = int(calcular_sumatoria_serie(formula_limit_n_preview))

                preview_vida_util = abs(20 - preview_bits)
                if preview_vida_util == 0: preview_vida_util = 1

                pygame.draw.circle(pantalla, preview_color, (ANCHO_PANTALLA // 2, preview_center_y), preview_radius)
                pygame.draw.circle(pantalla, NEGRO, (ANCHO_PANTALLA // 2, preview_center_y), preview_radius, 2)
                
                texto_preview_bits = fuente_pequena.render(f"NB: {preview_bits}", True, NEGRO)
                texto_preview_max = fuente_pequena.render(f"Max Almacenamiento: {max_almacenamiento_preview}", True, PURPURA)
                texto_preview_vida_util = fuente_pequena.render(f"Vida Útil: {preview_vida_util}", True, CIAN)

                pantalla.blit(texto_preview_bits, (ANCHO_PANTALLA // 2 - texto_preview_bits.get_width() // 2, preview_center_y - preview_radius - 30))
                pantalla.blit(texto_preview_max, (ANCHO_PANTALLA // 2 - texto_preview_max.get_width() // 2, preview_center_y + preview_radius + 10))
                pantalla.blit(texto_preview_vida_util, (ANCHO_PANTALLA // 2 - texto_preview_vida_util.get_width() // 2, preview_center_y + preview_radius + 25))

            else:
                texto_error = fuente_pequena.render("NB debe ser >= 1", True, ROJO)
                pantalla.blit(texto_error, (ANCHO_PANTALLA // 2 - texto_error.get_width() // 2, ALTO_PANTALLA // 2 + 150))

        except ValueError:
            texto_error = fuente_pequena.render("Ingresa un número válido", True, ROJO)
            pantalla.blit(texto_error, (ANCHO_PANTALLA // 2 - texto_error.get_width() // 2, ALTO_PANTALLA // 2 + 150))


        pygame.draw.rect(pantalla, VERDE, create_button_rect, 0, 5)
        pygame.draw.rect(pantalla, NEGRO, create_button_rect, 2, 5)
        texto_crear = fuente.render("Crear Neurona", True, BLANCO)
        texto_crear_rect = texto_crear.get_rect(center=create_button_rect.center)
        pantalla.blit(texto_crear, texto_crear_rect)


    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
sys.exit()