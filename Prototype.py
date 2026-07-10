import tkinter as tk
import math
import time
import threading
import queue
import random


# ==========================================
# 1. ESTRUCTURA DEL ÁRBOL (Toma de decisiones)
# ==========================================
class NodoArbol:
    def __init__(self, pregunta=None, si_nodo=None, no_nodo=None, es_hoja=False, resultado=None):
        self.pregunta = pregunta
        self.si_nodo = si_nodo
        self.no_nodo = no_nodo
        self.es_hoja = es_hoja
        self.resultado = resultado


def generar_arbol_aterrizaje():
    """Genera el árbol de decisión estándar para aproximación a un aeropuerto."""
    # Hojas del árbol (Resultados finales)
    hoja_aterrizaje = NodoArbol(es_hoja=True, resultado="Autorizado para aterrizar. Pista libre.")
    hoja_espera = NodoArbol(es_hoja=True, resultado="Tráfico en pista. Entrando en patrón de espera.")
    hoja_desvio = NodoArbol(es_hoja=True, resultado="Clima severo. Desvío a aeropuerto alterno.")

    # Nodos de decisión
    nodo_trafico = NodoArbol(pregunta="¿Pista libre de tráfico?", si_nodo=hoja_aterrizaje, no_nodo=hoja_espera)
    raiz_clima = NodoArbol(pregunta="¿Clima óptimo para aproximación?", si_nodo=nodo_trafico, no_nodo=hoja_desvio)

    return raiz_clima


# ==========================================
# 2. ESTRUCTURA DEL GRAFO (Red de Rutas)
# ==========================================
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


# ==========================================
# 3. LÓGICA DEL AVIÓN (Concurrencia)
# ==========================================
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
        """Método que se ejecuta en un proceso/hilo independiente para cada avión."""
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


# ==========================================
# 4. INTERFAZ GRÁFICA (Estilo Radar ATC)
# ==========================================
class InterfazRadar:
    def __init__(self, root, grafo):
        self.root = root
        self.root.title("Simulador Radar ATC - Proyecto EDyA")
        self.root.configure(bg="#001100")
        self.grafo = grafo
        self.ui_queue = queue.Queue()
        self.aviones_ui = {}  # Referencias gráficas de los aviones
        self.contador_vuelos = 1

        # Canvas para el Radar
        self.canvas = tk.Canvas(root, width=600, height=500, bg="#001a00", highlightthickness=1,
                                highlightbackground="#00ff00")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Panel lateral para Logs y Controles
        panel_der = tk.Frame(root, bg="#001100")
        panel_der.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Button(panel_der, text="Generar Vuelo UIO -> GYE", command=lambda: self.crear_vuelo("Quito", "Guayaquil"),
                  bg="#004400", fg="#00ff00").pack(fill=tk.X, pady=5)
        tk.Button(panel_der, text="Generar Vuelo GYE -> UIO", command=lambda: self.crear_vuelo("Guayaquil", "Quito"),
                  bg="#004400", fg="#00ff00").pack(fill=tk.X, pady=5)

        tk.Label(panel_der, text="Comunicaciones ATC (Árboles)", bg="#001100", fg="#00ff00",
                 font=("Consolas", 10, "bold")).pack(pady=(20, 5))

        self.consola = tk.Text(panel_der, width=40, height=25, bg="#000000", fg="#00ff00", font=("Consolas", 9))
        self.consola.pack()

        self.dibujar_grafo()
        self.procesar_cola()  # Inicia el loop de eventos seguro

    def dibujar_grafo(self):
        """Dibuja nodos y aristas en el Canvas estilo radar verde."""
        # Dibujar aristas
        visitadas = set()
        for nombre, nodo in self.grafo.nodos.items():
            for vecino in nodo.vecinos:
                par = tuple(sorted([nombre, vecino.nombre]))
                if par not in visitadas:
                    self.canvas.create_line(nodo.x, nodo.y, vecino.x, vecino.y, fill="#005500", dash=(4, 4), width=2)
                    visitadas.add(par)

        # Dibujar nodos
        for nombre, nodo in self.grafo.nodos.items():
            color = "#00ff00" if nodo.es_aeropuerto else "#008800"
            radio = 8 if nodo.es_aeropuerto else 4
            self.canvas.create_oval(nodo.x - radio, nodo.y - radio, nodo.x + radio, nodo.y + radio, fill=color,
                                    outline="#00ff00")
            self.canvas.create_text(nodo.x + 15, nodo.y - 10, text=nombre, fill="#00ff00",
                                    font=("Consolas", 10, "bold"))

    def crear_vuelo(self, origen, destino):
        ruta = self.grafo.obtener_ruta(origen, destino)
        if not ruta: return

        id_vuelo = f"UIO{self.contador_vuelos:03d}"
        self.contador_vuelos += 1

        # Iniciar el proceso (hilo) del avión
        avion = AvionHilo(id_vuelo, origen, destino, ruta, self.ui_queue)
        avion.start()

    def procesar_cola(self):
        """Lee la cola de mensajes de los hilos para actualizar la GUI sin bloqueos."""
        try:
            while True:
                mensaje = self.ui_queue.get_nowait()

                if mensaje["tipo"] == "log":
                    self.consola.insert(tk.END, mensaje["mensaje"] + "\n")
                    self.consola.see(tk.END)

                elif mensaje["tipo"] == "posicion":
                    v_id = mensaje["id"]
                    x, y = mensaje["x"], mensaje["y"]

                    if v_id not in self.aviones_ui:
                        self.aviones_ui[v_id] = self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#ffffff")
                    else:
                        self.canvas.coords(self.aviones_ui[v_id], x - 4, y - 4, x + 4, y + 4)

                elif mensaje["tipo"] == "finalizado":
                    v_id = mensaje["id"]
                    if v_id in self.aviones_ui:
                        # Cambiar color o eliminar cuando aterriza/termina
                        self.canvas.itemconfig(self.aviones_ui[v_id], fill="#ffff00")

        except queue.Empty:
            pass

        # Volver a revisar la cola en 50 milisegundos
        self.root.after(50, self.procesar_cola)


# ==========================================
# 5. INICIALIZACIÓN DEL SISTEMA
# ==========================================
if __name__ == "__main__":
    # 1. Configurar la red espacial (Grafo)
    red_atc = GrafoATC()

    n_quito = NodoGrafo("Quito", 300, 100, es_aeropuerto=True)
    n_latacunga = NodoGrafo("Latacunga (WP)", 300, 200)
    n_manta = NodoGrafo("Manta (WP)", 100, 250)
    n_guayaquil = NodoGrafo("Guayaquil", 150, 400, es_aeropuerto=True)
    n_cuenca = NodoGrafo("Cuenca (WP)", 400, 350)

    # 2. Conectar las aerovías (Aristas)
    n_quito.agregar_vecino(n_latacunga)
    n_latacunga.agregar_vecino(n_guayaquil)
    n_quito.agregar_vecino(n_manta)
    n_manta.agregar_vecino(n_guayaquil)
    n_latacunga.agregar_vecino(n_cuenca)
    n_cuenca.agregar_vecino(n_guayaquil)

    for n in [n_quito, n_latacunga, n_manta, n_guayaquil, n_cuenca]:
        red_atc.agregar_nodo(n)

    # 3. Lanzar la interfaz gráfica
    ventana = tk.Tk()
    app = InterfazRadar(ventana, red_atc)
    ventana.mainloop()