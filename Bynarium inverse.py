import re
import json
import time # Para el comando 'pausa'
from collections import defaultdict # Para el comando 'ciclo'

# Variable global para el registro de eventos
global_log = []

def log_event(event_type, neuron_id=None, details=None):
    """Registra un evento en el log global."""
    entry = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'event_type': event_type,
        'neuron_id': neuron_id,
        'details': details
    }
    global_log.append(entry)

def calcular_sumatoria_serie(limite_n):
    """
    Calcula la sumatoria de una serie (pares o impares) hasta el limite_n.
    Este 'limite_n' es el valor que se pasa a las fórmulas.
    """
    if limite_n <= 0:
        return 0 # Para casos como 1 bit (limite_n = 0), la sumatoria es 0

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

def estimar_sumatoria_binaria(valor):
    """
    Convierte un valor decimal en una sumatoria simbólica de números impares.
    Esta es la lógica para interpretar las activaciones actuales visibles
    basadas en el valor decimal establecido por 'mov'.
    """
    suma = 0
    serie = []
    # Solo impares, estructura simbólica
    # Se construye la sumatoria de impares que sea <= al valor dado
    for i in range(1, valor + 1, 2):
        if suma + i <= valor:
            suma += i
            serie.append(str(i))
        else:
            break
    return suma, "+".join(serie) if serie else "0"

# Función para encontrar todas las rutas entre dos nodos
def find_all_paths(graph, start, end, path=None, max_depth=10):
    """
    Encuentra todas las rutas posibles entre un nodo de inicio y un nodo final
    en un grafo representado por conexiones de neuronas.
    graph: diccionario de neuronas_estado
    start: ID de la neurona de inicio
    end: ID de la neurona de destino (opcional)
    path: lista interna para el seguimiento de la ruta actual
    max_depth: profundidad máxima de búsqueda para evitar bucles infinitos
    """
    if path is None:
        path = []
    
    path = path + [start]

    if start == end:
        return [path]
    if start not in graph:
        return []
    if len(path) > max_depth: # Limitar la profundidad para evitar bucles infinitos
        return []

    paths = []
    for node in graph[start]['connections_out']:
        if node not in path: # Evitar ciclos en la misma ruta
            new_paths = find_all_paths(graph, node, end, path, max_depth)
            for p in new_paths:
                paths.append(p)
    return paths


def Bynarium_NeuronasActualizadas():
    neuronas_estado = {}
    
    # --- Patrones Regex ---
    patron_crea = re.compile(r"crea:\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE)
    patron_out = re.compile(r"out:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_mov = re.compile(r"mov:\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE)
    patron_act = re.compile(r"act:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_inh = re.compile(r"inh:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_bif = re.compile(r"bif:\s*([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_nop = re.compile(r"nop:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    # patron_comb actualizado para capturar el operador
    patron_comb = re.compile(r"comb:\s*([A-Za-z0-9_]+)\s*(\?\+|\?-)\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_fusion = re.compile(r"fusion:\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*->\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_fus = re.compile(r"fus:\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE)
    patron_reset = re.compile(r"reset", re.IGNORECASE)
    patron_preset = re.compile(r"preset:\s*(piramide|cuadrado|invertida)\s*,\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE)
    patron_ruta = re.compile(r"ruta(?::\s*([A-Za-z0-9_]+)(?:\s*->\s*([A-Za-z0-9_]+))?)?(?:\s*(activa|completa))?", re.IGNORECASE)
    patron_guar = re.compile(r"guar", re.IGNORECASE)
    patron_carg = re.compile(r"carg", re.IGNORECASE)
    patron_loop = re.compile(r"loop:\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE)
    patron_pausa = re.compile(r"pausa:\s*(\d+)", re.IGNORECASE)
    patron_log = re.compile(r"log(?::\s*([A-Za-z0-9_]+))?", re.IGNORECASE)
    patron_eval = re.compile(r"eval", re.IGNORECASE)
    patron_ciclo = re.compile(r"ciclo", re.IGNORECASE)
    patron_evento = re.compile(r"evento:\s*([A-Za-z0-9_]+)\s*,\s*(act_gt|val_eq)\s*,\s*(\d+)\s*,\s*([A-Za-z0-9_]+)\s*,\s*(act|inh)", re.IGNORECASE)
    patron_copia = re.compile(r"copia:\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_help = re.compile(r"help|ayuda", re.IGNORECASE)
    patron_help_specific = re.compile(r"(help|ayuda)\s+with\s+([A-Za-z]+)", re.IGNORECASE)
    patron_topo = re.compile(r"topo:\s*([A-Za-z0-9_]+)?", re.IGNORECASE)

    while True:
        comand = input("\nEscribe tu comando (help para comandos; salir para terminar): ").strip()
        if comand.lower() == "salir":
            print("Saliendo de Bynarium. ¡Hasta pronto!")
            break

        # --- Procesamiento de Comandos ---

        # Comando 'crea'
        match_crea = patron_crea.match(comand)
        if match_crea:
            id_neurona = match_crea.group(1).upper()
            bits_str = match_crea.group(2)
            try:
                bits_int = int(bits_str)
                if bits_int < 1:
                    print("Error: El número de bits debe ser un entero positivo.")
                elif id_neurona in neuronas_estado:
                    print(f"Error: La neurona '{id_neurona}' ya existe.")
                else:
                    formula_limit_n = bits_int - 1
                    if formula_limit_n < 0:
                        formula_limit_n = 0
                        
                    max_activations_capacity_val = int(calcular_sumatoria_serie(formula_limit_n))
                    max_activations_capacity_str = generar_sumatoria_str(formula_limit_n)
                    
                    current_activations_val = 0
                    current_activations_str = "0"

                    neuronas_estado[id_neurona] = {
                        'bits': bits_int,
                        'formula_limit_n': formula_limit_n,
                        'max_activations_capacity_val': max_activations_capacity_val,
                        'max_activations_capacity_str': max_activations_capacity_str,
                        'current_activations_val': current_activations_val,
                        'current_activations_str': current_activations_str,
                        'valor_decimal': 0,
                        'valor_binario_str': bin(0)[2:].zfill(bits_int),
                        'connections_out': set()
                    }
                    print(f"Neurona '{id_neurona}' creada con {bits_int} bits.")
                    print(f"   El límite para la fórmula de sumatoria (Bits-1) es: {formula_limit_n}")
                    print(f"   La capacidad total de activaciones para esta neurona es: {max_activations_capacity_str} (valor: {max_activations_capacity_val})")
                    print(f"   Valor inicial: {neuronas_estado[id_neurona]['valor_binario_str']} (decimal: {neuronas_estado[id_neurona]['valor_decimal']})")
                    log_event('crea', id_neurona, {'bits': bits_int})
            except ValueError:
                print(f"Error: El número de bits '{bits_str}' no es un entero válido.")
            continue

        # Comando 'out' (muestra el estado actual de una neurona)
        match_out = patron_out.match(comand)
        if match_out:
            id_neurona = match_out.group(1).upper()
            if id_neurona in neuronas_estado:
                estado = neuronas_estado[id_neurona]
                print(f"--- Estado de Neurona '{id_neurona}' ---")
                print(f"   Bits: {estado['bits']}")
                print(f"   Límite para Sumatoria (Bits-1): {estado['formula_limit_n']}")
                print(f"   Capacidad Máxima de Activaciones: {estado['max_activations_capacity_str']} (valor: {estado['max_activations_capacity_val']})")
                print(f"   Activaciones Actuales: {estado['current_activations_str']} (valor: {estado['current_activations_val']})")
                print(f"   Valor Decimal: {estado['valor_decimal']}")
                print(f"   Valor Binario: {estado['valor_binario_str']}")
                print(f"   Conexiones de Salida: {', '.join(sorted(list(estado['connections_out']))) if estado['connections_out'] else 'Ninguna'}")
            else:
                print(f"Error: La neurona '{id_neurona}' no existe. Usa 'crea:' para crearla primero.")
            continue

        # Comando 'mov' (establece el valor decimal y binario de la neurona)
        match_mov = patron_mov.match(comand)
        if match_mov:
            id_neurona = match_mov.group(1).upper()
            nuevo_valor_decimal_str = match_mov.group(2)
            if id_neurona not in neuronas_estado:
                print(f"Error: La neurona '{id_neurona}' no existe.")
                continue
            
            try:
                nuevo_valor_decimal = int(nuevo_valor_decimal_str)
                bits_requeridos = neuronas_estado[id_neurona]['bits']
                max_valor_decimal = (2 ** bits_requeridos) - 1
                
                if nuevo_valor_decimal < 0 or nuevo_valor_decimal > max_valor_decimal:
                    print(f"Error: El valor {nuevo_valor_decimal} excede el rango para {bits_requeridos} bits (0 a {max_valor_decimal}).")
                    print(f"   Para almacenar este valor, la neurona '{id_neurona}' necesitaría más bits.")
                    continue
                
                old_valor_decimal = neuronas_estado[id_neurona]['valor_decimal']
                old_valor_binario_str = neuronas_estado[id_neurona]['valor_binario_str']

                neuronas_estado[id_neurona]['valor_decimal'] = nuevo_valor_decimal
                neuronas_estado[id_neurona]['valor_binario_str'] = bin(nuevo_valor_decimal)[2:].zfill(bits_requeridos)

                activ_val, activ_str = estimar_sumatoria_binaria(nuevo_valor_decimal)
                neuronas_estado[id_neurona]['current_activations_val'] = activ_val
                neuronas_estado[id_neurona]['current_activations_str'] = activ_str
                
                print(f"Comando 'mov' detectado: Neurona '{id_neurona}' actualizada a valor: {neuronas_estado[id_neurona]['valor_decimal']} (binario: {neuronas_estado[id_neurona]['valor_binario_str']})")
                print(f"   Activaciones simbólicas interpretadas como: {activ_str} (valor: {activ_val})")
                log_event('mov', id_neurona, {'old_decimal': old_valor_decimal, 'new_decimal': nuevo_valor_decimal, 'old_bin': old_valor_binario_str, 'new_bin': neuronas_estado[id_neurona]['valor_binario_str'], 'activations': activ_val})
            except ValueError:
                print(f"Error: El valor '{nuevo_valor_decimal_str}' en 'mov' no es un entero válido.")
            continue

        # Comando 'act' (incrementa current_activations hasta max_activations_capacity)
        match_act = patron_act.match(comand)
        if match_act:
            id_neurona = match_act.group(1).upper()
            if id_neurona in neuronas_estado:
                neurona = neuronas_estado[id_neurona]
                old_activations = neurona['current_activations_val']
                if neurona['current_activations_val'] < neurona['max_activations_capacity_val']:
                    neurona['current_activations_val'] += 1
                    neurona['current_activations_str'] = str(neurona['current_activations_val'])
                    print(f"Neurona '{id_neurona}' activada.")
                    print(f"   Activaciones actuales: {neurona['current_activations_str']} (Capacidad total: {neurona['max_activations_capacity_str']} | valor: {neurona['max_activations_capacity_val']}).")
                    log_event('act', id_neurona, {'old_activations': old_activations, 'new_activations': neurona['current_activations_val']})
                else:
                    print(f"Neurona '{id_neurona}' ya alcanzó su capacidad máxima de activaciones ({neurona['max_activations_capacity_str']} | valor: {neurona['max_activations_capacity_val']}).")
            else:
                print(f"Error: La neurona '{id_neurona}' no existe.")
            continue
        
        # Comandos 'inh', 'bif', 'nop'
        match_inh = patron_inh.match(comand)
        if match_inh:
            id_neurona = match_inh.group(1).upper()
            if id_neurona in neuronas_estado:
                neurona = neuronas_estado[id_neurona]
                old_activations = neurona['current_activations_val']
                if neurona['current_activations_val'] > 0:
                    neurona['current_activations_val'] -= 1
                    neurona['current_activations_str'] = str(neurona['current_activations_val'])
                    print(f"Neurona '{id_neurona}' inhibida. Activaciones actuales: {neurona['current_activations_str']}.")
                    log_event('inh', id_neurona, {'old_activations': old_activations, 'new_activations': neurona['current_activations_val']})
                else:
                    print(f"Neurona '{id_neurona}' ya está en su activación mínima (0).")
            else:
                print(f"Error: La neurona '{id_neurona}' no existe.")
            continue

        match_bif = patron_bif.match(comand)
        if match_bif:
            origen_id = match_bif.group(1).upper()
            destino1_id = match_bif.group(2).upper()
            destino2_id = match_bif.group(3).upper()

            if origen_id in neuronas_estado and destino1_id in neuronas_estado and destino2_id in neuronas_estado:
                neurona_origen = neuronas_estado[origen_id]
                neurona_destino1 = neuronas_estado[destino1_id]
                neurona_destino2 = neuronas_estado[destino2_id]

                if neurona_origen['current_activations_val'] >= 2: 
                    old_origen_activations = neurona_origen['current_activations_val']
                    old_destino1_activations = neurona_destino1['current_activations_val']
                    old_destino2_activations = neurona_destino2['current_activations_val']

                    neurona_origen['current_activations_val'] -= 2 
                    neurona_origen['current_activations_str'] = str(neurona_origen['current_activations_val'])
                    
                    neurona_destino1['current_activations_val'] = min(neurona_destino1['current_activations_val'] + 1, neurona_destino1['max_activations_capacity_val'])
                    neurona_destino1['current_activations_str'] = str(neurona_destino1['current_activations_val'])
                    neurona_destino2['current_activations_val'] = min(neurona_destino2['current_activations_val'] + 1, neurona_destino2['max_activations_capacity_val'])
                    neurona_destino2['current_activations_str'] = str(neurona_destino2['current_activations_val'])
                    
                    neurona_origen['connections_out'].add(destino1_id)
                    neurona_origen['connections_out'].add(destino2_id)

                    print(f"Bifurcación de '{origen_id}' a '{destino1_id}' y '{destino2_id}'.")
                    print(f"   '{origen_id}' (activaciones: {neurona_origen['current_activations_str']})")
                    print(f"   '{destino1_id}' (activaciones: {neurona_destino1['current_activations_str']})")
                    print(f"   '{destino2_id}' (activaciones: {neurona_destino2['current_activations_str']})")
                    log_event('bif', origen_id, {
                        'destinos': [destino1_id, destino2_id],
                        'origen_old_activations': old_origen_activations,
                        'origen_new_activations': neurona_origen['current_activations_val'],
                        'destino1_old_activations': old_destino1_activations,
                        'destino1_new_activations': neurona_destino1['current_activations_val'],
                        'destino2_old_activations': old_destino2_activations,
                        'destino2_new_activations': neurona_destino2['current_activations_val']
                    })
                else:
                    print(f"La neurona '{origen_id}' necesita al menos 2 activaciones para bifurcar.")
            else:
                print("Error: Una o más neuronas especificadas para la bifurcación no existen.")
            continue

        match_nop = patron_nop.match(comand)
        if match_nop:
            id_neurona = match_nop.group(1).upper()
            if id_neurona in neuronas_estado:
                print(f"Neurona '{id_neurona}' mantendrá su estado actual de activaciones: {neuronas_estado[id_neurona]['current_activations_str']}. (Operación 'nop').")
                log_event('nop', id_neurona, {'activations': neuronas_estado[id_neurona]['current_activations_val']})
            else:
                print(f"Error: La neurona '{id_neurona}' no existe.")
            continue
            
        # Comando 'comb' (combina la capacidad de dos neuronas o descombina)
        match_comb = patron_comb.match(comand)
        if match_comb:
            id1 = match_comb.group(1).upper()
            operator = match_comb.group(2)
            id2 = match_comb.group(3).upper()

            if id1 not in neuronas_estado:
                print(f"Error: La neurona '{id1}' no existe.")
                continue
            if id2 not in neuronas_estado:
                print(f"Error: La neurona '{id2}' no existe.")
                continue
            if id1 == id2:
                print("Error: No puedes operar una neurona consigo misma.")
                continue

            if operator == '?+':
                id_vacia = id1
                id_llena = id2
                neurona_vacia = neuronas_estado[id_vacia]
                neurona_llena = neuronas_estado[id_llena]

                if neurona_llena['bits'] < 3: 
                    print(f"Error: La neurona '{id_llena}' (llena) debe tener al menos 3 bits para poder ceder uno y recalcular sus activaciones.")
                    continue

                # Guardar valores antiguos para el mensaje de salida y log
                old_bits_vacia = neurona_vacia['bits']
                old_capacity_vacia_str = neurona_vacia['max_activations_capacity_str']
                old_activations_vacia_str = neurona_vacia['current_activations_str']
                old_valor_decimal_vacia = neurona_vacia['valor_decimal']
                old_valor_binario_vacia = neurona_vacia['valor_binario_str']

                old_bits_llena = neurona_llena['bits']
                old_capacity_llena_str = neurona_llena['max_activations_capacity_str']
                old_activations_llena_str = neurona_llena['current_activations_str']
                old_valor_decimal_llena = neurona_llena['valor_decimal']
                old_valor_binario_llena = neurona_llena['valor_binario_str']

                # 1. Ajuste del número de bits
                neurona_vacia['bits'] += 1
                neurona_llena['bits'] -= 1

                # 2. Recálculo de la capacidad de activaciones (max_activations_capacity)
                new_formula_limit_vacia = neurona_vacia['bits'] - 1
                neurona_vacia['formula_limit_n'] = new_formula_limit_vacia
                neurona_vacia['max_activations_capacity_val'] = int(calcular_sumatoria_serie(new_formula_limit_vacia))
                neurona_vacia['max_activations_capacity_str'] = generar_sumatoria_str(new_formula_limit_vacia)

                new_formula_limit_llena = neurona_llena['bits'] - 2
                if new_formula_limit_llena < 0:
                    new_formula_limit_llena = 0 
                neurona_llena['formula_limit_n'] = new_formula_limit_llena
                neurona_llena['max_activations_capacity_val'] = int(calcular_sumatoria_serie(new_formula_limit_llena))
                neurona_llena['max_activations_capacity_str'] = generar_sumatoria_str(new_formula_limit_llena)

                # 3. Ajuste de current_activations
                neurona_vacia['current_activations_val'] = 0
                neurona_vacia['current_activations_str'] = "0"

                neurona_llena['current_activations_val'] = neurona_llena['max_activations_capacity_val']
                neurona_llena['current_activations_str'] = neurona_llena['max_activations_capacity_str']

                # 4. Ajuste de valor_decimal y valor_binario_str (reiniciar a 0)
                neurona_vacia['valor_decimal'] = 0
                neurona_vacia['valor_binario_str'] = bin(0)[2:].zfill(neurona_vacia['bits'])
                
                neurona_llena['valor_decimal'] = 0
                neurona_llena['valor_binario_str'] = bin(0)[2:].zfill(neurona_llena['bits'])

                print(f"\n--- Operación 'comb' (?+) realizada entre '{id_vacia}' y '{id_llena}' ---")
                print(f"Neurona '{id_vacia}' (vacía):")
                print(f"   Bits: {old_bits_vacia} -> {neurona_vacia['bits']}")
                print(f"   Capacidad: {old_capacity_vacia_str} (valor: {neurona_vacia['max_activations_capacity_val']}) -> {neurona_vacia['max_activations_capacity_str']} (valor: {neurona_vacia['max_activations_capacity_val']})")
                print(f"   Activaciones: {old_activations_vacia_str} (valor: {neurona_vacia['current_activations_val']}) -> {neurona_vacia['current_activations_str']} (valor: {neurona_vacia['current_activations_val']})")
                print(f"   Valor Binario: {neurona_vacia['valor_binario_str']}")

                print(f"Neurona '{id_llena}' (llena):")
                print(f"   Bits: {old_bits_llena} -> {neurona_llena['bits']}")
                print(f"   Capacidad: {old_capacity_llena_str} (valor: {neurona_llena['max_activations_capacity_val']}) -> {neurona_llena['max_activations_capacity_str']} (valor: {neurona_llena['max_activations_capacity_val']})")
                print(f"   Activaciones: {old_activations_llena_str} (valor: {neurona_llena['current_activations_val']}) -> {neurona_llena['current_activations_str']} (valor: {neurona_llena['current_activations_val']})")
                print(f"   Valor Binario: {neurona_llena['valor_binario_str']}")
                log_event('comb_plus', None, {
                    'vacia_id': id_vacia, 'vacia_old_bits': old_bits_vacia, 'vacia_new_bits': neurona_vacia['bits'],
                    'vacia_old_activations': old_activations_vacia_str, 'vacia_new_activations': neurona_vacia['current_activations_str'],
                    'vacia_old_decimal': old_valor_decimal_vacia, 'vacia_new_decimal': neurona_vacia['valor_decimal'],
                    'llena_id': id_llena, 'llena_old_bits': old_bits_llena, 'llena_new_bits': neurona_llena['bits'],
                    'llena_old_activations': old_activations_llena_str, 'llena_new_activations': neurona_llena['current_activations_str'],
                    'llena_old_decimal': old_valor_decimal_llena, 'llena_new_decimal': neurona_llena['valor_decimal']
                })

            elif operator == '?-':
                # Identificar A (mayor NB) y B (menor NB)
                neuron1 = neuronas_estado[id1]
                neuron2 = neuronas_estado[id2]

                if neuron1['bits'] > neuron2['bits']:
                    id_A = id1
                    id_B = id2
                    neurona_A = neuron1
                    neurona_B = neuron2
                elif neuron2['bits'] > neuron1['bits']:
                    id_A = id2
                    id_B = id1
                    neurona_A = neuron2
                    neurona_B = neuron1
                else:
                    print(f"Error: Para la operación '?-', las neuronas deben tener un número de bits diferente.")
                    continue

                # Verificar condiciones
                nb_A = neurona_A['bits']
                nb_B = neurona_B['bits']

                if not (nb_A % 2 != 0 and nb_B % 2 != 0):
                    print(f"Error: Para '?-', ambos números de bits ({nb_A} y {nb_B}) deben ser impares.")
                    continue
                
                if abs(nb_A - nb_B) != 2:
                    print(f"Error: Para '?-', la diferencia absoluta entre los números de bits ({nb_A} y {nb_B}) debe ser 2.")
                    continue

                nb_m = (nb_A + nb_B) // 2

                # Guardar estados antiguos para el log y la salida
                old_state_A = neurona_A.copy()
                old_state_B = neurona_B.copy()

                # Modificar Neurona A (mayor NB, se convierte en "intermedia, vacía pero válida")
                neurona_A['bits'] = nb_m
                neurona_A['formula_limit_n'] = nb_m - 1
                neurona_A['max_activations_capacity_val'] = int(calcular_sumatoria_serie(neurona_A['formula_limit_n']))
                neurona_A['max_activations_capacity_str'] = generar_sumatoria_str(neurona_A['formula_limit_n'])
                
                # Según ejemplo: 1000 (decimal 8) para NB_m = 4 bits
                neurona_A['valor_decimal'] = 8
                neurona_A['valor_binario_str'] = bin(8)[2:].zfill(nb_m)
                activ_val_A, activ_str_A = estimar_sumatoria_binaria(neurona_A['valor_decimal'])
                neurona_A['current_activations_val'] = activ_val_A
                neurona_A['current_activations_str'] = activ_str_A
                neurona_A['connections_out'].clear() # Limpiar conexiones

                # Modificar Neurona B (menor NB, se convierte en "casi llena")
                neurona_B['bits'] = nb_m
                neurona_B['formula_limit_n'] = nb_m - 1
                neurona_B['max_activations_capacity_val'] = int(calcular_sumatoria_serie(neurona_B['formula_limit_n']))
                neurona_B['max_activations_capacity_str'] = generar_sumatoria_str(neurona_B['formula_limit_n'])
                
                # Según ejemplo: 0100 (decimal 4) para NB_m = 4 bits
                neurona_B['valor_decimal'] = 4
                neurona_B['valor_binario_str'] = bin(4)[2:].zfill(nb_m)
                activ_val_B, activ_str_B = estimar_sumatoria_binaria(neurona_B['valor_decimal'])
                neurona_B['current_activations_val'] = activ_val_B
                neurona_B['current_activations_str'] = activ_str_B
                neurona_B['connections_out'].clear() # Limpiar conexiones
                
                print(f"\n--- Operación 'comb' (?-: Desombidicionar) realizada entre '{id_A}' y '{id_B}' ---")
                print(f"Neurona '{id_A}' (anteriormente {old_state_A['bits']} bits) ahora es una estructura intermedia de {nb_m} bits.")
                print(f"   Valor Decimal: {neurona_A['valor_decimal']} (Binario: {neurona_A['valor_binario_str']})")
                print(f"   Activaciones: {neurona_A['current_activations_str']} (valor: {neurona_A['current_activations_val']})")
                print(f"Neurona '{id_B}' (anteriormente {old_state_B['bits']} bits) ahora es una estructura casi llena de {nb_m} bits.")
                print(f"   Valor Decimal: {neurona_B['valor_decimal']} (Binario: {neurona_B['valor_binario_str']})")
                print(f"   Activaciones: {neurona_B['current_activations_str']} (valor: {neurona_B['current_activations_val']})")
                log_event('desombidicionar', None, {
                    'neuron_A_id': id_A, 'neuron_A_old_bits': old_state_A['bits'], 'neuron_A_new_bits': nb_m,
                    'neuron_A_new_decimal': neurona_A['valor_decimal'], 'neuron_A_new_activations': neurona_A['current_activations_val'],
                    'neuron_B_id': id_B, 'neuron_B_old_bits': old_state_B['bits'], 'neuron_B_new_bits': nb_m,
                    'neuron_B_new_decimal': neurona_B['valor_decimal'], 'neuron_B_new_activations': neurona_B['current_activations_val']
                })
            continue # Fin del comando 'comb'

        # Comando 'fusion' (bifurcación inversa/fusión)
        match_fusion = patron_fusion.match(comand)
        if match_fusion:
            id_origen1 = match_fusion.group(1).upper()
            id_origen2 = match_fusion.group(2).upper()
            id_destino = match_fusion.group(3).upper()

            # Validaciones
            if id_origen1 not in neuronas_estado:
                print(f"Error: La neurona '{id_origen1}' (origen 1) no existe.")
                continue
            if id_origen2 not in neuronas_estado:
                print(f"Error: La neurona '{id_origen2}' (origen 2) no existe.")
                continue
            if id_destino not in neuronas_estado:
                print(f"Error: La neurona '{id_destino}' (destino) no existe.")
                continue
            if id_origen1 == id_destino or id_origen2 == id_destino or id_origen1 == id_origen2:
                print("Error: Las neuronas origen y destino deben ser distintas.")
                continue

            neurona_origen1 = neuronas_estado[id_origen1]
            neurona_origen2 = neuronas_estado[id_origen2]
            neurona_destino = neuronas_estado[id_destino]

            # Regla: ambos orígenes deben estar activos o contener estructura binaria válida (valor_decimal > 0)
            if neurona_origen1['valor_decimal'] == 0 and neurona_origen2['valor_decimal'] == 0:
                print("Error: Ambas neuronas origen deben contener una estructura binaria válida (valor decimal > 0) para fusionarse.")
                continue
            
            # Regla: el destino debe estar vacío
            if neurona_destino['valor_decimal'] != 0 or neurona_destino['current_activations_val'] != 0:
                print(f"Error: La neurona destino '{id_destino}' no está vacía. Operación abortada.")
                continue

            # 1. Combinación binaria: concatenación
            combined_bin_str = neurona_origen1['valor_binario_str'] + neurona_origen2['valor_binario_str']
            final_bin_str = combined_bin_str
            fuga_message = ""
            conflict_f2 = False

            # 2. Simplificación y chequeo de conflicto
            if combined_bin_str == "1001":
                final_bin_str = "100"
                fuga_message = " (y fuga de 1)"
            elif "11" in combined_bin_str: # Regla general "sin 11"
                conflict_f2 = True
                print(f"Error: Colisión lógica (F2) - la combinación binaria '{combined_bin_str}' contiene '11'. Operación abortada.")
                continue # Abortar la operación

            # Convertir la cadena binaria final a decimal
            new_decimal_destino_val = int(final_bin_str, 2)
            
            # 3. Validar capacidad del destino
            max_val_destino = (2 ** neurona_destino['bits']) - 1
            if new_decimal_destino_val > max_val_destino:
                print(f"Error: La neurona destino '{id_destino}' (con {neurona_destino['bits']} bits) no tiene suficiente capacidad para el valor combinado ({new_decimal_destino_val}). Operación abortada.")
                continue

            # Guardar estados antiguos para el mensaje de salida y log
            old_origen1_bin = neurona_origen1['valor_binario_str']
            old_origen2_bin = neurona_origen2['valor_binario_str']
            old_destino_bin = neurona_destino['valor_binario_str']

            # 4. Actualizar neurona destino
            neurona_destino['valor_decimal'] = new_decimal_destino_val
            neurona_destino['valor_binario_str'] = final_bin_str.zfill(neurona_destino['bits']) # Asegurar que tenga los bits del destino

            # Recalcular activaciones simbólicas para el destino
            activ_val_destino, activ_str_destino = estimar_sumatoria_binaria(new_decimal_destino_val)
            neurona_destino['current_activations_val'] = activ_val_destino
            neurona_destino['current_activations_str'] = activ_str_destino

            # 5. Resetear neuronas origen
            neurona_origen1['valor_decimal'] = 0
            neurona_origen1['valor_binario_str'] = bin(0)[2:].zfill(neurona_origen1['bits'])
            neurona_origen1['current_activations_val'] = 0
            neurona_origen1['current_activations_str'] = "0"
            neurona_origen1['connections_out'].clear()

            neurona_origen2['valor_decimal'] = 0
            neurona_origen2['valor_binario_str'] = bin(0)[2:].zfill(neurona_origen2['bits'])
            neurona_origen2['current_activations_val'] = 0
            neurona_origen2['current_activations_str'] = "0"
            neurona_origen2['connections_out'].clear()

            print(f"\n--- Operación 'fusion' realizada: '{id_origen1}' ({old_origen1_bin}) y '{id_origen2}' ({old_origen2_bin}) se fusionan en '{id_destino}' ---")
            print(f"   Cadena binaria combinada: {combined_bin_str}{fuga_message}")
            print(f"   Neurona '{id_destino}' ahora tiene valor: {neurona_destino['valor_decimal']} (binario: {neurona_destino['valor_binario_str']})")
            print(f"   Activaciones: {neurona_destino['current_activations_str']} (valor: {neurona_destino['current_activations_val']})")
            log_event('fusion', id_destino, {
                'origen1': id_origen1, 'origen2': id_origen2,
                'combined_bin_str': combined_bin_str, 'final_bin_str': final_bin_str,
                'fuga_message': fuga_message, 'new_decimal_destino': new_decimal_destino_val
            })
            continue

        # Comando 'fus' (transferir activaciones)
        match_fus = patron_fus.match(comand)
        if match_fus:
            id_origen = match_fus.group(1).upper()
            id_destino = match_fus.group(2).upper()
            cantidad_str = match_fus.group(3)

            # Validaciones
            if id_origen not in neuronas_estado:
                print(f"Error: La neurona '{id_origen}' (origen) no existe.")
                continue
            if id_destino not in neuronas_estado:
                print(f"Error: La neurona '{id_destino}' (destino) no existe.")
                continue
            if id_origen == id_destino:
                print("Error: No puedes transferir activaciones a la misma neurona.")
                continue

            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    print("Error: La cantidad de activaciones a transferir debe ser un número positivo.")
                    continue
            except ValueError:
                print(f"Error: La cantidad '{cantidad_str}' no es un número válido.")
                continue

            neurona_origen = neuronas_estado[id_origen]
            neurona_destino = neuronas_estado[id_destino]

            if neurona_origen['current_activations_val'] < cantidad:
                print(f"Error: La neurona '{id_origen}' solo tiene {neurona_origen['current_activations_str']} activaciones, no suficientes para transferir {cantidad}.")
                continue

            espacio_disponible_destino = neurona_destino['max_activations_capacity_val'] - neurona_destino['current_activations_val']
            
            activaciones_a_transferir_real = min(cantidad, espacio_disponible_destino)

            if activaciones_a_transferir_real == 0:
                print(f"La neurona '{id_destino}' ya está llena o no tiene espacio para recibir activaciones. No se transfirió nada.")
                continue
            
            old_origen_activations = neurona_origen['current_activations_val']
            old_destino_activations = neurona_destino['current_activations_val']

            neurona_origen['current_activations_val'] -= activaciones_a_transferir_real
            neurona_origen['current_activations_str'] = str(neurona_origen['current_activations_val'])

            neurona_destino['current_activations_val'] += activaciones_a_transferir_real
            neurona_destino['current_activations_str'] = str(neurona_destino['current_activations_val'])

            neurona_origen['connections_out'].add(id_destino)

            print(f"\n--- Operación 'fus' (transferencia) realizada ---")
            print(f"Se transfirieron {activaciones_a_transferir_real} activaciones de '{id_origen}' a '{id_destino}'.")
            print(f"   '{id_origen}' activaciones actuales: {neurona_origen['current_activations_str']}")
            print(f"   '{id_destino}' activaciones actuales: {neurona_destino['current_activations_str']}")
            
            if activaciones_a_transferir_real < cantidad:
                print(f"Nota: Solo se pudieron transferir {activaciones_a_transferir_real} de {cantidad} activaciones solicitadas, debido a la capacidad de '{id_destino}'.")
            log_event('fus', id_origen, {
                'destino': id_destino, 'cantidad_transferida': activaciones_a_transferir_real,
                'origen_old_activations': old_origen_activations, 'origen_new_activations': neurona_origen['current_activations_val'],
                'destino_old_activations': old_destino_activations, 'destino_new_activations': neurona_destino['current_activations_val']
            })
            continue

        # Comando 'reset' (eliminar todas las neuronas)
        match_reset = patron_reset.match(comand)
        if match_reset:
            neuronas_estado.clear()
            global_log.clear() # Limpiar el log también
            print("Todas las neuronas han sido eliminadas. Bynarium reiniciado.")
            log_event('reset', None, {'message': 'Todas las neuronas eliminadas y log limpiado.'})
            continue
            
        # Comando 'preset'
        match_preset = patron_preset.match(comand)
        if match_preset:
            topology_type = match_preset.group(1).lower()
            id_prefix = match_preset.group(2).upper()
            initial_quantity_str = match_preset.group(3)
            
            try:
                initial_quantity = int(initial_quantity_str)
                if initial_quantity < 1:
                    print("Error: La cantidad inicial de nodos debe ser un entero positivo.")
                    continue
            except ValueError:
                print(f"Error: La cantidad inicial '{initial_quantity_str}' no es un entero válido.")
                continue

            layers_config = []
            if topology_type == "piramide":
                layers_config.append({'bits': 2, 'quantity': initial_quantity})
                layers_config.append({'bits': 3, 'quantity': initial_quantity // 2})
                layers_config.append({'bits': 4, 'quantity': (initial_quantity // 2) // 2})
            elif topology_type == "cuadrado":
                layers_config.append({'bits': 2, 'quantity': initial_quantity})
                layers_config.append({'bits': 3, 'quantity': initial_quantity})
                layers_config.append({'bits': 4, 'quantity': initial_quantity})
            elif topology_type == "invertida":
                layers_config.append({'bits': 2, 'quantity': initial_quantity})
                layers_config.append({'bits': 3, 'quantity': initial_quantity * 2})
                layers_config.append({'bits': 4, 'quantity': initial_quantity * 4})
            
            created_neurons_count = 0
            
            layers_neuron_ids = [[] for _ in layers_config]

            # Verificar conflictos de ID antes de crear cualquier neurona
            conflict_found = False
            for layer_idx, layer_info in enumerate(layers_config):
                layer_num = layer_idx + 1
                for node_idx in range(1, layer_info['quantity'] + 1):
                    new_id = f"{id_prefix}{layer_num}{node_idx}"
                    if new_id in neuronas_estado:
                        print(f"Error: El ID de neurona '{new_id}' ya existe. La creación del preset '{topology_type}' ha sido abortada para evitar conflictos.")
                        conflict_found = True
                        break
                if conflict_found:
                    break
            
            if conflict_found:
                continue # Abortar la creación del preset

            # Si no hay conflictos, proceder con la creación de neuronas
            print(f"\n--- Creando preset '{topology_type}' con prefijo '{id_prefix}' y cantidad inicial {initial_quantity} ---")
            newly_created_ids = []
            for layer_idx, layer_info in enumerate(layers_config):
                layer_num = layer_idx + 1
                bits_for_layer = layer_info['bits']
                quantity_for_layer = layer_info['quantity']
                
                print(f"  Capa {layer_num} ({quantity_for_layer} nodos de {bits_for_layer} bits):")
                for node_idx in range(1, quantity_for_layer + 1):
                    id_neurona = f"{id_prefix}{layer_num}{node_idx}"
                    
                    formula_limit_n = bits_for_layer - 1
                    if formula_limit_n < 0:
                        formula_limit_n = 0
                    max_activations_capacity_val = int(calcular_sumatoria_serie(formula_limit_n))
                    max_activations_capacity_str = generar_sumatoria_str(formula_limit_n)
                    
                    neuronas_estado[id_neurona] = {
                        'bits': bits_for_layer,
                        'formula_limit_n': formula_limit_n,
                        'max_activations_capacity_val': max_activations_capacity_val,
                        'max_activations_capacity_str': max_activations_capacity_str,
                        'current_activations_val': 0,
                        'current_activations_str': "0",
                        'valor_decimal': 0,
                        'valor_binario_str': bin(0)[2:].zfill(bits_for_layer),
                        'connections_out': set()
                    }
                    layers_neuron_ids[layer_idx].append(id_neurona)
                    newly_created_ids.append(id_neurona)
                    print(f"    - Neurona '{id_neurona}' creada.")
                    created_neurons_count += 1
            
            # Establecer conexiones entre capas
            connections_made = []
            print("  Estableciendo conexiones entre capas...")
            for i in range(len(layers_config) - 1):
                current_layer_ids = layers_neuron_ids[i]
                next_layer_ids = layers_neuron_ids[i+1]
                
                if topology_type == "piramide":
                    for j, source_id in enumerate(current_layer_ids):
                        target_index = j // 2
                        if target_index < len(next_layer_ids):
                            target_id = next_layer_ids[target_index]
                            neuronas_estado[source_id]['connections_out'].add(target_id)
                            connections_made.append(f"{source_id} -> {target_id}")
                elif topology_type == "cuadrado":
                    for j, source_id in enumerate(current_layer_ids):
                        if j < len(next_layer_ids):
                            target_id = next_layer_ids[j]
                            neuronas_estado[source_id]['connections_out'].add(target_id)
                            connections_made.append(f"{source_id} -> {target_id}")
                elif topology_type == "invertida":
                    for j, source_id in enumerate(current_layer_ids):
                        target_index1 = j * 2
                        target_index2 = j * 2 + 1
                        if target_index1 < len(next_layer_ids):
                            target_id1 = next_layer_ids[target_index1]
                            neuronas_estado[source_id]['connections_out'].add(target_id1)
                            connections_made.append(f"{source_id} -> {target_id1}")
                        if target_index2 < len(next_layer_ids):
                            target_id2 = next_layer_ids[target_index2]
                            neuronas_estado[source_id]['connections_out'].add(target_id2)
                            connections_made.append(f"{source_id} -> {target_id2}")
            
            print(f"Preset '{topology_type}' creado exitosamente. Total de {created_neurons_count} neuronas creadas y conectadas.")
            log_event('preset', None, {
                'type': topology_type, 'prefix': id_prefix, 'initial_quantity': initial_quantity,
                'created_neurons': newly_created_ids, 'connections_made': connections_made
            })
            continue

        # Comando 'ruta'
        match_ruta = patron_ruta.match(comand)
        if match_ruta:
            start_node_id = match_ruta.group(1)
            end_node_id = match_ruta.group(2)
            option = match_ruta.group(3)

            if option == "completa":
                print("\n--- MAPA COMPLETO DE LA RED (Conexiones Directas) ---")
                if not neuronas_estado:
                    print("No hay neuronas creadas.")
                    log_event('ruta', None, {'type': 'completa', 'result': 'no neurons'})
                    continue
                for neuron_id, data in neuronas_estado.items():
                    connections = sorted(list(data['connections_out']))
                    print(f"• {neuron_id} -> {', '.join(connections) if connections else 'Ninguna'}")
                log_event('ruta', None, {'type': 'completa', 'result': 'displayed'})
                continue

            if start_node_id:
                start_node_id = start_node_id.upper()
                if start_node_id not in neuronas_estado:
                    print(f"Error: La neurona de inicio '{start_node_id}' no existe.")
                    log_event('ruta', start_node_id, {'error': 'start neuron not found'})
                    continue

                if end_node_id: # ruta: ID_Origen -> ID_Destino
                    end_node_id = end_node_id.upper()
                    if end_node_id not in neuronas_estado:
                        print(f"Error: La neurona de destino '{end_node_id}' no existe.")
                        log_event('ruta', end_node_id, {'error': 'end neuron not found'})
                        continue
                    
                    print(f"\n--- RUTAS DE '{start_node_id}' A '{end_node_id}' ---")
                    paths = find_all_paths(neuronas_estado, start_node_id, end_node_id)
                    if paths:
                        for i, p in enumerate(paths):
                            path_str = " -> ".join(p)
                            is_active = all(neuronas_estado[node]['current_activations_val'] > 0 or neuronas_estado[node]['valor_decimal'] > 0 for node in p)
                            status = " (ACTIVA)" if is_active else ""
                            print(f"  Ruta {i+1}: {path_str}{status}")
                        log_event('ruta', start_node_id, {'type': 'specific', 'target': end_node_id, 'paths_found': len(paths)})
                    else:
                        print(f"No se encontraron rutas de '{start_node_id}' a '{end_node_id}'.")
                        log_event('ruta', start_node_id, {'type': 'specific', 'target': end_node_id, 'paths_found': 0})

                else: # ruta: ID_Origen
                    print(f"\n--- TODAS LAS RUTAS DESDE '{start_node_id}' ---")
                    all_possible_paths = []
                    for potential_end_node_id in neuronas_estado.keys():
                        if potential_end_node_id != start_node_id:
                            paths_to_end = find_all_paths(neuronas_estado, start_node_id, potential_end_node_id)
                            all_possible_paths.extend(paths_to_end)
                    
                    if all_possible_paths:
                        for i, p in enumerate(all_possible_paths):
                            path_str = " -> ".join(p)
                            is_active = all(neuronas_estado[node]['current_activations_val'] > 0 or neuronas_estado[node]['valor_decimal'] > 0 for node in p)
                            status = " (ACTIVA)" if is_active else ""
                            print(f"  Ruta {i+1}: {path_str}{status}")
                        log_event('ruta', start_node_id, {'type': 'all_from_source', 'paths_found': len(all_possible_paths)})
                    else:
                        print(f"No se encontraron rutas desde '{start_node_id}'.")
                        log_event('ruta', start_node_id, {'type': 'all_from_source', 'paths_found': 0})
            elif option == "activa": # ruta activa
                print("\n--- TODAS LAS RUTAS ACTIVAS (Valor Decimal > 0 o Activaciones Actuales > 0) ---")
                found_any_active_path = False
                all_neuron_ids = list(neuronas_estado.keys())
                for i in range(len(all_neuron_ids)):
                    for j in range(len(all_neuron_ids)):
                        if i != j:
                            start_node = all_neuron_ids[i]
                            end_node = all_neuron_ids[j]
                            paths = find_all_paths(neuronas_estado, start_node, end_node)
                            for p in paths:
                                is_active = all(neuronas_estado[node]['current_activations_val'] > 0 or neuronas_estado[node]['valor_decimal'] > 0 for node in p)
                                if is_active:
                                    print(f"  Ruta ACTIVA: {' -> '.join(p)}")
                                    found_any_active_path = True
                if not found_any_active_path:
                    print("No se encontraron rutas activas en la red.")
                log_event('ruta', None, {'type': 'activa', 'result': 'displayed'})
            else:
                print("Error: Comando 'ruta' incompleto o incorrecto. Usa 'help with ruta' para ver las opciones.")
            continue

        # Comando 'guar' (guardar estado como JSON string)
        match_guar = patron_guar.match(comand)
        if match_guar:
            serializable_state = {}
            for neuron_id, data in neuronas_estado.items():
                serializable_neuron_data = data.copy()
                serializable_neuron_data['connections_out'] = list(serializable_neuron_data['connections_out'])
                serializable_state[neuron_id] = serializable_neuron_data
            
            json_output = json.dumps(serializable_state, indent=4)
            print("\n--- ESTADO DE BYNARIUM (JSON) ---")
            print("Copia el siguiente texto y pégalo en un archivo de texto (ej. mi_red.json) para guardarlo:")
            print("```json")
            print(json_output)
            print("```")
            print("\nEstado de Bynarium listo para copiar.")
            log_event('guar', None, {'message': 'Estado serializado a JSON para copiar.'})
            continue

        # Comando 'carg' (cargar estado desde JSON string)
        match_carg = patron_carg.match(comand)
        if match_carg:
            print("\n--- CARGAR ESTADO DE BYNARIUM ---")
            print("Por favor, pega el texto JSON que guardaste previamente y presiona Enter dos veces (una vez para la última línea, otra para confirmar):")
            json_input_lines = []
            while True:
                try:
                    line = input()
                    if not line: # Si el usuario presiona Enter en una línea vacía
                        break
                    json_input_lines.append(line)
                except EOFError: # Para entornos que envían EOF (ej. al pegar mucho texto)
                    break
            json_input_str = "\n".join(json_input_lines)

            if json_input_str.startswith("```json") and json_input_str.endswith("```"):
                json_input_str = json_input_str[len("```json"):-len("```")].strip()
            
            try:
                loaded_state = json.loads(json_input_str)
                
                new_neuronas_estado = {}
                for neuron_id, data in loaded_state.items():
                    loaded_neuron_data = data.copy()
                    loaded_neuron_data['connections_out'] = set(loaded_neuron_data['connections_out'])
                    new_neuronas_estado[neuron_id] = loaded_neuron_data
                
                neuronas_estado.clear()
                neuronas_estado.update(new_neuronas_estado)
                
                print(f"Estado de Bynarium cargado exitosamente.")
                print("Usa 'topo:' para ver las neuronas cargadas.")
                log_event('carg', None, {'message': 'Estado cargado desde JSON pegado.'})
            except json.JSONDecodeError as e:
                print(f"Error: El texto pegado no es un JSON válido o está corrupto: {e}")
                log_event('carg', None, {'error': f'JSON Decode Error: {e}'})
            except Exception as e:
                print(f"Error inesperado al cargar el estado: {e}")
                log_event('carg', None, {'error': f'Unexpected error: {e}'})
            continue

        # Comando 'loop' (repetir activaciones)
        match_loop = patron_loop.match(comand)
        if match_loop:
            id_neurona = match_loop.group(1).upper()
            repeticiones_str = match_loop.group(2)

            if id_neurona not in neuronas_estado:
                print(f"Error: La neurona '{id_neurona}' no existe.")
                continue
            
            try:
                repeticiones = int(repeticiones_str)
                if repeticiones <= 0:
                    print("Error: El número de repeticiones debe ser un entero positivo.")
                    continue
            except ValueError:
                print(f"Error: La cantidad de repeticiones '{repeticiones_str}' no es un número válido.")
                continue
            
            neurona = neuronas_estado[id_neurona]
            activaciones_iniciales = neurona['current_activations_val']
            activaciones_realizadas = 0

            print(f"\n--- Ejecutando 'loop' en '{id_neurona}' por {repeticiones} repeticiones ---")
            for i in range(repeticiones):
                if neurona['current_activations_val'] < neurona['max_activations_capacity_val']:
                    neurona['current_activations_val'] += 1
                    neurona['current_activations_str'] = str(neurona['current_activations_val'])
                    activaciones_realizadas += 1
                    print(f"  Repetición {i+1}: Neurona '{id_neurona}' activada. Activaciones actuales: {neurona['current_activations_str']}.")
                else:
                    print(f"  Repetición {i+1}: Neurona '{id_neurona}' ya alcanzó su capacidad máxima de activaciones ({neurona['max_activations_capacity_str']} | valor: {neurona['max_activations_capacity_val']}). Deteniendo loop.")
                    break
            
            print(f"Loop finalizado. Se realizaron {activaciones_realizadas} activaciones en '{id_neurona}'.")
            print(f"Activaciones finales de '{id_neurona}': {neurona['current_activations_str']}.")
            log_event('loop', id_neurona, {
                'requested_repetitions': repeticiones, 'actual_repetitions': activaciones_realizadas,
                'initial_activations': activaciones_iniciales, 'final_activations': neurona['current_activations_val']
            })
            continue

        # NUEVO: Comando 'pausa'
        match_pausa = patron_pausa.match(comand)
        if match_pausa:
            ms_str = match_pausa.group(1)
            try:
                milliseconds = int(ms_str)
                if milliseconds < 0:
                    print("Error: El tiempo de pausa debe ser un valor positivo.")
                    continue
                print(f"Pausando Bynarium por {milliseconds} ms...")
                time.sleep(milliseconds / 1000) # Convertir milisegundos a segundos
                print("Pausa finalizada.")
                log_event('pausa', None, {'duration_ms': milliseconds})
            except ValueError:
                print(f"Error: El valor '{ms_str}' no es un número válido para la pausa.")
            continue

        # NUEVO: Comando 'log'
        match_log = patron_log.match(comand)
        if match_log:
            target_id = match_log.group(1)
            print("\n--- REGISTRO DE EVENTOS DE BYNARIUM ---")
            if not global_log:
                print("No hay eventos registrados aún.")
            else:
                filtered_log = [entry for entry in global_log if target_id is None or (entry['neuron_id'] and entry['neuron_id'].upper() == target_id.upper())]
                if not filtered_log:
                    print(f"No se encontraron eventos para la neurona '{target_id}'.")
                else:
                    for entry in filtered_log:
                        neuron_info = f" (Neurona: {entry['neuron_id']})" if entry['neuron_id'] else ""
                        details_info = f" Detalles: {entry['details']}" if entry['details'] else ""
                        print(f"[{entry['timestamp']}] {entry['event_type'].upper()}{neuron_info}{details_info}")
            log_event('log', target_id, {'message': 'Registro de eventos mostrado.'})
            continue

        # NUEVO: Comando 'eval'
        match_eval = patron_eval.match(comand)
        if match_eval:
            print("\n--- DIAGNÓSTICO DE ESTADO GENERAL (EVAL) ---")
            if not neuronas_estado:
                print("No hay neuronas en el sistema para evaluar.")
                log_event('eval', None, {'result': 'no neurons'})
                continue

            total_neurons = len(neuronas_estado)
            active_neurons_count = 0
            total_decimal_value = 0
            total_activations_value = 0
            leaks_found = [] # valor_decimal > 0 pero current_activations_val == 0
            isolated_neurons = [] # sin conexiones de salida

            for neuron_id, data in neuronas_estado.items():
                if data['current_activations_val'] > 0:
                    active_neurons_count += 1
                total_decimal_value += data['valor_decimal']
                total_activations_value += data['current_activations_val']

                if data['valor_decimal'] > 0 and data['current_activations_val'] == 0:
                    leaks_found.append(neuron_id)
                
                if not data['connections_out']:
                    isolated_neurons.append(neuron_id)
            
            print(f"• Total de Neuronas: {total_neurons}")
            print(f"• Neuronas Activas (activaciones > 0): {active_neurons_count}")
            print(f"• Suma Total de Valor Decimal: {total_decimal_value}")
            print(f"• Suma Total de Activaciones Actuales: {total_activations_value}")

            if leaks_found:
                print(f"• Posibles Fugas (Valor Decimal > 0, Activaciones = 0): {', '.join(leaks_found)}")
            else:
                print("• No se detectaron posibles fugas (Valor Decimal > 0, Activaciones = 0).")
            
            if isolated_neurons:
                print(f"• Neuronas Aisladas (sin conexiones de salida): {', '.join(isolated_neurons)}")
            else:
                print("• No se detectaron neuronas aisladas.")
            
            log_event('eval', None, {
                'total_neurons': total_neurons,
                'active_neurons_count': active_neurons_count,
                'total_decimal_value': total_decimal_value,
                'total_activations_value': total_activations_value,
                'leaks_found': leaks_found,
                'isolated_neurons': isolated_neurons
            })
            continue

        # NUEVO: Comando 'ciclo'
        match_ciclo = patron_ciclo.match(comand)
        if match_ciclo:
            if not neuronas_estado:
                print("No hay neuronas en el sistema para ejecutar un ciclo.")
                continue

            activations_to_add = defaultdict(int)
            activations_to_subtract = defaultdict(int)
            
            print("\n--- Ejecutando un Ciclo de Activación de Red ---")
            # Primera pasada: Calcular cambios
            for source_id, source_neuron in neuronas_estado.items():
                if source_neuron['current_activations_val'] > 0:
                    # La neurona origen pulsa, por lo tanto su activación disminuye
                    activations_to_subtract[source_id] += 1
                    
                    # Propagar a las conexiones de salida
                    if source_neuron['connections_out']:
                        print(f"  Neurona '{source_id}' (activaciones: {source_neuron['current_activations_str']}) pulsa a: {', '.join(source_neuron['connections_out'])}")
                        for target_id in source_neuron['connections_out']:
                            if target_id in neuronas_estado:
                                target_neuron = neuronas_estado[target_id]
                                if target_neuron['current_activations_val'] < target_neuron['max_activations_capacity_val']:
                                    activations_to_add[target_id] += 1
                                else:
                                    print(f"    '{target_id}' está llena, no recibe activación de '{source_id}'.")
                            else:
                                print(f"    Advertencia: Conexión a neurona inexistente '{target_id}' desde '{source_id}'.")
                    else:
                        print(f"  Neurona '{source_id}' (activaciones: {source_neuron['current_activations_str']}) pulsa, pero no tiene conexiones de salida.")
                
            # Segunda pasada: Aplicar cambios
            changes_applied = False
            for neuron_id, neuron_data in neuronas_estado.items():
                old_activations = neuron_data['current_activations_val']
                
                # Sumar activaciones recibidas
                neuron_data['current_activations_val'] += activations_to_add[neuron_id]
                # Restar activaciones enviadas (si pulsó)
                neuron_data['current_activations_val'] -= activations_to_subtract[neuron_id]

                # Asegurar que las activaciones no bajen de 0
                neuron_data['current_activations_val'] = max(0, neuron_data['current_activations_val'])
                # Asegurar que las activaciones no excedan la capacidad máxima
                neuron_data['current_activations_val'] = min(neuron_data['current_activations_val'], neuron_data['max_activations_capacity_val'])
                
                if old_activations != neuron_data['current_activations_val']:
                    neuron_data['current_activations_str'] = str(neuron_data['current_activations_val'])
                    print(f"  Estado final '{neuron_id}': Activaciones {old_activations} -> {neuron_data['current_activations_str']}.")
                    changes_applied = True
            
            if not changes_applied:
                print("No se realizaron cambios de activación en este ciclo.")
            print("Ciclo de activación finalizado.")
            log_event('ciclo', None, {'message': 'Ciclo de activación ejecutado.'})
            continue

        # NUEVO: Comando 'evento'
        match_evento = patron_evento.match(comand)
        if match_evento:
            id_condicion_neurona = match_evento.group(1).upper()
            tipo_condicion = match_evento.group(2)
            valor_condicion_str = match_evento.group(3)
            id_accion_neurona = match_evento.group(4).upper()
            accion_tipo = match_evento.group(5)

            if id_condicion_neurona not in neuronas_estado:
                print(f"Error: La neurona de condición '{id_condicion_neurona}' no existe.")
                continue
            if id_accion_neurona not in neuronas_estado:
                print(f"Error: La neurona de acción '{id_accion_neurona}' no existe.")
                continue

            try:
                valor_condicion = int(valor_condicion_str)
            except ValueError:
                print(f"Error: El valor de condición '{valor_condicion_str}' no es un número válido.")
                continue

            neurona_condicion = neuronas_estado[id_condicion_neurona]
            condicion_cumplida = False

            if tipo_condicion == 'act_gt':
                if neurona_condicion['current_activations_val'] > valor_condicion:
                    condicion_cumplida = True
            elif tipo_condicion == 'val_eq':
                if neurona_condicion['valor_decimal'] == valor_condicion:
                    condicion_cumplida = True
            
            if condicion_cumplida:
                print(f"\n--- EVENTO DETECTADO ---")
                print(f"Condición '{id_condicion_neurona}' ({tipo_condicion} {valor_condicion}) cumplida.")
                neurona_accion = neuronas_estado[id_accion_neurona]
                old_accion_activations = neurona_accion['current_activations_val']

                if accion_tipo == 'act':
                    if neurona_accion['current_activations_val'] < neurona_accion['max_activations_capacity_val']:
                        neurona_accion['current_activations_val'] += 1
                        neurona_accion['current_activations_str'] = str(neurona_accion['current_activations_val'])
                        print(f"  Acción: '{id_accion_neurona}' activada. Activaciones: {old_accion_activations} -> {neurona_accion['current_activations_str']}.")
                    else:
                        print(f"  Acción: '{id_accion_neurona}' ya está en su capacidad máxima, no se pudo activar.")
                elif accion_tipo == 'inh':
                    if neurona_accion['current_activations_val'] > 0:
                        neurona_accion['current_activations_val'] -= 1
                        neurona_accion['current_activations_str'] = str(neurona_accion['current_activations_val'])
                        print(f"  Acción: '{id_accion_neurona}' inhibida. Activaciones: {old_accion_activations} -> {neurona_accion['current_activations_str']}.")
                    else:
                        print(f"  Acción: '{id_accion_neurona}' ya está en su activación mínima, no se pudo inhibir.")
                
                log_event('evento_trigger', id_condicion_neurona, {
                    'condition_type': tipo_condicion, 'condition_value': valor_condicion,
                    'action_neuron': id_accion_neurona, 'action_type': accion_tipo,
                    'action_old_activations': old_accion_activations, 'action_new_activations': neurona_accion['current_activations_val']
                })
            else:
                print(f"Condición para '{id_condicion_neurona}' no cumplida. No se realizó ninguna acción.")
                log_event('evento_check', id_condicion_neurona, {'condition_type': tipo_condicion, 'condition_value': valor_condicion, 'result': 'not met'})
            continue

        # NUEVO: Comando 'copia'
        match_copia = patron_copia.match(comand)
        if match_copia:
            id_origen = match_copia.group(1).upper()
            id_nuevo = match_copia.group(2).upper()

            if id_origen not in neuronas_estado:
                print(f"Error: La neurona origen '{id_origen}' no existe.")
                continue
            if id_nuevo in neuronas_estado:
                print(f"Error: La neurona destino '{id_nuevo}' ya existe. Por favor, elige un ID nuevo.")
                continue
            
            neurona_origen = neuronas_estado[id_origen]
            
            # Duplicar el estado de la neurona origen
            new_neuron_data = neurona_origen.copy()
            new_neuron_data['connections_out'] = set() # Las conexiones de salida no se copian, la nueva neurona empieza sin conexiones
            
            neuronas_estado[id_nuevo] = new_neuron_data

            print(f"\n--- Operación 'copia' realizada ---")
            print(f"Neurona '{id_origen}' duplicada a '{id_nuevo}'.")
            print(f"   Estado de '{id_nuevo}':")
            print(f"     Bits: {new_neuron_data['bits']}")
            print(f"     Valor Decimal: {new_neuron_data['valor_decimal']}")
            print(f"     Activaciones: {new_neuron_data['current_activations_str']}")
            print(f"     Conexiones de Salida: Ninguna (se inician vacías)")
            log_event('copia', id_nuevo, {'origen': id_origen, 'details': 'Duplicado de estado de neurona.'})
            continue


        # --- Comandos de Ayuda ---
        match_help_specific = patron_help_specific.match(comand)
        if match_help_specific:
            cmd_help = match_help_specific.group(2).lower()
            if cmd_help == "crea":
                print("\ncrea: [ID_Neurona], [Número_de_Bits] - Crea una nueva neurona con un ID y un número de bits.")
                print("   Ejemplo: crea: N1, 8 (Crea la neurona N1 con 8 bits).")
                print("   El número de bits (cajanum) se usa para calcular un límite (cajanum-1) para una fórmula de sumatoria, que a su vez define la 'capacidad máxima de activaciones' de la neurona.")
            elif cmd_help == "out":
                print("\nout: [ID_Neurona] - Muestra el estado actual (bits, capacidad de activación, activaciones actuales, valor decimal/binario) de la neurona.")
                print("   También muestra las conexiones de salida establecidas por operaciones como 'bif', 'fus', 'fusion' o 'preset'.")
                print("   Ejemplo: out: N1")
            elif cmd_help == "mov":
                print("\nmov: [ID_Neurona], [Valor_Decimal] - Establece el valor decimal interno de la neurona. El valor se convierte a binario.")
                print("   Ejemplo: mov: N1, 255 (establece el valor de N1 a 255 si tiene suficientes bits).")
                print("   El valor debe estar dentro del rango de bits de la neurona (0 a 2^bits - 1).")
                print("   Al usar 'mov:', se actualiza tanto el binario como las activaciones actuales visibles.")
                print("   Las activaciones se interpretan desde el valor decimal como una sumatoria simbólica (ej: 16 = 1+3+5+7).")
            elif cmd_help == "act":
                print("\nact: [ID_Neurona] - Activa la neurona, incrementando su contador de 'activaciones actuales'.")
                print("   La activación se detiene una vez que se alcanza la 'capacidad máxima de activaciones' de la neurona.")
            elif cmd_help == "inh":
                print("\ninh: [ID_Neurona] - Inhibe la neurona, decrementando su contador de 'activaciones actuales'.")
                print("   Las activaciones no pueden bajar de 0.")
            elif cmd_help == "bif":
                print("\nbif: [ID_Origen] = [ID_Destino1], [ID_Destino2] - Bifurca 2 'activaciones actuales' de la neurona origen a los destinos.")
                print("   La neurona origen pierde 2 activaciones, y cada destino gana 1 (si no excede su propia capacidad máxima).")
                print("   Establece conexiones de salida desde el origen a ambos destinos.")
            elif cmd_help == "nop":
                print("\nnop: [ID_Neurona] - Mantiene el estado de la neurona. No realiza cambios en sus 'activaciones actuales' o valor.")
            elif cmd_help == "comb":
                print("\ncomb: [ID_Neurona1] [?+ | ?-] [ID_Neurona2] - Realiza operaciones de combinación o descompresión estructural.")
                print("   - comb: [ID_Vacia] ?+ [ID_Llena]: Expande la capacidad de [ID_Vacia] tomando 1 bit de [ID_Llena]. [ID_Vacia] se reinicia, [ID_Llena] recalcula sus activaciones a su nueva capacidad máxima.")
                print("   - comb: [ID_A] ?- [ID_B]: Descomprime una estructura mayor en dos subestructuras. Requiere que los NB de [ID_A] y [ID_B] sean impares y difieran en 2.")
                print("     La neurona con mayor NB se convierte en una estructura intermedia (valor decimal 8). La de menor NB se convierte en una estructura casi llena (valor decimal 4). Ambas tendrán NB_m = (NB_mayor + NB_menor) / 2. Sus conexiones de salida se limpian.")
                print("   Ejemplo: comb: N1 ?+ N2")
                print("   Ejemplo: comb: N1 ?- N2")
            elif cmd_help == "fusion":
                print("\nfusion: [ID_Origen1], [ID_Origen2] -> [ID_Destino] - Fusiona la estructura binaria de dos neuronas origen en una neurona destino.")
                print("   Ambas neuronas origen deben tener un valor decimal > 0. La neurona destino debe estar vacía (valor decimal y activaciones en 0).")
                print("   Las cadenas binarias de los orígenes se concatenan. Si el resultado es '1001', se simplifica a '100' (con 'fuga de 1').")
                print("   Si la cadena binaria combinada contiene '11', ocurre una 'colisión lógica (F2)' y la operación falla.")
                print("   El destino debe tener suficiente capacidad de bits para el resultado. Las neuronas origen se reinician.")
                print("   Ejemplo: fusion: N1, N2 -> N3 (N1 y N2 se fusionan en N3).")
            elif cmd_help == "fus":
                print("\nfus: [ID_Origen], [ID_Destino], [Cantidad] - Transfiere una cantidad específica de activaciones desde la neurona origen a la neurona destino.")
                print("   La neurona origen debe tener suficientes activaciones. La neurona destino recibirá activaciones hasta su capacidad máxima.")
                print("   Establece una conexión de salida desde el origen al destino.")
                print("   Ejemplo: fus: N1, N2, 5 (Transfiere 5 activaciones de N1 a N2).")
            elif cmd_help == "reset":
                print("\nreset - Elimina todas las neuronas del sistema, reiniciando Bynarium.")
                print("   Ejemplo: reset")
            elif cmd_help == "preset":
                print("\npreset: [Tipo_Topología], [Prefijo_ID], [Cantidad_Inicial] - Crea una topología predefinida de neuronas.")
                print("   [Tipo_Topología]: 'piramide', 'cuadrado', o 'invertida'.")
                print("   [Prefijo_ID]: Un prefijo para los IDs de las nuevas neuronas (ej. 'N', 'S1').")
                print("   [Cantidad_Inicial]: Número de neuronas en la primera capa.")
                print("\n   Tipos de Topología y Conexiones:")
                print("   - piramide: Capa 1: [Cantidad_Inicial] (2 bits). Capa 2: [Cantidad_Inicial]/2 (3 bits). Capa 3: ([Cantidad_Inicial]/2)/2 (4 bits).")
                print("     Conexiones: Cada neurona en la Capa N se conecta a la neurona correspondiente en la Capa N+1 (fan-in: dos de N a una de N+1).")
                print("   - cuadrado: Capa 1: [Cantidad_Inicial] (2 bits). Capa 2: [Cantidad_Inicial] (3 bits). Capa 3: [Cantidad_Inicial] (4 bits).")
                print("     Conexiones: Cada neurona en la Capa N se conecta a la neurona con el mismo índice en la Capa N+1 (conexión 1 a 1).")
                print("   - invertida: Capa 1: [Cantidad_Inicial] (2 bits). Capa 2: [Cantidad_Inicial]*2 (3 bits). Capa 3: [Cantidad_Inicial]*4 (4 bits).")
                print("     Conexiones: Cada neurona en la Capa N se conecta a dos neuronas en la Capa N+1 (fan-out).")
                print("   Los IDs se generarán como [Prefijo_ID][Número_Capa][Índice_Nodo] (ej. 'S11', 'S23').")
                print("   Ejemplo: preset: piramide, S, 8")
            elif cmd_help == "topo":
                print("\ntopo: [ID_Neurona]? - Muestra la topología (estado resumido) de todas las neuronas creadas, o detalles de una neurona específica.")
                print("   Ahora también muestra las conexiones de salida de cada neurona.")
                print("   Ejemplo: topo: (muestra todas)")
                print("   Ejemplo: topo: N1 (muestra detalles de N1)")
            elif cmd_help == "ruta":
                print("\nruta: [ID_Origen] [-> [ID_Destino]] [activa|completa]? - Muestra rutas de conexión entre neuronas.")
                print("   - ruta: [ID_Origen]: Muestra todas las rutas posibles desde [ID_Origen] a cualquier otra neurona.")
                print("   - ruta: [ID_Origen] -> [ID_Destino]: Muestra todas las rutas posibles desde [ID_Origen] hasta [ID_Destino].")
                print("   - ruta: activa: Muestra todas las rutas en la red donde cada neurona en la ruta tiene valor decimal > 0 o activaciones actuales > 0.")
                print("   - ruta: completa: Muestra un mapa de todas las neuronas y sus conexiones directas de salida.")
                print("   Ejemplo: ruta: N1")
                print("   Ejemplo: ruta: N1 -> N5")
                print("   Ejemplo: ruta: activa")
                print("   Ejemplo: ruta: completa")
            elif cmd_help == "guar":
                print("\nguar - Muestra el estado actual de todas las neuronas (incluyendo activaciones y conexiones) como un texto JSON en la consola.")
                print("   Copia este texto y pégalo en un archivo de texto (ej. mi_red.json) para guardarlo manualmente.")
                print("   Ejemplo: guar")
            elif cmd_help == "carg":
                print("\ncarg - Te pedirá que pegues el texto JSON que guardaste previamente. Carga ese estado, reemplazando el actual de Bynarium.")
                print("   Ejemplo: carg")
            elif cmd_help == "loop":
                print("\nloop: [ID_Neurona], [Cantidad_Repeticiones] - Repite la operación de 'activar' la neurona la cantidad de veces especificada.")
                print("   La activación se detendrá automáticamente si la neurona alcanza su capacidad máxima durante el loop.")
                print("   Ejemplo: loop: N1, 10 (Activa N1 diez veces, o hasta que se llene).")
            elif cmd_help == "pausa":
                print("\npausa: [milisegundos] - Introduce una espera simbólica en el sistema por la cantidad de milisegundos especificada.")
                print("   Útil para simular un tiempo de procesamiento o para visualizaciones paso a paso.")
                print("   Ejemplo: pausa: 500 (Pausa por 500 milisegundos).")
            elif cmd_help == "log":
                print("\nlog: [ID_Neurona]? - Muestra el historial de eventos registrados en el sistema.")
                print("   - log: (sin ID): Muestra todos los eventos registrados.")
                print("   - log: [ID_Neurona]: Muestra solo los eventos relacionados con una neurona específica.")
                print("   Ejemplo: log")
                print("   Ejemplo: log: N1")
            elif cmd_help == "eval":
                print("\neval - Realiza un diagnóstico del estado general de la red de neuronas.")
                print("   Muestra información como el número total de neuronas, neuronas activas, suma de valores decimales y activaciones, y detecta posibles 'fugas' (valor > 0 pero activaciones = 0) o neuronas aisladas (sin conexiones de salida).")
                print("   Ejemplo: eval")
            elif cmd_help == "ciclo":
                print("\nciclo - Ejecuta un ciclo de activación de la red neuronal.")
                print("   Cada neurona con activaciones > 0 'pulsa' (decrementa sus activaciones en 1) e intenta activar en 1 a sus neuronas conectadas (si no están a máxima capacidad).")
                print("   Ejemplo: ciclo")
            elif cmd_help == "evento":
                print("\nevento: [ID_Neurona_Condicion], [tipo_condicion], [valor_condicion], [ID_Neurona_Accion], [accion_tipo] - Dispara una acción en una neurona si se cumple una condición en otra.")
                print("   [tipo_condicion]: 'act_gt' (activaciones mayor que), 'val_eq' (valor decimal igual a).")
                print("   [accion_tipo]: 'act' (activar), 'inh' (inhibir).")
                print("   Ejemplo: evento: N1, act_gt, 5, N2, act (Si N1 tiene más de 5 activaciones, activa N2).")
                print("   Ejemplo: evento: N3, val_eq, 10, N4, inh (Si N3 tiene valor decimal 10, inhibe N4).")
            elif cmd_help == "copia":
                print("\ncopia: [ID_Origen], [ID_Nuevo] - Duplica una neurona existente, creando una nueva con el mismo estado (bits, valor decimal, activaciones).")
                print("   La nueva neurona no tendrá conexiones de salida inicialmente.")
                print("   Ejemplo: copia: N1, N1_copia")
            else:
                print(f"Ayuda para '{cmd_help}' no disponible.")
            continue

        elif comand == "help" or comand == "ayuda":
            print("\n--- Comandos disponibles ---")
            print("   crea: [ID], [Bits]")
            print("   out: [ID]")
            print("   mov: [ID], [Valor]")
            print("   act: [ID]")
            print("   inh: [ID]")
            print("   bif: [ID_Origen] = [ID_Destino1], [ID_Destino2]")
            print("   nop: [ID]")
            print("   comb: [ID_Neurona1] [?+ | ?-] [ID_Neurona2]") # Actualizado en el menú principal
            print("   fusion: [ID_Origen1], [ID_Origen2] -> [ID_Destino]")
            print("   fus: [ID_Origen], [ID_Destino], [Cantidad]")
            print("   reset")
            print("   preset: [Tipo_Topología], [Prefijo_ID], [Cantidad_Inicial]")
            print("   ruta: [ID_Origen] [-> [ID_Destino]] [activa|completa]?")
            print("   guar")
            print("   carg")
            print("   loop: [ID_Neurona], [Cantidad_Repeticiones]")
            print("   pausa: [milisegundos]")
            print("   log: [ID_Neurona]?")
            print("   eval")
            print("   ciclo")
            print("   evento: [ID_Condicion], [Tipo_Condicion], [Valor_Condicion], [ID_Accion], [Accion_Tipo]")
            print("   copia: [ID_Origen], [ID_Nuevo]")
            print("   topo: [ID]?")
            print("\nPara más información: 'help with [comando]' o 'ayuda con [comando]'.")
            print("   Ejemplo: 'help with crea'")
            print("   Para salir: 'salir'")
            print("Espero que te sirva <3")
            continue

        print(f"Comando '{comand}' no reconocido o formato incorrecto. Escribe 'help' o 'ayuda' para ver la lista de comandos.")

# --- Ejecución ---
Bynarium_NeuronasActualizadas()
