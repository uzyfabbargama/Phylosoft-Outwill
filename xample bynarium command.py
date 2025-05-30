import re

def Bynarium_con_almacenamiento():
    # Diccionario para almacenar los valores asociados a las letras/IDs
    # Se reinicia cada vez que se llama a Bynarium_con_almacenamiento()
    valores_almacenados = {}

    # Patrones para los comandos
    patron_out = re.compile(r"out:\s*([A-Za-z0-9_]+)\s*,\s*(\d+)", re.IGNORECASE)
    patron_mov = re.compile(r"mov:\s*([A-Za-z]+)\s*,\s*(\d+)", re.IGNORECASE) # Adapto el patrón si 'mov' asigna
    patron_get = re.compile(r"get:\s*([A-Za-z0-9_]+)", re.IGNORECASE) # Nuevo comando para obtener un valor
    patron_help = re.compile(r"help|ayuda", re.IGNORECASE)

    while True: # Bucle para que el usuario pueda ingresar múltiples comandos
        comand = input("\nEscribe tu comando (ej. out: A, 10; get: A; mov: Base, 5; help; salir): ").strip()
        
        if comand.lower() == "salir":
            print("Saliendo de Bynarium.")
            break # Sale del bucle

        # --- Intenta hacer coincidir los comandos en orden de prioridad ---

        # 1. Comando 'out' (lo usaré para asignar valores, como en tu ejemplo)
        coincidencia_out = patron_out.match(comand)
        if coincidencia_out:
            letra_key = coincidencia_out.group(1).upper() # Convertir a mayúsculas para consistencia
            cajanum_str = coincidencia_out.group(2)
            try:
                cajanum_int = int(cajanum_str)
                # ¡Aquí asignamos el valor!
                valores_almacenados[letra_key] = cajanum_int
                print(f"Comando 'out' detectado: '{letra_key}' ahora tiene el valor {cajanum_int}.")
                print(f"Valores actuales: {valores_almacenados}")
            except ValueError:
                print(f"Error: El número en el comando 'out' ('{cajanum_str}') no es un entero válido.")
            continue # Continúa al siguiente ciclo del bucle

        # 2. Comando 'mov' (mantengo su lógica si es diferente a 'out', sino, elimínalo)
        # Si 'mov' también asigna valores, la lógica sería muy similar a 'out'.
        # Por ahora, asumiré que 'mov' es para "mover" algo (ej. actualizar un estado)
        coincidencia_mov = patron_mov.match(comand)
        if coincidencia_mov:
            elemento_str = coincidencia_mov.group(1).upper()
            cantidad_str = coincidencia_mov.group(2)
            try:
                cantidad_int = int(cantidad_str)
                # Aquí 'mov' podría actualizar un valor existente, o simular un movimiento
                # Si el elemento ya existe, podrías sumarle o restarle
                if elemento_str in valores_almacenados:
                    valores_almacenados[elemento_str] += cantidad_int # Ejemplo: sumar la cantidad
                    print(f"Comando 'mov' detectado: '{elemento_str}' movido por {cantidad_int}. Nuevo valor: {valores_almacenados[elemento_str]}")
                else:
                    # Si 'mov' debe asignar un valor si no existe
                    valores_almacenados[elemento_str] = cantidad_int
                    print(f"Comando 'mov' detectado: '{elemento_str}' establecido a {cantidad_int}.")

            except ValueError:
                print(f"Error: La cantidad en el comando 'mov' ('{cantidad_str}') no es un entero válido.")
            continue

        # 3. Nuevo comando 'get' para recuperar el valor de una letra
        coincidencia_get = patron_get.match(comand)
        if coincidencia_get:
            letra_key = coincidencia_get.group(1).upper()
            if letra_key in valores_almacenados:
                valor = valores_almacenados[letra_key]
                print(f"El valor de '{letra_key}' es: {valor}")
            else:
                print(f"'{letra_key}' no tiene un valor asignado.")
            continue

        # 4. Comando 'help'
        coincidencia_help = patron_help.match(comand)
        if coincidencia_help:
            print("--- Lista de Comandos ---")
            print("  out: [ID_o_Letra], [valor] - Asigna un valor a un ID. Ejemplo: out: A, 10")
            print("  mov: [ID_o_Letra], [cantidad] - Modifica el valor de un ID. Ejemplo: mov: Base, 50")
            print("  get: [ID_o_Letra] - Obtiene el valor de un ID. Ejemplo: get: A")
            print("  help / ayuda - Muestra esta lista.")
            print("  salir - Termina la ejecución.")
            continue

        # Si ninguno de los anteriores coincide
        print(f"Comando '{comand}' no reconocido o formato incorrecto. Escribe 'help' para ver los comandos.")

# --- Ejecución ---
Bynarium_con_almacenamiento()