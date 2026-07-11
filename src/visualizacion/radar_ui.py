import tkinter as tk
import queue

from Prototype import AvionHilo


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
