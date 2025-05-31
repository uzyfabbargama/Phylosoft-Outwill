import pygame
import sys
import math
# Importarías tu lógica de Bynarium aquí si estuviera en un archivo separado.
# Por simplicidad, simularemos el estado de las neuronas para esta demostración.

# --- SIMULACIÓN DEL ESTADO DE BYNARIUM (PARA DEMOSTRACIÓN) ---
# En una aplicación real, este diccionario sería el 'neuronas_estado'
# de tu lógica de Bynarium, y lo actualizarías desde allí.
neuronas_estado_simulado = {
    'N1': {'bits': 4, 'current_activations_val': 1, 'valor_decimal': 3, 'connections_out': {'N2', 'N3'}},
    'N2': {'bits': 3, 'current_activations_val': 0, 'valor_decimal': 0, 'connections_out': set()},
    'N3': {'bits': 5, 'current_activations_val': 5, 'valor_decimal': 15, 'connections_out': {'N4'}},
    'N4': {'bits': 2, 'current_activations_val': 0, 'valor_decimal': 0, 'connections_out': set()},
    'N5': {'bits': 6, 'current_activations_val': 2, 'valor_decimal': 7, 'connections_out': {'N1'}},
}

# --- CONFIGURACIÓN DE PYGAME ---
ANCHO_PANTALLA = 1000
ALTO_PANTALLA = 700
FPS = 60

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
GRIS = (100, 100, 100)
AMARILLO = (255, 255, 0)

# Inicializar Pygame
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Visualizador de Bynarium")
reloj = pygame.time.Clock()

# Fuente para el texto de las neuronas
fuente_neurona = pygame.font.Font(None, 24)

# --- CLASE PARA REPRESENTAR UNA NEURONA VISUALMENTE (CON SPRITE) ---
class NeuronVisual:
    def __init__(self, neuron_id, x, y, radius, color, sprite_path=None):
        self.id = neuron_id
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.sprite_path = sprite_path
        self.sprite_image = None
        self.is_active = False # Estado para el sprite

        # Cargar la imagen del sprite si se proporciona una ruta
        if self.sprite_path:
            try:
                # Usar una imagen de marcador de posición si no se puede cargar una real
                # En un entorno real, reemplazarías esto con tus rutas de imagen locales
                self.sprite_image = pygame.image.load(self.sprite_path).convert_alpha()
                # Escalar la imagen para que se ajuste al radio de la neurona
                self.sprite_image = pygame.transform.scale(self.sprite_image, (radius * 2, radius * 2))
            except pygame.error:
                print(f"Advertencia: No se pudo cargar la imagen del sprite '{self.sprite_path}'. Usando un marcador de posición.")
                # Crear un marcador de posición simple si la imagen no se carga
                self.sprite_image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(self.sprite_image, AMARILLO, (radius, radius), radius, 2) # Borde amarillo
                pygame.draw.circle(self.sprite_image, (255, 165, 0, 150), (radius, radius), radius - 2) # Relleno naranja semi-transparente

    def draw(self, screen, neuron_data):
        # Actualizar el estado de actividad basado en los datos de Bynarium
        self.is_active = neuron_data['current_activations_val'] > 0 or neuron_data['valor_decimal'] > 0

        # Dibujar la neurona (círculo)
        if self.is_active:
            pygame.draw.circle(screen, VERDE, (self.x, self.y), self.radius) # Activa: verde
        else:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius) # Inactiva: color base

        # Dibujar el sprite si existe
        if self.sprite_image:
            sprite_rect = self.sprite_image.get_rect(center=(self.x, self.y))
            screen.blit(self.sprite_image, sprite_rect)
            
            # Opcional: Cambiar el color del sprite o añadir un efecto si está activo
            if self.is_active:
                # Puedes aplicar un filtro de color o un efecto de brillo al sprite
                # Esto es un ejemplo simple, para efectos más complejos se necesita más lógica
                s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                s.fill((255, 255, 0, 50)) # Un brillo amarillo semi-transparente
                screen.blit(s, sprite_rect)

        # Dibujar el texto de ID de la neurona
        texto_id = fuente_neurona.render(self.id, True, NEGRO)
        texto_rect = texto_id.get_rect(center=(self.x, self.y - self.radius - 15))
        screen.blit(texto_id, texto_rect)

        # Dibujar el valor decimal y las activaciones
        texto_valor = fuente_neurona.render(f"Val: {neuron_data['valor_decimal']}", True, NEGRO)
        texto_activaciones = fuente_neurona.render(f"Act: {neuron_data['current_activations_val']}", True, NEGRO)
        
        texto_valor_rect = texto_valor.get_rect(center=(self.x, self.y + self.radius + 10))
        texto_activaciones_rect = texto_activaciones.get_rect(center=(self.x, self.y + self.radius + 25))
        
        screen.blit(texto_valor, texto_valor_rect)
        screen.blit(texto_activaciones, texto_activaciones_rect)

# --- FUNCIÓN PARA DIBUJAR CONEXIONES ---
def draw_connections(screen, neurons_visual, neuronas_estado_data):
    for source_id, source_neuron_data in neuronas_estado_data.items():
        if source_id in neurons_visual:
            source_pos = (neurons_visual[source_id].x, neurons_visual[source_id].y)
            for target_id in source_neuron_data['connections_out']:
                if target_id in neurons_visual:
                    target_pos = (neurons_visual[target_id].x, neurons_visual[target_id].y)
                    pygame.draw.line(screen, GRIS, source_pos, target_pos, 2)
                    # Opcional: Dibujar una flecha para indicar la dirección
                    draw_arrow(screen, GRIS, source_pos, target_pos)

def draw_arrow(screen, color, start, end):
    pygame.draw.line(screen, color, start, end, 2)
    rotation = math.degrees(math.atan2(start[1] - end[1], end[0] - start[0])) + 90
    pygame.draw.polygon(screen, color, ((end[0] + 8 * math.sin(math.radians(rotation)), end[1] + 8 * math.cos(math.radians(rotation))), \
                                        (end[0] + 8 * math.sin(math.radians(rotation - 120)), end[1] + 8 * math.cos(math.radians(rotation - 120))), \
                                        (end[0] + 8 * math.sin(math.radians(rotation + 120)), end[1] + 8 * math.cos(math.radians(rotation + 120)))))


# --- CREAR INSTANCIAS DE NEURONAS VISUALES ---
# Posiciones fijas para la demostración. En una aplicación real, podrías calcularlas dinámicamente
# o permitir que el usuario las arrastre.
neurons_visual = {
    'N1': NeuronVisual('N1', 200, 200, 40, AZUL, "https://placehold.co/80x80/0000FF/FFFFFF?text=N1"), # Reemplaza con tu ruta de imagen
    'N2': NeuronVisual('N2', 400, 100, 30, ROJO, "https://placehold.co/60x60/FF0000/FFFFFF?text=N2"),
    'N3': NeuronVisual('N3', 400, 300, 50, VERDE, "https://placehold.co/100x100/00FF00/FFFFFF?text=N3"),
    'N4': NeuronVisual('N4', 600, 200, 25, GRIS, "https://placehold.co/50x50/808080/FFFFFF?text=N4"),
    'N5': NeuronVisual('N5', 100, 400, 45, AMARILLO, "https://placehold.co/90x90/FFFF00/000000?text=N5"),
}

# --- BUCLE PRINCIPAL DEL JUEGO/SIMULACIÓN ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Aquí podrías añadir lógica para interactuar con las neuronas
        # Por ejemplo, al hacer clic en una neurona, podrías "activarla"
        # y luego actualizar neuronas_estado_simulado.
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     for neuron_id, visual_neuron in neurons_visual.items():
        #         dist = math.hypot(event.pos[0] - visual_neuron.x, event.pos[1] - visual_neuron.y)
        #         if dist <= visual_neuron.radius:
        #             print(f"Clic en neurona: {neuron_id}")
        #             # Aquí llamarías a tu lógica de Bynarium, por ejemplo:
        #             # Bynarium_NeuronasActualizadas().execute_command(f"act: {neuron_id}")
        #             # Y luego actualizarías neuronas_estado_simulado con el nuevo estado
        #             # Por ahora, solo simulamos un cambio simple
        #             if neuronas_estado_simulado[neuron_id]['current_activations_val'] < 5:
        #                 neuronas_estado_simulado[neuron_id]['current_activations_val'] += 1
        #             else:
        #                 neuronas_estado_simulado[neuron_id]['current_activations_val'] = 0 # Reset
        #             print(f"Nueva activación de {neuron_id}: {neuronas_estado_simulado[neuron_id]['current_activations_val']}")


    # --- LÓGICA DE ACTUALIZACIÓN (si hubiera animación o cambios dinámicos) ---
    # Aquí es donde podrías actualizar el estado de tus neuronas de Bynarium
    # si tuvieras un bucle de simulación automático o eventos externos.
    # Por ejemplo, podrías llamar a 'ciclo' de Bynarium aquí periódicamente.

    # --- DIBUJO ---
    pantalla.fill(BLANCO) # Limpiar la pantalla

    # Dibujar conexiones primero para que las neuronas queden encima
    draw_connections(pantalla, neurons_visual, neuronas_estado_simulado)

    # Dibujar cada neurona visual
    for neuron_id, visual_neuron in neurons_visual.items():
        if neuron_id in neuronas_estado_simulado:
            visual_neuron.draw(pantalla, neuronas_estado_simulado[neuron_id])

    pygame.display.flip() # Actualizar la pantalla

    reloj.tick(FPS) # Controlar los FPS

pygame.quit()
sys.exit()
