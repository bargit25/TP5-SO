"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 2: El Problema del Oso y las Abejas
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.4 (Sincronización con semáforos)
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10                  # Capacidad del tarro de miel
NUM_ABEJAS = 5          # Número de abejas obreras
tarro_miel = 0          # Variable compartida
simulacion_activa = True

# TODO PARA EL ESTUDIANTE:
# 1. Define los mecanismos de sincronización necesarios:
# - Un cerrojo (Lock) o semáforo binario para exclusión mutua en el tarro.
# - Un semáforo para despertar al oso cuando el tarro esté lleno.
# - Un semáforo para que las abejas esperen si el tarro está lleno o el oso está comiendo.

# Mecanismos de sincronización:
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_abejas = threading.Semaphore(M) # Las abejas pueden llenar hasta M porciones

def abeja(id_abeja):
    global tarro_miel, simulacion_activa
    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))
        
        # 1. Esperar a que el tarro esté disponible.
        sem_abejas.acquire()
        
        # 2. Entrar en exclusión mutua con el tarro
        mutex.acquire()
        if not simulacion_activa:
            mutex.release()
            sem_abejas.release()
            break
        # 3. Depositar una porción de miel (tarro_miel += 1).    
        tarro_miel += 1
        print(f"🐝 Abeja {id_abeja} depositó miel. Tarro: {tarro_miel}/{M}")
        
        # 4. Si tarro_miel == M, avisar/despertar al oso dormido.
        if tarro_miel == M:
            print("🍯 ¡El tarro está lleno! Despertando al oso...")
            sem_oso.release()
        else:
            # 5. Si no está lleno, permitir que otras abejas sigan produciendo.
            sem_abejas.release()
            
        mutex.release()
        
        pass

def oso(max_tarros=2):
    global tarro_miel, simulacion_activa
    tarros_comidos = 0
    while tarros_comidos < max_tarros:
        
        # Espera pasivamente hasta que el tarro alcance M porciones
        sem_oso.acquire()
        
        if not simulacion_activa:
            break
            
        print("\n" + "="*40)
        print("🐻 El oso se despierta y se come toda la miel!")
        print("="*40)
        
        mutex.acquire()
        tarro_miel = 0
        mutex.release()
        
        time.sleep(0.2)
        print("🐻 El oso vuelve a dormir.\n")
        
        # Avisar a las abejas que el tarro está vacío y disponible nuevamente (liberamos M espacios)
        for _ in range(M):
            sem_abejas.release()
            
        tarros_comidos += 1
        time.sleep(0.1)
        
    simulacion_activa = False

if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
    print("=" * 60)
    hilos = []
    
    # Crear e iniciar el hilo del oso
    h_oso = threading.Thread(target=oso, args=(2,))
    hilos.append(h_oso)
    h_oso.start()
    
    # Crear e iniciar los hilos de las N abejas
    for i in range(1, NUM_ABEJAS + 1):
        h_abeja = threading.Thread(target=abeja, args=(i,))
        hilos.append(h_abeja)
        h_abeja.start()
        
    # Esperar a que terminen todos los hilos
    for h in hilos:
        h.join()
        
    print("\n" + "=" * 60)
    print(" Simulación del Oso y las Abejas Finalizada con Éxito")
    print("=" * 60)
    
    pass

