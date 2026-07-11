import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor
from src.concurrencia.avion import Avion


def proceso_trabajador(id_proceso, cola_tareas, cola_ui, limite_hilos):
    """Se ejecuta en un núcleo físico independiente."""
    with ThreadPoolExecutor(max_workers=limite_hilos) as pool_hilos:
        while True:
            tarea = cola_tareas.get()

            if tarea == "KILL":
                cola_ui.put({"tipo": "log", "mensaje": f"Proceso {id_proceso} apagado."})
                break

            avion = Avion(
                id_vuelo=tarea['id_vuelo'],
                origen_nombre=tarea['origen'],
                destino_nombre=tarea['destino'],
                ruta_coordenadas=tarea['ruta'],
                cola_ui=cola_ui
            )
            pool_hilos.submit(avion.ejecutar_vuelo)

class GestorTrafico:
    def __init__(self):
        self.nucleos_totales = multiprocessing.cpu_count()
        self.num_procesos = max(1, self.nucleos_totales - 2)
        self.hilos_por_proceso = 20

        self.cola_ui = multiprocessing.Queue()
        self.colas_trabajadores = [multiprocessing.Queue() for _ in range(self.num_procesos)]
        self.procesos = []

        self.indice_asignacion = 0

    def iniciar_procesos(self):
        """Levanta los procesos físicos según el hardware disponible."""
        self.cola_ui.put({"tipo": "log", "mensaje": f"Hardware detectado: {self.nucleos_totales} núcleos."})
        self.cola_ui.put({"tipo": "log", "mensaje": f"Levantando {self.num_procesos} procesos trabajadores."})
        self.cola_ui.put(
            {"tipo": "log", "mensaje": f"Capacidad teórica: {self.num_procesos * self.hilos_por_proceso} vuelos."})

        for i in range(self.num_procesos):
            p = multiprocessing.Process(
                target=proceso_trabajador,
                args=(i, self.colas_trabajadores[i], self.cola_ui, self.hilos_por_proceso),
                daemon=True
            )
            p.start()
            self.procesos.append(p)

    def asignar_vuelo(self, plan_vuelo_dict):
        """Asigna vuelos con balanceo de carga Round-Robin."""
        trabajador_seleccionado = self.indice_asignacion % self.num_procesos
        self.colas_trabajadores[trabajador_seleccionado].put(plan_vuelo_dict)
        self.indice_asignacion += 1

    def detener_todo(self):
        """Envía señal de apagado seguro a todos los procesos."""
        for cola in self.colas_trabajadores:
            cola.put("KILL")
        for p in self.procesos:
            p.join()