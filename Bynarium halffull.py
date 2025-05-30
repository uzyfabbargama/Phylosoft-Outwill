import re

def calcular_sumatoria_serie(limite_n):
    """
    Calcula la sumatoria de una serie (pares o impares) hasta el limite_n.
    Este 'limite_n' es el valor que se pasa a las fórmulas.
    """
    if limite_n <= 0:
        return 0 # Para casos como 1 bit (limite_n = 0), la sumatoria es 0

    # Ensure integer division where necessary for formulas
    if limite_n % 2 == 0:  # Si el límite es par
        # Fórmula para 2 + 4 + ... + limite_n
        # Example: if limite_n is 8, (8 * ((8 + 2) / 4)) = 8 * (10 / 4) = 8 * 2.5 = 20.0
        # If the series is 2+4+6+8 = 20.
        return limite_n * ((limite_n + 2) / 4)
    else:  # Si el límite es impar
        # Fórmula para 1 + 3 + ... + limite_n
        # Example: if limite_n is 7, ((7 + 1) / 2) ** 2 = (8 / 2) ** 2 = 4 ** 2 = 16.0
        # If the series is 1+3+5+7 = 16.
        return ((limite_n + 1) / 2) ** 2

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
    patron_comb = re.compile(r"comb:\s*([A-Za-z0-9_]+)\s*\?\+\s*([A-Za-z0-9_]+)", re.IGNORECASE) # Nuevo patrón para 'comb'
    patron_help = re.compile(r"help|ayuda", re.IGNORECASE)
    patron_help_specific = re.compile(r"(help|ayuda)\s+with\s+([A-Za-z]+)", re.IGNORECASE)
    patron_topo = re.compile(r"topo:\s*([A-Za-z0-9_]+)?", re.IGNORECASE) # Make ID optional for global topo

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
                    # Ensure formula_limit_n is non-negative for sum calculation
                    if formula_limit_n < 0:
                        formula_limit_n = 0
                        
                    # This is the "total capacity" of activations based on the formula
                    max_activations_capacity = int(calcular_sumatoria_serie(formula_limit_n))
                    
                    neuronas_estado[id_neurona] = {
                        'bits': bits_int,
                        'formula_limit_n': formula_limit_n, # The 'n' for the sum formula (bits - 1)
                        'max_activations_capacity': max_activations_capacity, # The result of the sum
                        'current_activations': 0, # How many activations have occurred so far
                        'valor_decimal': 0,
                        'valor_binario_str': bin(0)[2:].zfill(bits_int)
                    }
                    print(f"Neurona '{id_neurona}' creada con {bits_int} bits.")
                    print(f"   El límite para la fórmula de sumatoria (Bits-1) es: {formula_limit_n}")
                    print(f"   La capacidad total de activaciones para esta neurona es: {max_activations_capacity}")
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
                print(f"   Capacidad Máxima de Activaciones: {estado['max_activations_capacity']}")
                print(f"   Activaciones Actuales: {estado['current_activations']}")
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
                # Calcula el valor decimal máximo que puede almacenar la neurona con sus bits
                # Una neurona con 'n' bits puede almacenar valores de 0 a (2^n - 1)
                max_valor_decimal = (2 ** bits_requeridos) - 1
                
                # Verifica si el nuevo valor decimal está dentro del rango permitido
                if nuevo_valor_decimal < 0 or nuevo_valor_decimal > max_valor_decimal:
                    print(f"Error: El valor {nuevo_valor_decimal} excede el rango para {bits_requeridos} bits (0 a {max_valor_decimal}).")
                    print(f"   Para almacenar este valor, la neurona '{id_neurona}' necesitaría más bits.")
                    continue
                
                # Si el valor es válido, actualiza el valor decimal y su representación binaria
                neuronas_estado[id_neurona]['valor_decimal'] = nuevo_valor_decimal
                # Convierte el valor decimal a binario y lo rellena con ceros a la izquierda
                # para que tenga la longitud exacta de los bits de la neurona.
                neuronas_estado[id_neurona]['valor_binario_str'] = bin(nuevo_valor_decimal)[2:].zfill(bits_requeridos)
                
                print(f"Comando 'mov' detectado: Neurona '{id_neurona}' actualizada a valor: {neuronas_estado[id_neurona]['valor_decimal']} (binario: {neuronas_estado[id_neurona]['valor_binario_str']})")
            except ValueError:
                print(f"Error: El valor '{nuevo_valor_decimal_str}' en 'mov' no es un entero válido.")
            continue

        # Comando 'act' (incrementa current_activations hasta max_activations_capacity)
        match_act = patron_act.match(comand)
        if match_act:
            id_neurona = match_act.group(1).upper()
            if id_neurona in neuronas_estado:
                neurona = neuronas_estado[id_neurona]
                
                if neurona['current_activations'] < neurona['max_activations_capacity']:
                    neurona['current_activations'] += 1
                    print(f"Neurona '{id_neurona}' activada.")
                    print(f"   Activaciones actuales: {neurona['current_activations']} (Capacidad total: {neurona['max_activations_capacity']}).")
                else:
                    print(f"Neurona '{id_neurona}' ya alcanzó su capacidad máxima de activaciones ({neurona['max_activations_capacity']}).")
            else:
                print(f"Error: La neurona '{id_neurona}' no existe.")
            continue
        
        # Comandos 'inh', 'bif', 'nop' (actualizados para usar 'current_activations' y 'max_activations_capacity')
        match_inh = patron_inh.match(comand)
        if match_inh:
            id_neurona = match_inh.group(1).upper()
            if id_neurona in neuronas_estado:
                neurona = neuronas_estado[id_neurona]
                if neurona['current_activations'] > 0:
                    neurona['current_activations'] -= 1
                    print(f"Neurona '{id_neurona}' inhibida. Activaciones actuales: {neurona['current_activations']}.")
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

                # Assuming bifurcating costs 2 current_activations from origin
                if neurona_origen['current_activations'] >= 2: 
                    neurona_origen['current_activations'] -= 2 
                    
                    # Each destination gains 1, up to their own max_activations_capacity
                    neurona_destino1['current_activations'] = min(neurona_destino1['current_activations'] + 1, neurona_destino1['max_activations_capacity'])
                    neurona_destino2['current_activations'] = min(neurona_destino2['current_activations'] + 1, neurona_destino2['max_activations_capacity'])
                    
                    print(f"Bifurcación de '{origen_id}' a '{destino1_id}' y '{destino2_id}'.")
                    print(f"   '{origen_id}' (activaciones: {neurona_origen['current_activations']})")
                    print(f"   '{destino1_id}' (activaciones: {neurona_destino1['current_activations']})")
                    print(f"   '{destino2_id}' (activaciones: {neurona_destino2['current_activations']})")
                else:
                    print(f"La neurona '{origen_id}' necesita al menos 2 activaciones para bifurcar.")
            else:
                print("Error: Una o más neuronas especificadas para la bifurcación no existen.")
            continue

        match_nop = patron_nop.match(comand)
        if match_nop:
            id_neurona = match_nop.group(1).upper()
            if id_neurona in neuronas_estado:
                print(f"Neurona '{id_neurona}' mantendrá su estado actual de activaciones: {neuronas_estado[id_neurona]['current_activations']}. (Operación 'nop').")
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

            # La neurona que cede bits debe tener al menos 2 bits para que 'bits - 2' sea válido
            # y 'bits - 4' para el cálculo de activaciones actuales también sea válido
            if neurona_llena['bits'] < 4: # Se ajusta a 4 para que (bits - 4) sea >= 0
                print(f"Error: La neurona '{id_llena}' (llena) debe tener al menos 4 bits para poder ceder uno y ajustar sus activaciones.")
                continue

            # Guardar valores antiguos para el mensaje de salida
            old_bits_vacia = neurona_vacia['bits']
            old_capacity_vacia = neurona_vacia['max_activations_capacity']
            old_activations_vacia = neurona_vacia['current_activations']

            old_bits_llena = neurona_llena['bits']
            old_capacity_llena = neurona_llena['max_activations_capacity']
            old_activations_llena = neurona_llena['current_activations']

            # 1. Ajuste del número de bits
            neurona_vacia['bits'] += 1
            neurona_llena['bits'] -= 1

            # 2. Recálculo de la capacidad de activaciones (max_activations_capacity)
            # Para ID_Vacia (gana bits): formula_limit_n es (bits - 1)
            new_formula_limit_vacia = neurona_vacia['bits'] - 1
            neurona_vacia['formula_limit_n'] = new_formula_limit_vacia
            neurona_vacia['max_activations_capacity'] = int(calcular_sumatoria_serie(new_formula_limit_vacia))

            # Para ID_Llena (pierde bits): formula_limit_n es (bits - 2)
            new_formula_limit_llena = neurona_llena['bits'] - 2
            # Asegurarse de que el límite no sea negativo, aunque calcular_sumatoria_serie ya lo maneja
            if new_formula_limit_llena < 0:
                new_formula_limit_llena = 0 
            neurona_llena['formula_limit_n'] = new_formula_limit_llena
            neurona_llena['max_activations_capacity'] = int(calcular_sumatoria_serie(new_formula_limit_llena))

            # 3. Ajuste de current_activations
            # ID_Vacia se reinicia
            neurona_vacia['current_activations'] = 0

            # ID_Llena: Se calcula con la fórmula (bits - 4)
            # Asegurarse de que (bits - 4) no sea negativo
            activations_limit_for_llena = neurona_llena['bits'] - 4
            if activations_limit_for_llena < 0:
                activations_limit_for_llena = 0
            neurona_llena['current_activations'] = int(calcular_sumatoria_serie(activations_limit_for_llena))

            # 4. Ajuste de valor_decimal y valor_binario_str (reiniciar a 0)
            neurona_vacia['valor_decimal'] = 0
            neurona_vacia['valor_binario_str'] = bin(0)[2:].zfill(neurona_vacia['bits'])
            
            neurona_llena['valor_decimal'] = 0
            neurona_llena['valor_binario_str'] = bin(0)[2:].zfill(neurona_llena['bits'])

            print(f"\n--- Operación 'comb' realizada entre '{id_vacia}' y '{id_llena}' ---")
            print(f"Neurona '{id_vacia}' (vacía):")
            print(f"   Bits: {old_bits_vacia} -> {neurona_vacia['bits']}")
            print(f"   Capacidad: {old_capacity_vacia} -> {neurona_vacia['max_activations_capacity']}")
            print(f"   Activaciones: {old_activations_vacia} -> {neurona_vacia['current_activations']}")
            print(f"   Valor Binario: {neurona_vacia['valor_binario_str']}")

            print(f"Neurona '{id_llena}' (llena):")
            print(f"   Bits: {old_bits_llena} -> {neurona_llena['bits']}")
            print(f"   Capacidad: {old_capacity_llena} -> {neurona_llena['max_activations_capacity']}")
            print(f"   Activaciones: {old_activations_llena} -> {neurona_llena['current_activations']}")
            print(f"   Valor Binario: {neurona_llena['valor_binario_str']}")
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
                    print(f"• ID: {target_id}")
                    print(f"   Bits: {estado['bits']}")
                    print(f"   Límite para Sumatoria (Bits-1): {estado['formula_limit_n']}")
                    print(f"   Capacidad Máxima de Activaciones: {estado['max_activations_capacity']}")
                    print(f"   Activaciones Actuales: {estado['current_activations']}")
                    print(f"   Valor Decimal: {estado['valor_decimal']}")
                    print(f"   Valor Binario: {estado['valor_binario_str']}")
                    # Future: Display connections if 'bif' or 'comb' store them
                else:
                    print(f"Error: La neurona '{target_id}' no existe.")
            else: # topo: (global)
                if not neuronas_estado:
                    print("No hay neuronas creadas actualmente.")
                else:
                    print("\n--- TOPOLOGÍA ACTUAL DE LA RED (Resumen) ---")
                    for id_neurona, estado in neuronas_estado.items():
                        print(f"• {id_neurona}: Bits={estado['bits']}, Capacidad={estado['max_activations_capacity']}, Activaciones={estado['current_activations']}, Bin={estado['valor_binario_str']}")
            continue # Important to continue the loop after handling 'topo'


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
                print("   La neurona '[ID_Vacia]' (izquierda) gana 1 bit de capacidad.")
                print("   La neurona '[ID_Llena]' (derecha) pierde 1 bit de capacidad.")
                print("   Las capacidades de activación se recalculan según las nuevas cantidades de bits (ID_Vacia: bits-1; ID_Llena: bits-2).")
                print("   Las activaciones actuales de la neurona 'llena' se calculan como la sumatoria de (bits-4) de su nuevo tamaño.")
                print("   Los valores decimales y binarios de ambas neuronas se reinician a 0.")
                print("   Ejemplo: comb: N1 ?+ N2 (N1 gana 1 bit, N2 pierde 1 bit).")
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
            print("   comb: [ID_Vacia] ?+ [ID_Llena]") # Actualizado en el menú principal
            print("   topo: [ID]?")
            print("\nPara más información: 'help with [comando]' o 'ayuda con [comando]'.")
            print("   Ejemplo: 'help with crea'")
            print("   Para salir: 'salir'")
            print("Espero que te sirva <3")
            continue

        print(f"Comando '{comand}' no reconocido o formato incorrecto. Escribe 'help' o 'ayuda' para ver la lista de comandos.")

# --- Ejecución ---
Bynarium_NeuronasActualizadas()
