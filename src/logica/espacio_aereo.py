import math
import heapq
import random
from src.logica.aproximacion import generar_arbol_aterrizaje

class NodoGrafo:
    def __init__(self, nombre, x, y, es_aeropuerto=False):
        self.nombre = nombre
        self.x = x
        self.y = y
        self.es_aeropuerto = es_aeropuerto
        self.vecinos = {}
        self.arbol_aterrizaje = generar_arbol_aterrizaje() if es_aeropuerto else None

        self.tiene_tormenta = False
        self.aristas_bloqueadas = []  # Guarda los nombres de las rutas cerradas

    def agregar_vecino(self, vecino):
        distancia = math.hypot(self.x - vecino.x, self.y - vecino.y)
        self.vecinos[vecino] = distancia
        vecino.vecinos[self] = distancia


class GrafoATC:
    def __init__(self):
        self.nodos = {}

    def agregar_nodo(self, nodo):
        self.nodos[nodo.nombre] = nodo

    def actualizar_clima(self):
        for nodo in self.nodos.values():
            nodo.tiene_tormenta = False
            nodo.aristas_bloqueadas = []

        eventos = []
        dado = random.random()

        # 40% de probabilidad: Frente frío en la costa.
        # Bloquea Manta y la ruta directa Latacunga-Guayaquil. Única salida: Cuenca.
        if dado < 0.4:
            lat = self.nodos.get("Latacunga (WP)")
            gye = self.nodos.get("Guayaquil")
            man = self.nodos.get("Manta (WP)")

            if lat and gye and man:
                # Cortar la arista
                lat.aristas_bloqueadas.append(gye.nombre)
                gye.aristas_bloqueadas.append(lat.nombre)
                # Bloquear el nodo costero
                man.tiene_tormenta = True
                eventos.append("Frente frío en la costa (Manta y corredor LAT-GYE cerrados)")

        # 30% de probabilidad: Tormenta en la sierra central.
        # Bloquea Latacunga. Única salida: Manta.
        elif dado < 0.7:
            lat = self.nodos.get("Latacunga (WP)")
            if lat:
                lat.tiene_tormenta = True
                eventos.append("Tormenta severa en Latacunga")

        return eventos

    def obtener_ruta(self, inicio, fin):
        if inicio not in self.nodos or fin not in self.nodos:
            return None, []

        eventos_clima = self.actualizar_clima()

        distancias = {nombre: float('inf') for nombre in self.nodos}
        distancias[inicio] = 0
        padres = {nombre: None for nombre in self.nodos}

        cola_prioridad = [(0, inicio)]

        while cola_prioridad:
            costo_actual, nombre_actual = heapq.heappop(cola_prioridad)
            nodo_actual = self.nodos[nombre_actual]

            if nombre_actual == fin:
                break

            if costo_actual > distancias[nombre_actual]:
                continue

            for vecino, distancia_fisica in nodo_actual.vecinos.items():
                # Penalización por tormenta en el nodo
                factor_nodo = 100.0 if vecino.tiene_tormenta else 1.0

                # Penalización por aerovía cerrada
                factor_arista = 100.0 if vecino.nombre in nodo_actual.aristas_bloqueadas else 1.0

                costo_arista = distancia_fisica * factor_nodo * factor_arista
                nuevo_costo = costo_actual + costo_arista

                if nuevo_costo < distancias[vecino.nombre]:
                    distancias[vecino.nombre] = nuevo_costo
                    padres[vecino.nombre] = nodo_actual
                    heapq.heappush(cola_prioridad, (nuevo_costo, vecino.nombre))

        ruta = []
        nodo_paso = self.nodos[fin]
        while nodo_paso is not None:
            ruta.append(nodo_paso)
            nodo_paso = padres[nodo_paso.nombre]

        ruta.reverse()

        if len(ruta) == 1 and ruta[0].nombre != inicio:
            return None, eventos_clima

        return ruta, eventos_clima