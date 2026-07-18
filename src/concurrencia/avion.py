import math
import time
import random


class Avion:
    def __init__(self, id_vuelo, origen_nombre, destino_nombre, ruta_coordenadas, cola_ui):
        self.id_vuelo = id_vuelo
        self.origen_nombre = origen_nombre
        self.destino_nombre = destino_nombre
        self.ruta = ruta_coordenadas
        self.cola_ui = cola_ui

        self.x = self.ruta[0]['x']
        self.y = self.ruta[0]['y']
        self.velocidad = 2.0

    def ejecutar_vuelo(self):
        self.enviar_log(f"Despegando de {self.origen_nombre} hacia {self.destino_nombre}")

        for i in range(1, len(self.ruta)):
            waypoint_destino = self.ruta[i]
            self.volar_hacia(waypoint_destino)

            if i == len(self.ruta) - 1 and waypoint_destino['es_aeropuerto']:
                self.enviar_log(f"Llegando a Zona de Control: {waypoint_destino['nombre']}")

                self.evaluar_arbol_aterrizaje(waypoint_destino['arbol'], waypoint_destino['x'], waypoint_destino['y'])
            else:
                self.enviar_log(f"Cruzando waypoint: {waypoint_destino['nombre']}")
                time.sleep(0.5)

    def volar_hacia(self, destino):
        distancia = math.hypot(destino['x'] - self.x, destino['y'] - self.y)
        while distancia > self.velocidad:
            dx = (destino['x'] - self.x) / distancia
            dy = (destino['y'] - self.y) / distancia
            self.x += dx * self.velocidad
            self.y += dy * self.velocidad

            self.cola_ui.put({"tipo": "posicion", "id": self.id_vuelo, "x": self.x, "y": self.y, "estado": "volando"})
            time.sleep(0.05)
            distancia = math.hypot(destino['x'] - self.x, destino['y'] - self.y)

    def volar_en_circulos(self, cx, cy, radio=15, vueltas=2):

        pasos = 40
        for _ in range(vueltas):
            for i in range(pasos):
                angulo = (i / pasos) * 2 * math.pi
                self.x = cx + radio * math.cos(angulo)
                self.y = cy + radio * math.sin(angulo)
                self.cola_ui.put(
                    {"tipo": "posicion", "id": self.id_vuelo, "x": self.x, "y": self.y, "estado": "espera"})
                time.sleep(0.05)

    def evaluar_arbol_aterrizaje(self, nodo_arbol, cx, cy):
        self.enviar_log("--- Contactando Torre para Aproximación ---")
        aterrizado = False

        while not aterrizado:
            actual = nodo_arbol
            while actual and not actual.es_hoja:
                time.sleep(0.5)

                respuesta = random.random() < 0.6
                actual = actual.si_nodo if respuesta else actual.no_nodo

            if actual:
                self.enviar_log(f"RESULTADO ÁRBOL: {actual.resultado}")
                if "espera" in actual.resultado.lower() or "desvío" in actual.resultado.lower():
                    self.enviar_log("Pista ocupada. Entrando en patrón de espera (Orbitando)...")
                    self.volar_en_circulos(cx, cy, radio=18, vueltas=2)
                    self.enviar_log("Reevaluando condiciones de aterrizaje...")
                else:
                    self.enviar_log("Aterrizaje exitoso. Bienvenido.")
                    aterrizado = True

        self.cola_ui.put({"tipo": "finalizado", "id": self.id_vuelo})

    def enviar_log(self, mensaje):
        self.cola_ui.put({"tipo": "log", "id": self.id_vuelo, "mensaje": f"[{self.id_vuelo}] {mensaje}", "detalle": mensaje})