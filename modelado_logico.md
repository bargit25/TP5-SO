# 🧩 Problemas de Modelado Lógico: Sincronización y Concurrencia
## Cátedra de Teoría de Sistemas Operativos — UNJu FI 2026

Resuelve los siguientes problemas utilizando pseudocódigo con **Semáforos** (`wait()` y `signal()`) o **Monitores** (variables de condición). Para cada problema:
- Identifica claramente las variables compartidas.
- Especifica el tipo de cada semáforo (binario o contador) y su **valor de inicialización**.
- Escribe el pseudocódigo estructurado de cada hebra o proceso concurrente.

---

## 📌 Mapeo Teórico-Práctico: Del Pseudocódigo a Python (`threading`)

Antes de comenzar a programar en `ejercicios_python/`, utiliza esta guía rápida de equivalencias:

| Concepto Teórico | Notación Lógica / Pseudocódigo | Implementación en Python (`import threading`) |
| :--- | :--- | :--- |
| **Semáforo Binario (Mutex)** | `S = Semáforo(1)` | `S = threading.Semaphore(1)` o `lock = threading.Lock()` |
| **Semáforo de Evento (Señal)** | `S = Semáforo(0)` | `S = threading.Semaphore(0)` |
| **Semáforo Contador (Recursos)** | `S = Semáforo(N)` | `S = threading.Semaphore(N)` |
| **Operación $P$ / Esperar** | `wait(S)` | `S.acquire()` |
| **Operación $V$ / Señalizar** | `signal(S)` | `S.release()` |
| **Crear Monitor / Lock de Estado** | `Monitor M { ... }` | `class MiMonitor: def __init__(self): self.lock = threading.Lock()` |
| **Variable de Condición** | `cond = Condicion()` | `cond = threading.Condition(self.lock)` |
| **Esperar en Condición** | `cond.wait()` | `with self.lock: while not condicion: cond.wait()` |
| **Despertar a un proceso** | `cond.signal()` | `with self.lock: cond.notify()` |
| **Despertar a todos (Broadcast)** | `cond.broadcast()` | `with self.lock: cond.notify_all()` |
| **Crear y lanzar hilo** | `iniciar_hebra(f, args)` | `t = threading.Thread(target=f, args=(...)); t.start()` |
| **Esperar finalización de hilo** | `esperar_hebra(t)` | `t.join()` |

---

## Problema 1: Sincronización de Secuencias Estrictas y Alternadas

Encontrar la secuencia lógica y los valores iniciales de los semáforos que permitan forzar de manera determinista las siguientes trazas de ejecución en un sistema multiproceso:

1. **Secuencia con Prioridad Fija (`ABCABC`):**
   - Un emisor ($A$) y dos receptores ($B$ y $C$) que retiran la misma información en momentos distintos ($B$ tiene prioridad sobre $C$). Secuencia esperada: $A \rightarrow B \rightarrow C \rightarrow A \rightarrow B \rightarrow C...$

// Semáforos binarios para control estricto de turnos
Semaphore sem_a = 1;  // Habilita el inicio del proceso A
Semaphore sem_b = 0;  // Bloquea inicialmente al proceso B
Semaphore sem_c = 0;  // Bloquea inicialmente al proceso C

Proceso A:
    while True:
        wait(sem_a)
        // Sección crítica A
        signal(sem_b)

Proceso B:
    while True:
        wait(sem_b)
        // Sección crítica B
        signal(sem_c)

Proceso C:
    while True:
        wait(sem_c)
        // Sección crítica C
        signal(sem_a)

2. **Secuencia Alternada (`ABACABAC`):**
   - Un emisor ($A$) y dos receptores ($B$ y $C$) que retiran información en forma alternada (comienza $B$). Secuencia esperada: $A \rightarrow B \rightarrow A \rightarrow C \rightarrow A \rightarrow B \rightarrow A \rightarrow C...$

// Semáforos binarios para alternancia de turnos
Semaphore sem_a = 1;  // Habilita al emisor A
Semaphore sem_b = 0;  // Controla el turno del receptor B
Semaphore sem_c = 0;  // Controla el turno del receptor C

Proceso A:
    while True:
        wait(sem_a)
        // Sección crítica A (primer uso)
        signal(sem_b)

        wait(sem_a)
        // Sección crítica A (segundo uso)
        signal(sem_c)

Proceso B:
    while True:
        wait(sem_b)
        // Sección crítica B
        signal(sem_a)

Proceso C:
    while True:
        wait(sem_c)
        // Sección crítica C
        signal(sem_a)

3. **Secuencia con No-Determinismo Regulado (`(A o B) C (A o B) C`):**
   - Dos emisores ($A$ y $B$) y un receptor ($C$). Los emisores compiten al azar, pero el receptor siempre debe intercalarse entre cada emisión: $(A \lor B) \rightarrow C \rightarrow (A \lor B) \rightarrow C...$

// Semáforos binarios y mutex de control
Semaphore turno_emisor = 1;  // Exclusión mutua para la competencia aleatoria entre A y B
Semaphore sem_c = 0;         // Sincroniza la espera obligatoria del receptor C
Semaphore sem_emisores = 1;  // Regula la alternancia entre emisión y recepción

Proceso A:
    while True:
        wait(sem_emisores)
        wait(turno_emisor)
        // Sección crítica A
        signal(turno_emisor)
        signal(sem_c)

Proceso B:
    while True:
        wait(sem_emisores)
        wait(turno_emisor)
        // Sección crítica B
        signal(turno_emisor)
        signal(sem_c)

Proceso C:
    while True:
        wait(sem_c)
        // Sección crítica C
        signal(sem_emisores)

**Tu tarea:**
1. En cada caso, define la cantidad de semáforos necesarios y su inicialización.
2. Escribe el pseudocódigo de cada proceso involucrado con sus llamadas a `wait()` y `signal()`.

---

## Problema 2: El Comedor Escolar (Recursos Heterogéneos)

En un colegio hay un comedor con capacidad para 18 personas. El estudiante, cuando desea comer, entra en el comedor y coge una bandeja con comida de cualquiera de los dos mostradores disponibles; a continuación, selecciona agua o coca cola. Si escoge coca cola, dispone de 3 abridores para abrir la botella; si escoge agua no necesita abridor. Después de la comida puede seleccionar un postre de 2 mostradores disponibles para ello, siempre y cuando desee postre. Cuando termina el postre, o si ha optado por no tomarlo, sale del comedor.

// Semáforos contadores para control de aforo y recursos físicos
Semaphore comedor = 18;            // Controla el aforo máximo de personas en el comedor
Semaphore mostrador_bandejas = 2;  // Controla los 2 mostradores disponibles de bandejas
Semaphore abridores = 3;           // Controla la disponibilidad de los 3 abridores físicos
Semaphore mostrador_postres = 2;   // Controla los 2 mostradores disponibles de postres

Proceso Estudiante():
    wait(comedor)

    wait(mostrador_bandejas)
    tomar_bandeja()
    signal(mostrador_bandejas)

    if (desea_coca_cola == Verdadero):
        wait(abridores)
        abrir_botella()
        signal(abridores)
    else:
        // Si escoge agua, no requiere abridor
        continuar

    if (desea_postre == Verdadero):
        wait(mostrador_postres)
        tomar_postre()
        signal(mostrador_postres)

    comer()
    signal(comedor)

**Tu tarea:**
1. Identifica los semáforos necesarios y su valor de inicialización.
2. Escribe el pseudocódigo del proceso `Estudiante()`.

---

## Problema 3: El Puente Levadizo (Monitores y Prioridad)

Tenemos un puente levadizo sobre un río con las siguientes condiciones de utilización:
- Los barcos tienen siempre prioridad de paso, pero para levantar el puente han de esperar a que no haya ningún coche sobre él.
- Los coches pueden utilizar el puente si no hay ningún barco pasando (en cuyo caso el puente estará levantado) o esperando.

Monitor PuenteLevadizoMonitor:
    // Variables de estado compartidas
    entero barcos_esperando = 0;
    entero coches_cruzando = 0;
    booleano puente_levantado = Falso;  // Falso = Abajo (Coches), Verdadero = Arriba (Barcos)

    // Variables de condición asociadas al monitor
    Condition cond_coches;
    Condition cond_barcos;

    metodo entrar_coche():
        while (puente_levantado or barcos_esperando > 0):
            cond_coches.wait()
        coches_cruzando = coches_cruzando + 1

    metodo salir_coche():
        coches_cruzando = coches_cruzando - 1
        if (coches_cruzando == 0):
            cond_barcos.signal()

    metodo entrar_barco():
        barcos_esperando = barcos_esperando + 1
        while (coches_cruzando > 0):
            cond_barcos.wait()
        barcos_esperando = barcos_esperando - 1
        puente_levantado = Verdadero

    metodo salir_barco():
        puente_levantado = Falso
        cond_coches.broadcast()

**Tu tarea:**
1. Diseña la solución utilizando **Monitores** (variables de condición).
2. Escribe el pseudocódigo para los métodos `entrar_coche()`, `salir_coche()`, `entrar_barco()`, `salir_barco()`.


