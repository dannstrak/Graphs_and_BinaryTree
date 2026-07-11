import math
from src.logica.aproximacion import generar_arbol_aterrizaje

class NodoGrafo:
    def __init__(self, nombre, x, y, es_aeropuerto=False):
        self.nombre = nombre
        self.x = x
        self.y = y
        self.es_aeropuerto = es_aeropuerto
        self.vecinos = {}  # Diccionario: {NodoVecino: Distancia}

        # Conexión Grafo -> Árbol: Si es aeropuerto, tiene un árbol de decisión
        self.arbol_aterrizaje = generar_arbol_aterrizaje() if es_aeropuerto else None

    def agregar_vecino(self, vecino):
        distancia = math.hypot(self.x - vecino.x, self.y - vecino.y)
        self.vecinos[vecino] = distancia
        vecino.vecinos[self] = distancia  # Grafo no dirigido


class GrafoATC:
    def __init__(self):
        self.nodos = {}

    def agregar_nodo(self, nodo):
        self.nodos[nodo.nombre] = nodo

    def obtener_ruta(self, inicio, fin):
        """Implementación sencilla de Búsqueda en Anchura (BFS) para la ruta."""
        if inicio not in self.nodos or fin not in self.nodos:
            return None

        visitados = set()
        cola = [[self.nodos[inicio]]]

        while cola:
            ruta = cola.pop(0)
            nodo_actual = ruta[-1]

            if nodo_actual.nombre == fin:
                return ruta

            if nodo_actual not in visitados:
                visitados.add(nodo_actual)
                for vecino in nodo_actual.vecinos:
                    nueva_ruta = list(ruta)
                    nueva_ruta.append(vecino)
                    cola.append(nueva_ruta)
        return None
