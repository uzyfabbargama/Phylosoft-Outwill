# Manual de Lenguaje Operativo Bynarium (v0.1)

 `Lo que tengo planeado para la próxima versión:`

**Autor:** \Uziel Fabio Gamarra Barrionuevo
**Compilador:** Bynarium CLI / Simulador de Neuronas Simbólicas
**Versión del lenguaje:** v0.1
**Fecha:** 2025

---

## ✨ Introducción

**Bynarium** es un paradigma computacional estructural-simbólico. A diferencia de los modelos de IA estadística tradicionales, Bynarium trabaja con **neuronas estructuradas** que se combinan, bifurcan y expanden para procesar información de forma evolutiva, modular y comprensible.

Este manual está diseñado para usuarios que quieran operar un sistema simbólico Bynarium usando un conjunto de comandos funcionales y legibles.

---

## 🔧 Comandos disponibles

### creación y estructura

* `crea: [ID], [Bits]` → Crea una neurona con identificador y cantidad de bits. Ej: `crea: A1, 2`
* `preset: [Topología], [Prefijo_ID], [Cantidad]` → Crea redes preestructuradas.

### manipulación simbólica

* `mov: [ID], [Valor]` → Mueve un valor simbólico a una neurona/sensor.
* `act: [ID]` → Activa una neurona.
* `inh: [ID]` → Inhibe una neurona.
* `nop: [ID]` → Neurona sin operación, estado pasivo.

### combinatoria estructural

* `comb: [ID1] ?+ [ID2]` → Combidición: combina contenido de dos neuronas para formar una nueva.
* `comb: [ID1] ?- [ID2]` → Descombidición (inverso): extrae lo que contribuyó ID2 a ID1.
* `fusion: [ID1], [ID2] -> [ID3]` → Fusiona dos neuronas en una tercera.
* `fus: [ID1], [ID2], [Cant]` → Transfiere parte del contenido de ID1 a ID2.
* `bif: [ID] = [ID2], [ID3]` → Bifurca una neurona en dos caminos estructurales.

### almacenamiento y flujo

* `guar` / `carg` → Guarda y carga estado completo del sistema.
* `log: [ID]?` → Muestra historial de una neurona.
* `ruta: [ID1] -> [ID2]` → Define una ruta de transferencia.

### control

* `reset` → Reinicia el sistema.
* `loop: [ID], [Veces]` → Ejecuta acción repetitiva.
* `pausa: [ms]` → Espera una cantidad de milisegundos.
* `evento: [ID_Cond], [Tipo], [Valor], [ID_Acc], [TipoAcc]` → Ejecuta acción cuando una condición se cumple.
* `eval` / `ciclo` → Ciclo de evaluación general.

### replicación y topología

* `copia: [ID1], [ID2]` → Copia contenido.
* `topo: [ID]` → Muestra topología local de una neurona.

---

## ⚖️ Conceptos Bynarium Clave

### Tipos de neuronas

* `sX`: sensor básico (1 bit)
* `A`: neurona de 2 bits
* `B`: neurona de 4 bits
* `C`: neurona de 6 bits (expandible)

### Combidición

Operación simbólica central:

```bash
comb: A1 ?+ A2
```

* Si A1 está llena y A2 tiene información compatible, se combinan para crear una caja extendida.
* Puede generar extensiones, activaciones en cascada, o escapes simbólicos.

### Capacidad de caja

* Se calcula según el tipo de caja (bits).
* Si se excede, se crea una **extensión**:

```bash
comb: C1 ?+ C2 -> C3extC4
```

* La combinación almacena el contenido simbólico más la clave.

---

## 🔢 Ejemplo simbólico: "Hola"

```bash
crea: A1, 2
mov: s8, h
mov: s15, o
comb: s8 ?+ s15 -> A1
out: A1
```

## 🧩 Ejemplo de palabra extendida: "Bynarium"

```bash
crea: C1, 6
crea: C2, 6
mov: s2, b
mov: s25, y
mov: s14, n
mov: s1, a
mov: s18, r
mov: s9, i
mov: s21, u
mov: s13, m
comb: C1 ?+ C2 -> C1extC2
```

---

## 🌈 Filosofía Bynarium

> Estructura es inteligencia.
> El cálculo no nace del azar, sino de la forma.
> Allí donde GPT busca estadística, Bynarium propone geometría.

---

## 📖 Apócrifo / En desarrollo

* `split`: separar partes de una caja.
* `meta`: anotar genealogía estructural.
* `visual`: mostrar conexiones como grafo.

---

**Gracias por crear inteligencia con estructura.**
Este es sólo el inicio de una nueva forma de pensar cómo piensa una máquina.

---

**Contacto, comunidad y contribuciones:**
\Uzielgamarra733@gmail.com

**Licencia:** Libre para usos educativos, experimentales y simbólicos.
MIT LICENSE
**v0.1**
