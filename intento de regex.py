import re

def Bynarium_regex():
    comand = input("Escribe tu comando: ")

    # Patrón para "out: (una letra o cualquier caracter), (un número entero)"
    # re.IGNORECASE hace que 'out:' coincida con 'Out:' o 'OUT:'
    match = re.match(r"out:0s*([A-Za-z0-9_]+)\s*,\s*(\d+)", comand, re.IGNORECASE)

    if match:
        letra_str = match.group(1) # El primer grupo capturado (la letra)
        cajanum_str = match.group(2) # El segundo grupo capturado (el número)
        
        try:
            cajanum_int = int(cajanum_str)
            print(f"Comando 'out' detectado con Regex:")
            print(f"  Letra: '{letra_str}'")
            print(f"  Número: {cajanum_int}")
            # Aquí puedes usar letra_str y cajanum_int para tu lógica
        except ValueError:
            print("Error: El número en 'out' no es válido.")
    elif comand == "help":
        print("Lista de comandos...")
    else:
        print("Comando no reconocido.")

# Ejemplo de uso:
# Bynarium_regex()