import threading
import time

print("==================================================")
print(" PROBLEMA 1.1: Secuencia con Prioridad Fija (ABCABC)")
print("==================================================\n")

# Definición de semáforos y valores de inicialización
sem_a = threading.Semaphore(1)
sem_b = threading.Semaphore(0)
sem_c = threading.Semaphore(0)

def proceso_a():
    for _ in range(3):
        sem_a.acquire()
        print("A", end=" ", flush=True)
        sem_b.release()

def proceso_b():
    for _ in range(3):
        sem_b.acquire()
        print("B", end=" ", flush=True)
        sem_c.release()

def proceso_c():
    for _ in range(3):
        sem_c.acquire()
        print("C", end=" ", flush=True)
        sem_a.release()

t1 = threading.Thread(target=proceso_a)
t2 = threading.Thread(target=proceso_b)
t3 = threading.Thread(target=proceso_c)

t1.start(); t2.start(); t3.start()
t1.join(); t2.join(); t3.join()
print("\n\n")


print("==================================================")
print(" PROBLEMA 1.2: Secuencia Alternada (ABACABAC)")
print("==================================================\n")

sem_a2 = threading.Semaphore(1)
sem_b2 = threading.Semaphore(0)
sem_c2 = threading.Semaphore(0)

def hilo_a_alt():
    for _ in range(2):
        sem_a2.acquire()
        print("A", end=" ", flush=True)
        sem_b2.release()
        sem_a2.acquire()
        print("A", end=" ", flush=True)
        sem_c2.release()

def hilo_b_alt():
    for _ in range(2):
        sem_b2.acquire()
        print("B", end=" ", flush=True)
        sem_a2.release()

def hilo_c_alt():
    for _ in range(2):
        sem_c2.acquire()
        print("C", end=" ", flush=True)
        sem_a2.release()

ta = threading.Thread(target=hilo_a_alt)
tb = threading.Thread(target=hilo_b_alt)
tc = threading.Thread(target=hilo_c_alt)

ta.start(); tb.start(); tc.start()
ta.join(); tb.join(); tc.join()
print("\n\n")


print("==================================================")
print(" PROBLEMA 1.3: No-Determinismo Regulado ((A o B) C)")
print("==================================================\n")

turno_emisor = threading.Semaphore(1)
sem_c3 = threading.Semaphore(0)
sem_emisores = threading.Semaphore(1)

def emisor_a():
    for _ in range(3):
        sem_emisores.acquire()
        turno_emisor.acquire()
        print("A", end=" ", flush=True)
        turno_emisor.release()
        sem_c3.release()

def emisor_b():
    for _ in range(3):
        sem_emisores.acquire()
        turno_emisor.acquire()
        print("B", end=" ", flush=True)
        turno_emisor.release()
        sem_c3.release()

def receptor_c():
    for _ in range(6):
        sem_c3.acquire()
        print("C", end=" ", flush=True)
        sem_emisores.release()

t_a = threading.Thread(target=emisor_a)
t_b = threading.Thread(target=emisor_b)
t_c = threading.Thread(target=receptor_c)

t_a.start(); t_b.start(); t_c.start()
t_a.join(); t_b.join(); t_c.join()
print("\n\n")


print("==================================================")
print(" PROBLEMA 2: El Comedor Escolar (Recursos Heterogéneos)")
print("==================================================\n")

# Definición de semáforos contadores y valores iniciales
comedor = threading.Semaphore(18)
mostrador_bandejas = threading.Semaphore(2)
abridores = threading.Semaphore(3)
mostrador_postres = threading.Semaphore(2)

def estudiante(id_estudiante, desea_coca, desea_postre):
    comedor.acquire()
    print(f"Estudiante {id_estudiante} entra al comedor.")
    
    mostrador_bandejas.acquire()
    print(f"  -> Estudiante {id_estudiante} toma bandeja.")
    mostrador_bandejas.release()
    
    if desea_coca:
        abridores.acquire()
        print(f"  -> Estudiante {id_estudiante} usa abridor para coca-cola.")
        time.sleep(0.05)
        abridores.release()
    else:
        print(f"  -> Estudiante {id_estudiante} elige agua (sin abridor).")
        
    if desea_postre:
        mostrador_postres.acquire()
        print(f"  -> Estudiante {id_estudiante} toma postre.")
        mostrador_postres.release()
        
    print(f"Estudiante {id_estudiante} come y sale del comedor.")
    comedor.release()

hilos_estudiantes = []
for i in range(4):
    t = threading.Thread(target=estudiante, args=(i+1, i % 2 == 0, i % 3 == 0))
    hilos_estudiantes.append(t)
    t.start()

for t in hilos_estudiantes:
    t.join()
print("\n")


print("==================================================")
print(" PROBLEMA 3: El Puente Levadizo (Monitores y Prioridad)")
print("==================================================\n")

class PuenteLevadizoMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.cond_coches = threading.Condition(self.lock)
        self.cond_barcos = threading.Condition(self.lock)
        self.barcos_esperando = 0
        self.coches_cruzando = 0
        self.puente_levantado = False  # False = Abajo (Coches), True = Arriba (Barcos)

    def entrar_coche(self, id_coche):
        with self.lock:
            while self.puente_levantado or self.barcos_esperando > 0:
                self.cond_coches.wait()
            self.coches_cruzando += 1
            print(f"[COCHE {id_coche}] Entra al puente.")

    def salir_coche(self, id_coche):
        with self.lock:
            self.coches_cruzando -= 1
            print(f"[COCHE {id_coche}] Sale del puente.")
            if self.coches_cruzando == 0:
                self.cond_barcos.notify()

    def entrar_barco(self, id_barco):
        with self.lock:
            self.barcos_esperando += 1
            while self.coches_cruzando > 0:
                self.cond_barcos.wait()
            self.barcos_esperando -= 1
            self.puente_levantado = True
            print(f"[BARCO {id_barco}] Puente levantado. Cruza el río.")

    def salir_barco(self, id_barco):
        with self.lock:
            self.puente_levantado = False
            print(f"[BARCO {id_barco}] Sale. Puente bajado para vehículos.")
            self.cond_coches.notify_all()

puente = PuenteLevadizoMonitor()

def simular_coche(id_c):
    puente.entrar_coche(id_c)
    time.sleep(0.05)
    puente.salir_coche(id_c)

def simular_barco(id_b):
    puente.entrar_barco(id_b)
    time.sleep(0.05)
    puente.salir_barco(id_b)

# Lanzamiento de hilos mixtos de coches y barcos
tc1 = threading.Thread(target=simular_coche, args=(1,))
tb1 = threading.Thread(target=simular_barco, args=(1,))
tc2 = threading.Thread(target=simular_coche, args=(2,))

tc1.start()
tb1.start()
tc2.start()

tc1.join()
tb1.join()
tc2.join()