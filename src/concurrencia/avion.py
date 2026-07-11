import math
import random
import threading
import time


class AvionHilo(threading.Thread):
    def __init__(self, id_vuelo, origen, destino, ruta, ui_queue):
        super().__init__()
        self.id_vuelo = id_vuelo
        self.ruta = ruta
        self.ui_queue = ui_queue
        self.x = ruta[0].x
        self.y = ruta[0].y
        self.velocidad = 2.0
        self.daemon = True  # El hilo muere si se cierra la app

    def run(self):
        self.enviar_log(f"Despegando de {self.ruta[0].nombre} hacia {self.ruta[-1].nombre}")

        for i in range(1, len(self.ruta)):
            nodo_destino = self.ruta[i]
            self.volar_hacia(nodo_destino)

            # Si llegó al nodo y es el destino final (Aeropuerto)
            if i == len(self.ruta) - 1 and nodo_destino.es_aeropuerto:
                self.enviar_log(f"Llegando a Zona de Control: {nodo_destino.nombre}")
                self.evaluar_arbol_aterrizaje(nodo_destino.arbol_aterrizaje)
            else:
                self.enviar_log(f"Cruzando waypoint: {nodo_destino.nombre}")
                time.sleep(0.5)

    def volar_hacia(self, nodo_destino):
        distancia = math.hypot(nodo_destino.x - self.x, nodo_destino.y - self.y)
        while distancia > self.velocidad:
            dx = (nodo_destino.x - self.x) / distancia
            dy = (nodo_destino.y - self.y) / distancia
            self.x += dx * self.velocidad
            self.y += dy * self.velocidad

            # Enviar posición a la GUI a través de la cola (Thread-safe)
            self.ui_queue.put({"tipo": "posicion", "id": self.id_vuelo, "x": self.x, "y": self.y})
            time.sleep(0.05)  # Tasa de actualización (Simula el tiempo de vuelo)
            distancia = math.hypot(nodo_destino.x - self.x, nodo_destino.y - self.y)

    def evaluar_arbol_aterrizaje(self, nodo_arbol):
        """Recorre el árbol de decisión conectado al grafo."""
        self.enviar_log("--- Iniciando Árbol de Aproximación ---")
        actual = nodo_arbol
        while not actual.es_hoja:
            self.enviar_log(f"Evaluando: {actual.pregunta}")
            time.sleep(1.5)  # Pausa para simular procesamiento/comunicación

            # Simulamos una condición aleatoria para el árbol
            respuesta = random.choice([True, True, True, False])  # Más probabilidad de éxito

            if respuesta:
                self.enviar_log("-> Respuesta: SÍ")
                actual = actual.si_nodo
            else:
                self.enviar_log("-> Respuesta: NO")
                actual = actual.no_nodo

        self.enviar_log(f"RESULTADO ÁRBOL: {actual.resultado}")
        self.ui_queue.put({"tipo": "finalizado", "id": self.id_vuelo})

    def enviar_log(self, mensaje):
        self.ui_queue.put({"tipo": "log", "mensaje": f"[{self.id_vuelo}] {mensaje}"})
