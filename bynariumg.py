import re

def calcular_sumatoria_serie(limite_n):
    """
    Calcula la sumatoria de una serie (pares o impares) hasta el limite_n.
    Este 'limite_n' es el valor que se pasa a las fórmulas.
    """
    if limite_n <= 0:
        return 0 # O manejar como un error si la sumatoria no aplica

    if limite_n % 2 == 0:  # Si el límite es par
        # Fórmula para 2 + 4 + ... + limite_n
        return limite_n * ((limite_n + 2) / 4)
    else:  # Si el límite es impar
        # Fórmula para 1 + 3 + ... + limite_n
        return ((limite_n + 1) / 2) ** 2

def Bynarium_NeuronasRevisadas():
    neuronas_estado = {} 

    # --- Patrones Regex (sin cambios aquí, el formato de comando es el mismo) ---
    patron_crea = re.compile(r"crea:\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE)
    patron_out = re.compile(r"out:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_mov = re.compile(r"mov:\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE) 
    patron_act = re.compile(r"act:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_inh = re.compile(r"inh:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_bif = re.compile(r"bif:\s*([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_nop = re.compile(r"nop:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    patron_help = re.compile(r"help|ayuda", re.IGNORECASE)
    patron_help_specific = re.compile(r"(help|ayuda)\s+with\s+([A-Za-z]+)", re.IGNORECASE)
    patron_topo = re.compile(r"topo:\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    while True:
        comand = input("\nEscribe tu comando (help para comandos; salir para terminar): ").strip()
        if comand.lower() == "salir":
            print("Saliendo de Bynarium. ¡Hasta pronto!")
            break

        # --- Procesamiento de Comandos ---

        # Comando 'crea' (ahora almacena 'bits' y calcula 'limite_activacion')
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
                    # cajanum = bits_int
                    limite_activacion_calculado = bits_int - 1 # ¡Aquí está la corrección!
                    
                    # Asegurarse que el límite de activación no sea negativo si bits_int es 0 o 1
                    if limite_activacion_calculado < 0:
                        limite_activacion_calculado = 0 
                    
                    neuronas_estado[id_neurona] = {
                        'bits': bits_int,
                        'limite_activacion': limite_activacion_calculado, # Almacena el resultado de bits - 1
                        'activacion_actual': 0, 
                        'valor_decimal': 0, 
                        'valor_binario_str': bin(0)[2:].zfill(bits_int)
                    }
                    print(f"Neurona '{id_neurona}' creada con {bits_int} bits (limite_activacion={limite_activacion_calculado}).")
                    print(f"Valor inicial: {neuronas_estado[id_neurona]['valor_binario_str']} (decimal: {neuronas_estado[id_neurona]['valor_decimal']})")
            except ValueError:
                print(f"Error: El número de bits '{bits_str}' no es un entero válido.")
            continue

        # Comando 'out' (sin cambios, solo muestra el estado)
        match_out = patron_out.match(comand)
        if match_out:
            id_neurona = match_out.group(1).upper()
            if id_neurona in neuronas_estado:
                estado = neuronas_estado[id_neurona]
                print(f"--- Estado de Neurona '{id_neurona}' ---")
                print(f"  Bits: {estado['bits']}")
                print(f"  Límite de Activación (Bits-1): {estado['limite_activacion']}")
                print(f"  Activación Actual: {estado['activacion_actual']}")
                print(f"  Valor Decimal: {estado['valor_decimal']}")
                print(f"  Valor Binario: {estado['valor_binario_str']}")
            else:
                print(f"Error: La neurona '{id_neurona}' no existe. Usa 'crea:' para crearla primero.")
            continue

        # Comando 'mov' (sin cambios, establece el valor decimal y binario)
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
                    continue
                
                neuronas_estado[id_neurona]['valor_decimal'] = nuevo_valor_decimal
                neuronas_estado[id_neurona]['valor_binario_str'] = bin(nuevo_valor_decimal)[2:].zfill(bits_requeridos)
                
                print(f"Comando 'mov' detectado: Neurona '{id_neurona}' actualizada a valor: {neuronas_estado[id_neurona]['valor_decimal']} (binario: {neuronas_estado[id_neurona]['valor_binario_str']})")
            except ValueError:
                print(f"Error: El valor '{nuevo_valor_decimal_str}' en 'mov' no es un entero válido.")
            continue

        # Comando 'act' (ahora usa 'limite_activacion' para la sumatoria)
        match_act = patron_act.match(comand)
        if match_act:
            id_neurona = match_act.group(1).upper()
            if id_neurona in neuronas_estado:
                neurona = neuronas_estado[id_neurona]
                
                # Usar el 'limite_activacion' (bits - 1) para la sumatoria
                sumatoria_aplicada = calcular_sumatoria_serie(neurona['limite_activacion'])
                
                if neurona['activacion_actual'] < neurona['limite_activacion']:
                    neurona['activacion_actual'] += 1
                    print(f"Neurona '{id_neurona}' activada.")
                    print(f"  La sumatoria para su activación se basó en el límite {neurona['limite_activacion']}: {sumatoria_aplicada}.")
                    print(f"  Activación actual: {neurona['activacion_actual']}.")
                    # Aquí podrías decidir cómo 'sumatoria_aplicada' afecta a la neurona,
                    # por ejemplo, si aumenta su 'valor_decimal' de alguna manera,
                    # o si es solo un valor conceptual asociado a cada 'tick' de activación.
                else:
                    print(f"Neurona '{id_neurona}' ya alcanzó su límite de activación ({neurona['limite_activacion']}).")
            else:
                print(f"Error: La neurona '{id_neurona}' no existe.")
            continue
        
        # Comandos 'inh', 'bif', 'nop' (sin cambios, usan 'activacion_actual')
        match_inh = patron_inh.match(comand)
        if match_inh:
            id_neurona = match_inh.group(1).upper()
            if id_neurona in neuronas_estado:
                neurona = neuronas_estado[id_neurona]
                if neurona['activacion_actual'] > 0:
                    neurona['activacion_actual'] -= 1
                    print(f"Neurona '{id_neurona}' inhibida. Activación actual: {neurona['activacion_actual']}.")
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
                    # Comando 'topo:' - muestra la topología actual de la red
                    


            if origen_id in neuronas_estado and destino1_id in neuronas_estado and destino2_id in neuronas_estado:
                neurona_origen = neuronas_estado[origen_id]
                neurona_destino1 = neuronas_estado[destino1_id]
                neurona_destino2 = neuronas_estado[destino2_id]

                if neurona_origen['activacion_actual'] >= 2: 
                    neurona_origen['activacion_actual'] -= 2 
                    neurona_destino1['activacion_actual'] = min(neurona_destino1['activacion_actual'] + 1, neurona_destino1['limite_activacion'])
                    neurona_destino2['activacion_actual'] = min(neurona_destino2['activacion_actual'] + 1, neurona_destino2['limite_activacion'])
                    
                    print(f"Bifurcación de '{origen_id}' a '{destino1_id}' y '{destino2_id}'.")
                    print(f"  '{origen_id}' (activación: {neurona_origen['activacion_actual']})")
                    print(f"  '{destino1_id}' (activación: {neurona_destino1['activacion_actual']})")
                    print(f"  '{destino2_id}' (activación: {neurona_destino2['activacion_actual']})")
                else:
                    print(f"La neurona '{origen_id}' necesita al menos 2 activaciones para bifurcar.")
            else:
                print("Error: Una o más neuronas especificadas para la bifurcación no existen.")
            continue
        if patron_topo.match(comand):
            if not neuronas_estado:
                print("No hay neuronas creadas actualmente.")
            else:
                print("\n--- TOPOLOGÍA ACTUAL DE LA RED ---")
                for id_neurona, estado in neuronas_estado.items():
                    print(f"• {id_neurona}: bits={estado['bits']}, límite={estado['limite_activacion']}, activación={estado['activacion_actual']}, bin={estado['valor_binario_str']}")
                    continue
        match_nop = patron_nop.match(comand)
        if match_nop:
            id_neurona = match_nop.group(1).upper()
            if id_neurona in neuronas_estado:
                print(f"Neurona '{id_neurona}' mantendrá su estado actual de activación: {neuronas_estado[id_neurona]['activacion_actual']}. (Operación 'nop').")
            else:
                print(f"Error: La neurona '{id_neurona}' no existe.")
            continue

        # --- Comandos de Ayuda ---
        match_help_specific = patron_help_specific.match(comand)
        if match_help_specific:
            cmd_help = match_help_specific.group(2).lower()
            if cmd_help == "crea":
                print("\ncrea: [ID_Neurona], [Número_de_Bits] - Crea una nueva neurona con un ID y un número de bits (su 'tamaño').")
                print("  Ejemplo: crea: N1, 8 (Crea la neurona N1 con 8 bits).")
                print("  El número de bits define su límite de activación como (Bits - 1).")
            elif cmd_help == "out":
                print("\nout: [ID_Neurona] - Muestra el estado actual (bits, activación, valor decimal/binario) de la neurona.")
                print("  Ejemplo: out: N1")
            elif cmd_help == "mov":
                print("\nmov: [ID_Neurona], [Valor_Decimal] - Establece el valor decimal interno de la neurona. El valor se convierte a binario.")
                print("  Ejemplo: mov: N1, 255 (establece el valor de N1 a 255 si tiene suficientes bits).")
                print("  El valor debe estar dentro del rango de bits de la neurona (0 a 2^bits - 1).")
            elif cmd_help == "act":
                print("\nact: [ID_Neurona] - Activa la neurona, incrementando su contador de activación.")
                print("  Si la neurona no ha alcanzado su límite de activación (Bits - 1), la activación aumenta.")
                print("  Se calcula una sumatoria (par/impar según el límite de activación), que representa la 'fuerza' de esta activación.")
            elif cmd_help == "inh":
                print("\ninh: [ID_Neurona] - Inhibe la neurona, decrementando su contador de activación.")
                print("  La activación no puede bajar de 0.")
            elif cmd_help == "bif":
                print("\nbif: [ID_Origen] = [ID_Destino1], [ID_Destino2] - Bifurca 2 puntos de activación de la neurona origen a los destinos.")
                print("  La neurona origen pierde 2 de activación, y cada destino gana 1 (si no excede su límite).")
            elif cmd_help == "nop":
                print("\nnop: [ID_Neurona] - Mantiene el estado de la neurona. No realiza cambios en su activación o valor.")
            elif cmd_help == "comb":
                 print("\ncomb: [ID1] ?+ [ID2] - (Aún no implementado). Este comando se usaría para combinar el estado binario de dos neuronas bajo ciertas condiciones.")
                 print("  Tu descripción: 'comb: combidición: combina según si la caja está llena con 0 en el primer dígito de izquierda a derecha'")
                 print("  'Si A= 2 y B = 2+1 (ya que aquí la caja 2 tiene 1 elemento)'")
                 print("  'comb: A ?+ B = A y B'")
                 print("  'En este caso A se convierte en 100 y b en 1 (una fuga)'")
            else:
                print(f"Ayuda para '{cmd_help}' no disponible.")
            continue

        elif comand == "help" or comand == "ayuda":
            print("\n--- Comandos disponibles ---")
            print("  crea: [ID], [Bits]")
            print("  out: [ID]")
            print("  mov: [ID], [Valor]")
            print("  act: [ID]")
            print("  inh: [ID]")
            print("  bif: [ID_Origen] = [ID_Destino1], [ID_Destino2]")
            print("  nop: [ID]")
            print("  comb: (a implementar)")
            print("\nPara más información: 'help with [comando]' o 'ayuda con [comando]'.")
            print("  Ejemplo: 'help with crea'")
            print("  Para salir: 'salir'")
            print("Espero que te sirva <3")
            continue

        print(f"Comando '{comand}' no reconocido o formato incorrecto. Escribe 'help' o 'ayuda' para ver la lista de comandos.")

# --- Ejecución ---
Bynarium_NeuronasRevisadas() #bif