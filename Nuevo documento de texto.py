import re
def Bynarium(): # No necesitas 'comand' como parámetro si lo vas a pedir dentro
    
    # La línea de abajo (comand = "comando") está sobrescribiendo lo que el usuario escribió.
    # Seguramente quieres que el programa use lo que el usuario escribió, así que la eliminaríamos.
    # comand = "comando" 
    letra = str
    letras = []
    cajanum =int
    caja = letra, cajanum
    cajas = []
    activo = int
    out = re.match(r"out:0s*([A-Za-z0-9_]+)\s*,\s*(\d+)", comand, re.IGNORECASE)
    mov = re.match(r"mov:0s*([A-Za-z0-9_]+)\s*,\s*(\d+)", comand, re.IGNORECASE)
    #comand = input ("Escribir un comando, help para lista de comandos") sumatoria
    while True:
        comand = input("Escribe tu comando para bynarium, help/ayuda para lista de comandos: ").strip()
        if comand.lower() == "salir":
            print("Saliendo de Bynarium.")
            break
    if comand == "help with mov" or comand == "ayuda con mov": # Usamos 'or' para cubrir ambas opciones
        print("mov: mueve estructura")
        print("Ejemplo de uso: Mov A, 2")
       
    elif comand == "help with comb"or comand == "ayuda con comb" : # Aquí puedes añadir más 'elif' para otros comandos
         print("comb: combidición: combina según si la caja está llena con 0 en el primer dígito de izquierda a derecha")
         print("Ejemplo de uso: comb: ")
         print("Si A= 2 y B = 2+1 (ya que aquí la caja 2 tiene 1 elemento)")
         print("comb: A ?+ B = A y B")
         print("En este caso A se convierte en 100 y b en 1 (una fuga)")
    elif comand == "help with crea" or comand == "ayuda con crea":
        print("escribe el tamaño de la caja con números enteros: (aquí debes escribir un número del 2 a infinito, (el 1 es para estímulos))")
        print("Escribe una letra: (aquí debes colocar una letra, tanto A o a, o abcdefg, etcétera)")
    elif comand == "help with out" or comand == "ayuda con out":
        print("out: muestra la salida y el resultado de cada caja")
        print("Ejemplo:")
        print("out: A")
        print("Si A vale: 3")
        print("A = 3")
        print("Esto muestra lo que tiene la caja A")
    elif comand == "help with act" or comand == "ayuda con act":
        print("act: activa una neurona, (+1)")
        print("ejemplo de act")
        print("act: A")
        print("activa una neurona, sumándole 1")
        print("algunas neuronas como 3, o 4, dependen de más activaciones que por ejemplo 2, que sólo necesita una")
    elif comand == "help with inh" or comand == "ayuda con inh":
        print("inh: inhibe una neurona, es decir le quita 1 a su activación (-1)")
        print("ejemplo de uso de inh: ")
        print("inh: A")
        print("ésto hace que una neurona pierda 1 de activación")
        print("algunas neuronas como 3, requieren 2 inh para desactivarse") # print("") (para copiar y pegar)
    elif comand == "help with bif" or comand == "ayuda con bif":
        print("bif: bifurca la activación entre dos neuronas")
        print("ejemplo de uso de bif:")
        print("bif : A = B, C")
        print("Lo que hace es dividir la activación")
        print("Si A es 3, posee 2 activaciones posibles, y se las divide a B y C")
        print("Tanto si B y C son 3 o 2")
    elif comand == "help with nop" or "ayuda con nop":
        print("nop: esta mantiene estado, lo que permite que la neurona inopere")
        print("ejemplo de uso de nop:")
        print("nop: A")
        print("mantiene el estado de A, sin sumarla ni inhibirla ni conbidicionarla (?+)")
    elif comand == "help" or comand == "ayuda":
        print("si quieres más información sobre")
        print("mov")
        print("comb")
        print("out")
        print("act")
        print("inh")
        print("bif")
        print("nop")
        print("ejemplo de uso:")
        print("ayuda con comando o help with: ayuda con mov")
        print("Espero que te sirva <3")
    elif comand == "crea" :
        cajanum = int(input("escribe el tamaño de la caja con números enteros"))
        letra = input("Escribe una letra:")
        letras.append({letra})
        caja = letra, cajanum
        cajas.append({caja})
    elif mov:
        letra_str = mov.group(1)
        cajanum_str = mov.group(2)
        try:
            cajanum_int = int(cajanum_str)
            print(f"Comando 'mov' detectado con Regex:")
            print(f"  Letra: '{letra_str}'")
            print(f"  Número: {cajanum_int}")
        except ValueError:
            print("Error: El número en 'out' no es válido.")
    elif out:
        letra_str = out.group(1)
        cajanum_str = out.group(2)
        try:
            cajanum_int = int(cajanum_str)
            print(f"Comando 'out' detectado con Regex:")
            print(f"  Letra: '{letra_str}'")
            print(f"  Número: {cajanum_int}")
        except ValueError:
            print("Error: El número en 'out' no es válido.")
            #print(f"caja actual: {caja}")
    elif comand == "act ":
        if (cajanum - 1) % 2:
            activo = cajanum * ((cajanum+2)/4) #sumatoria de 2+4+6+8+10..(par)
        else:
            activo = ((cajanum+1)/2)^2 #sumatoria de 1+3+5+7+9... (impares)
            
    else: # Si el comando no coincide con ninguno
        print(f"Comando '{comand}' no reconocido. Escribe 'help' o 'ayuda' para ver los comandos.")

#def pedir_entrada_binaria_basico():
    #while True:
       #entrada = input("Ingresa un valor binario (solo 0s y 1s): ")
        #es_binario = True
        #for caracter in entrada:
            #if caracter not in ('0', '1'):
                #es_binario = False
                #break # Salir del bucle interno si encontramos un carácter no binario
        
        #if es_binario and entrada: # Asegurarse de que no esté vacío y sea binario
            #print(f"¡Entrada binaria válida! Has ingresado: {entrada}")
            #return entrada
        #else:
            #print("Entrada no válida. Por favor, ingresa solo 0s y 1s.")

# Ejemplo de uso:
#valor_binario = pedir_entrada_binaria_basico()
#print(f"El valor binario final es: {valor_binario}")
# Para ejecutar tu función:
Bynarium()