import re

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
    patron_comb = re.compile(r"comb:\s*([A-Za-z0-9_]+)\s*\?\+\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_fusion = re.compile(r"fusion:\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*->\s*([A-Za-z0-9_]+)", re.IGNORECASE) # Nuevo patrón para 'fusion'
    patron_fus = re.compile(r"fus:\s*([A-Za-z0-9_]+)", re.IGNORECASE) # Nuevo patrón para 'fus' (eliminar neurona)
    patron_reset = re.compile(r"reset", re.IGNORECASE) # Nuevo patrón para 'reset' (eliminar todas)
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
                        'valor_binario_str': bin(0)[2:].zfill(bits_int)
                    }
                    print(f"Neurona '{id_neurona}' creada con {bits_int} bits.")
                    print(f"   El límite para la fórmula de sumatoria (Bits-1) es: {formula_limit_n}")
                    print(f"   La capacidad total de activaciones para esta neurona es: {max_activations_capacity_str} (valor: {max_activations_capacity_val})")
                    print(f"   Valor inicial: {neuronas_estado[id_neurona]['valor_binario_str']} (decimal: {neuronas_estado[id_neurona]['valor_decimal']})")
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
                
                neuronas_estado[id_neurona]['valor_decimal'] = nuevo_valor_decimal
                neuronas_estado[id_neurona]['valor_binario_str'] = bin(nuevo_valor_decimal)[2:].zfill(bits_requeridos)

                activ_val, activ_str = estimar_sumatoria_binaria(nuevo_valor_decimal)
                neuronas_estado[id_neurona]['current_activations_val'] = activ_val
                neuronas_estado[id_neurona]['current_activations_str'] = activ_str
                
                print(f"Comando 'mov' detectado: Neurona '{id_neurona}' actualizada a valor: {neuronas_estado[id_neurona]['valor_decimal']} (binario: {neuronas_estado[id_neurona]['valor_binario_str']})")
                print(f"   Activaciones simbólicas interpretadas como: {activ_str} (valor: {activ_val})")
            except ValueError:
                print(f"Error: El valor '{nuevo_valor_decimal_str}' en 'mov' no es un entero válido.")
            continue

        # Comando 'act' (incrementa current_activations hasta max_activations_capacity)
        match_act = patron_act.match(comand)
        if match_act:
            id_neurona = match_act.group(1).upper()
            if id_neurona in neuronas_estado:
                neurona = neuronas_estado[id_neurona]
                
                if neurona['current_activations_val'] < neurona['max_activations_capacity_val']:
                    neurona['current_activations_val'] += 1
                    neurona['current_activations_str'] = str(neurona['current_activations_val'])
                    print(f"Neurona '{id_neurona}' activada.")
                    print(f"   Activaciones actuales: {neurona['current_activations_str']} (Capacidad total: {neurona['max_activations_capacity_str']} | valor: {neurona['max_activations_capacity_val']}).")
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
                if neurona['current_activations_val'] > 0:
                    neurona['current_activations_val'] -= 1
                    neurona['current_activations_str'] = str(neurona['current_activations_val'])
                    print(f"Neurona '{id_neurona}' inhibida. Activaciones actuales: {neurona['current_activations_str']}.")
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
                    neurona_origen['current_activations_val'] -= 2 
                    neurona_origen['current_activations_str'] = str(neurona_origen['current_activations_val'])
                    
                    neurona_destino1['current_activations_val'] = min(neurona_destino1['current_activations_val'] + 1, neurona_destino1['max_activations_capacity_val'])
                    neurona_destino1['current_activations_str'] = str(neurona_destino1['current_activations_val'])
                    neurona_destino2['current_activations_val'] = min(neurona_destino2['current_activations_val'] + 1, neurona_destino2['max_activations_capacity_val'])
                    neurona_destino2['current_activations_str'] = str(neurona_destino2['current_activations_val'])
                    
                    print(f"Bifurcación de '{origen_id}' a '{destino1_id}' y '{destino2_id}'.")
                    print(f"   '{origen_id}' (activaciones: {neurona_origen['current_activations_str']})")
                    print(f"   '{destino1_id}' (activaciones: {neurona_destino1['current_activations_str']})")
                    print(f"   '{destino2_id}' (activaciones: {neurona_destino2['current_activations_str']})")
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
            else:
                print(f"Error: La neurona '{id_neurona}' no existe.")
            continue
            
        # Comando 'comb' (combina la capacidad de dos neuronas)
        match_comb = patron_comb.match(comand)
        if match_comb:
            id_vacia = match_comb.group(1).upper()
            id_llena = match_comb.group(2).upper()

            # Validaciones iniciales
            if id_vacia not in neuronas_estado:
                print(f"Error: La neurona '{id_vacia}' (vacía) no existe.")
                continue
            if id_llena not in neuronas_estado:
                print(f"Error: La neurona '{id_llena}' (llena) no existe.")
                continue
            if id_vacia == id_llena:
                print("Error: No puedes combinar una neurona consigo misma.")
                continue
            
            neurona_vacia = neuronas_estado[id_vacia]
            neurona_llena = neuronas_estado[id_llena]

            if neurona_llena['bits'] < 3: 
                print(f"Error: La neurona '{id_llena}' (llena) debe tener al menos 3 bits para poder ceder uno y recalcular sus activaciones.")
                continue

            # Guardar valores antiguos para el mensaje de salida
            old_bits_vacia = neurona_vacia['bits']
            old_capacity_vacia_str = neurona_vacia['max_activations_capacity_str']
            old_activations_vacia_str = neurona_vacia['current_activations_str']

            old_bits_llena = neurona_llena['bits']
            old_capacity_llena_str = neurona_llena['max_activations_capacity_str']
            old_activations_llena_str = neurona_llena['current_activations_str']

            # 1. Ajuste del número de bits
            neurona_vacia['bits'] += 1
            neurona_llena['bits'] -= 1

            # 2. Recálculo de la capacidad de activaciones (max_activations_capacity)
            # Para ID_Vacia (gana bits): formula_limit_n es (bits - 1)
            new_formula_limit_vacia = neurona_vacia['bits'] - 1
            neurona_vacia['formula_limit_n'] = new_formula_limit_vacia
            neurona_vacia['max_activations_capacity_val'] = int(calcular_sumatoria_serie(new_formula_limit_vacia))
            neurona_vacia['max_activations_capacity_str'] = generar_sumatoria_str(new_formula_limit_vacia)

            # Para ID_Llena (pierde bits): formula_limit_n es (bits - 2)
            new_formula_limit_llena = neurona_llena['bits'] - 2
            if new_formula_limit_llena < 0:
                new_formula_limit_llena = 0 
            neurona_llena['formula_limit_n'] = new_formula_limit_llena
            neurona_llena['max_activations_capacity_val'] = int(calcular_sumatoria_serie(new_formula_limit_llena))
            neurona_llena['max_activations_capacity_str'] = generar_sumatoria_str(new_formula_limit_llena)

            # 3. Ajuste de current_activations
            # ID_Vacia se reinicia
            neurona_vacia['current_activations_val'] = 0
            neurona_vacia['current_activations_str'] = "0"

            # ID_Llena: Sus activaciones actuales se calculan con la sumatoria de (bits - 2) de su nuevo tamaño
            # Esto significa que sus activaciones actuales serán iguales a su nueva capacidad máxima.
            neurona_llena['current_activations_val'] = neurona_llena['max_activations_capacity_val']
            neurona_llena['current_activations_str'] = neurona_llena['max_activations_capacity_str']


            # 4. Ajuste de valor_decimal y valor_binario_str (reiniciar a 0)
            neurona_vacia['valor_decimal'] = 0
            neurona_vacia['valor_binario_str'] = bin(0)[2:].zfill(neurona_vacia['bits'])
            
            neurona_llena['valor_decimal'] = 0
            neurona_llena['valor_binario_str'] = bin(0)[2:].zfill(neurona_llena['bits'])

            print(f"\n--- Operación 'comb' realizada entre '{id_vacia}' y '{id_llena}' ---")
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
            continue
            
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

            # Guardar estados antiguos para el mensaje de salida
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

            neurona_origen2['valor_decimal'] = 0
            neurona_origen2['valor_binario_str'] = bin(0)[2:].zfill(neurona_origen2['bits'])
            neurona_origen2['current_activations_val'] = 0
            neurona_origen2['current_activations_str'] = "0"

            print(f"\n--- Operación 'fusion' realizada: '{id_origen1}' ({old_origen1_bin}) y '{id_origen2}' ({old_origen2_bin}) se fusionan en '{id_destino}' ---")
            print(f"   Cadena binaria combinada: {combined_bin_str}{fuga_message}")
            print(f"   Neurona '{id_destino}' ahora tiene valor: {neurona_destino['valor_decimal']} (binario: {neurona_destino['valor_binario_str']})")
            print(f"   Activaciones: {neurona_destino['current_activations_str']} (valor: {neurona_destino['current_activations_val']})")
            print(f"   Las neuronas '{id_origen1}' y '{id_origen2}' han sido reiniciadas.")
            continue

        # Comando 'fus' (eliminar una neurona)
        match_fus = patron_fus.match(comand)
        if match_fus:
            id_neurona_a_eliminar = match_fus.group(1).upper()
            if id_neurona_a_eliminar in neuronas_estado:
                del neuronas_estado[id_neurona_a_eliminar]
                print(f"Neurona '{id_neurona_a_eliminar}' eliminada.")
            else:
                print(f"Error: La neurona '{id_neurona_a_eliminar}' no existe.")
            continue

        # Comando 'reset' (eliminar todas las neuronas)
        match_reset = patron_reset.match(comand)
        if match_reset:
            neuronas_estado.clear()
            print("Todas las neuronas han sido eliminadas. Bynarium reiniciado.")
            continue
            
        # Comando 'topo:' - muestra la topología actual de la red
        match_topo = patron_topo.match(comand)
        if match_topo:
            target_id = match_topo.group(1) # This will be None if no ID is provided

            if target_id: # topo: [ID]
                target_id = target_id.upper()
                if target_id in neuronas_estado:
                    estado = neuronas_estado[target_id]
                    print(f"\n--- TOPOLOGÍA Y ESTADO DE NEURONA '{target_id}' ---")
                    print(f"   • ID: {target_id}")
                    print(f"   Bits: {estado['bits']}")
                    print(f"   Límite para Sumatoria (Bits-1): {estado['formula_limit_n']}")
                    print(f"   Capacidad Máxima de Activaciones: {estado['max_activations_capacity_str']} (valor: {estado['max_activations_capacity_val']})")
                    print(f"   Activaciones Actuales: {estado['current_activations_str']} (valor: {estado['current_activations_val']})")
                    print(f"   Valor Decimal: {estado['valor_decimal']}")
                    print(f"   Valor Binario: {estado['valor_binario_str']}")
                else:
                    print(f"Error: La neurona '{target_id}' no existe.")
            else: # topo: (global)
                if not neuronas_estado:
                    print("No hay neuronas creadas actualmente.")
                else:
                    print("\n--- TOPOLOGÍA ACTUAL DE LA RED (Resumen) ---")
                    for id_neurona, estado in neuronas_estado.items():
                        print(f"• {id_neurona}: Bits={estado['bits']}, Capacidad={estado['max_activations_capacity_str']} (val: {estado['max_activations_capacity_val']}), Activaciones={estado['current_activations_str']} (val: {estado['current_activations_val']}), Bin={estado['valor_binario_str']}")
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
            elif cmd_help == "nop":
                print("\nnop: [ID_Neurona] - Mantiene el estado de la neurona. No realiza cambios en sus 'activaciones actuales' o valor.")
            elif cmd_help == "comb":
                print("\ncomb: [ID_Vacia] ?+ [ID_Llena] - Combina la capacidad de dos neuronas.")
                print("   La neurona '[ID_Vacia]' (izquierda) gana 1 bit de capacidad y reinicia sus activaciones a 0.")
                print("   La neurona '[ID_Llena]' (derecha) pierde 1 bit de capacidad. Sus activaciones actuales se recalculan a la sumatoria de (bits-2) de su nuevo tamaño (su nueva capacidad máxima).")
                print("   Los valores decimales y binarios de ambas neuronas se reinician a 0.")
                print("   Ejemplo: comb: N1 ?+ N2 (N1 gana 1 bit, N2 pierde 1 bit).")
            elif cmd_help == "fusion":
                print("\nfusion: [ID_Origen1], [ID_Origen2] -> [ID_Destino] - Fusiona la estructura binaria de dos neuronas origen en una neurona destino.")
                print("   Ambas neuronas origen deben tener un valor decimal > 0. La neurona destino debe estar vacía (valor decimal y activaciones en 0).")
                print("   Las cadenas binarias de los orígenes se concatenan. Si el resultado es '1001', se simplifica a '100' (con 'fuga de 1').")
                print("   Si la cadena binaria combinada contiene '11', ocurre una 'colisión lógica (F2)' y la operación falla.")
                print("   El destino debe tener suficiente capacidad de bits para el resultado. Las neuronas origen se reinician.")
                print("   Ejemplo: fusion: N1, N2 -> N3 (N1 y N2 se fusionan en N3).")
            elif cmd_help == "fus":
                print("\nfus: [ID_Neurona] - Elimina una neurona específica del sistema.")
                print("   Ejemplo: fus: N1 (Elimina la neurona N1).")
            elif cmd_help == "reset":
                print("\nreset - Elimina todas las neuronas del sistema, reiniciando Bynarium.")
                print("   Ejemplo: reset")
            elif cmd_help == "topo":
                print("\ntopo: [ID_Neurona]? - Muestra la topología (estado resumido) de todas las neuronas creadas, o detalles de una neurona específica.")
                print("   Ejemplo: topo: (muestra todas)")
                print("   Ejemplo: topo: N1 (muestra detalles de N1)")
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
            print("   comb: [ID_Vacia] ?+ [ID_Llena]")
            print("   fusion: [ID_Origen1], [ID_Origen2] -> [ID_Destino]") # Actualizado en el menú principal
            print("   fus: [ID]") # Actualizado en el menú principal
            print("   reset") # Actualizado en el menú principal
            print("   topo: [ID]?")
            print("\nPara más información: 'help with [comando]' o 'ayuda con [comando]'.")
            print("   Ejemplo: 'help with crea'")
            print("   Para salir: 'salir'")
            print("Espero que te sirva <3")
            continue

        print(f"Comando '{comand}' no reconocido o formato incorrecto. Escribe 'help' o 'ayuda' para ver la lista de comandos.")

# --- Ejecución ---
Bynarium_NeuronasActualizadas()