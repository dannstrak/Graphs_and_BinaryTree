import customtkinter as ctk
import tkinter as tk
import queue
import os
from PIL import Image, ImageTk

class InterfazRadar:
    def __init__(self, root, grafo, gestor_trafico):
        self.root = root
        self.root.title("ATC Command Center - Simulador Radar")
        self.root.geometry("1200x750")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.grafo = grafo
        self.gestor = gestor_trafico
        self.aviones_ui = {}
        self.etiquetas_ui = {}
        self.contador_vuelos = 1

        self.main_frame = ctk.CTkFrame(self.root, fg_color="#050a05")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.radar_frame = ctk.CTkFrame(self.main_frame, fg_color="#000000", border_width=2, border_color="#00ff41")
        self.radar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(self.radar_frame, bg="#001a1a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ctk.CTkFrame(self.main_frame, width=450, fg_color="#0a140a")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.control_frame.pack_propagate(False)

        self.lbl_titulo = ctk.CTkLabel(self.control_frame, text="CONTROL DE TRÁFICO Y CLIMA", font=("Consolas", 18, "bold"), text_color="#00ff41")
        self.lbl_titulo.pack(pady=(20, 10))

        self.btn_uio_gye = ctk.CTkButton(self.control_frame, text="✈ Despachar UIO -> GYE",
                                         command=lambda: self.crear_vuelo("Quito", "Guayaquil"),
                                         font=("Consolas", 14, "bold"), fg_color="#004d00", hover_color="#00cc00")
        self.btn_uio_gye.pack(fill=tk.X, padx=20, pady=5)

        self.btn_gye_uio = ctk.CTkButton(self.control_frame, text="✈ Despachar GYE -> UIO",
                                         command=lambda: self.crear_vuelo("Guayaquil", "Quito"),
                                         font=("Consolas", 14, "bold"), fg_color="#004d00", hover_color="#00cc00")
        self.btn_gye_uio.pack(fill=tk.X, padx=20, pady=5)

        ctk.CTkFrame(self.control_frame, height=2, fg_color="#00ff41").pack(fill=tk.X, padx=20, pady=10)

        self.lbl_consola = ctk.CTkLabel(self.control_frame, text="TRANSMISIONES ATC:", font=("Consolas", 14, "bold"), text_color="#00ff41")
        self.lbl_consola.pack(anchor="w", padx=20, pady=(0, 5))

        self.consola = ctk.CTkTextbox(self.control_frame, font=("Consolas", 12), fg_color="#000000",
                                      text_color="#00ff41", border_width=1, border_color="#004d00")
        self.consola.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.mapa_imagen = None
        self.root.after(100, self.configurar_fondo)
        self.procesar_cola()

    def configurar_fondo(self):

        ruta_mapa = "mapa_ecuador.png"
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if os.path.exists(ruta_mapa):
            try:
                img = Image.open(ruta_mapa)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                self.mapa_imagen = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.mapa_imagen)
            except Exception as e:
                self.consola.insert(tk.END, f"[Sistema] Error al cargar mapa: {e}\n")
                self.dibujar_anillos_radar(width, height)
        else:
            self.dibujar_anillos_radar(width, height)

        self.dibujar_grafo()

    def dibujar_anillos_radar(self, width, height):
        cx, cy = width / 2, height / 2
        for r in range(50, 800, 50):
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#002200", width=1)
        self.canvas.create_line(cx, 0, cx, height, fill="#002200", width=1)
        self.canvas.create_line(0, cy, width, cy, fill="#002200", width=1)

    def dibujar_grafo(self):
        self.canvas.delete("elementos_grafo")

        visitadas = set()
        for nombre, nodo in self.grafo.nodos.items():
            for vecino in nodo.vecinos:
                par = tuple(sorted([nombre, vecino.nombre]))
                if par not in visitadas:
                    self.canvas.create_line(nodo.x, nodo.y, vecino.x, vecino.y, fill="#00ff41", dash=(2, 4), width=1,
                                            tags="elementos_grafo")
                    visitadas.add(par)

        for nombre, nodo in self.grafo.nodos.items():
            if nodo.es_aeropuerto:
                self.canvas.create_rectangle(nodo.x - 8, nodo.y - 8, nodo.x + 8, nodo.y + 8, fill="#00ff41",
                                             outline="#ffffff", width=1, tags="elementos_grafo")
            else:
                color_nodo = "#ff0000" if getattr(nodo, 'tiene_tormenta', False) else "#008800"
                outline_nodo = "#ffff00" if getattr(nodo, 'tiene_tormenta', False) else "#00ff41"
                self.canvas.create_oval(nodo.x - 5, nodo.y - 5, nodo.x + 5, nodo.y + 5, fill=color_nodo,
                                        outline=outline_nodo, tags="elementos_grafo")

            self.canvas.create_text(nodo.x + 15, nodo.y - 15, text=nombre, fill="#ffffff",
                                    font=("Consolas", 11, "bold"), tags="elementos_grafo")

    def crear_vuelo(self, origen, destino):
        ruta_nodos, eventos_clima = self.grafo.obtener_ruta(origen, destino)
        if not ruta_nodos: return

        self.dibujar_grafo()

        id_vuelo = f"UIO{self.contador_vuelos:03d}"
        self.contador_vuelos += 1

        if eventos_clima:
            for evento in eventos_clima:
                self.consola.insert(tk.END, f"[Meteorología] {evento}\n")
        else:
            self.consola.insert(tk.END, f"[Meteorología] Cielos despejados. Ruta óptima natural.\n")

        ruta_texto = " -> ".join([n.nombre for n in ruta_nodos])
        self.consola.insert(tk.END, f"[Torre] Vuelo {id_vuelo} enrutado por: {ruta_texto}\n")
        self.consola.see(tk.END)

        ruta_limpia = [
            {'x': n.x, 'y': n.y, 'nombre': n.nombre, 'es_aeropuerto': n.es_aeropuerto, 'arbol': n.arbol_aterrizaje} for
            n in ruta_nodos]
        plan_vuelo = {'id_vuelo': id_vuelo, 'origen': origen, 'destino': destino, 'ruta': ruta_limpia}
        self.gestor.asignar_vuelo(plan_vuelo)

    def procesar_cola(self):
        try:
            while True:
                mensaje = self.gestor.cola_ui.get_nowait()

                if mensaje["tipo"] == "log":
                    self.consola.insert(tk.END, mensaje["mensaje"] + "\n")
                    self.consola.see(tk.END)

                elif mensaje["tipo"] == "posicion":
                    v_id = mensaje["id"]
                    x, y = mensaje["x"], mensaje["y"]
                    estado = mensaje.get("estado", "volando")

                    # Naranja si está orbitando, amarillo si vuela normal
                    color_avion = "#ffaa00" if estado == "espera" else "#ffd700"

                    if v_id in self.aviones_ui:

                        self.canvas.coords(self.aviones_ui[v_id], x, y)
                        self.canvas.itemconfig(self.aviones_ui[v_id], fill=color_avion)
                        self.canvas.coords(self.etiquetas_ui[v_id], x + 15, y + 15)
                    else:

                        self.aviones_ui[v_id] = self.canvas.create_text(x, y, text="✈", fill=color_avion, font=("Arial", 20))
                        self.etiquetas_ui[v_id] = self.canvas.create_text(x + 15, y + 15, text=v_id, fill="#ffffff", font=("Consolas", 10, "bold"))

                elif mensaje["tipo"] == "finalizado":
                    v_id = mensaje["id"]
                    if v_id in self.aviones_ui:
                        self.canvas.itemconfig(self.aviones_ui[v_id], fill="#ff0000")
                        self.canvas.itemconfig(self.etiquetas_ui[v_id], fill="#ff0000")

        except queue.Empty:
            pass

        self.root.after(40, self.procesar_cola)