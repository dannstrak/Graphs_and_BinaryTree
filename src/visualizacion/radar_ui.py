import customtkinter as ctk
import tkinter as tk
import queue
import os
import time
from PIL import Image, ImageTk

class ToolTip:
    def __init__(self, widget, text, bg="#1a1a1a", fg="#ffffff", border_color="#00ff41"):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.border_color = border_color
        self.tooltip_window = None

        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return


        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty()

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)

        self.tooltip_window.configure(bg=self.border_color)

        frame = tk.Frame(self.tooltip_window, bg=self.bg, padx=1, pady=1)
        frame.pack(padx=1, pady=1)

        label = tk.Label(frame, text=self.text, bg=self.bg, fg=self.fg,
                         justify="left", font=("Consolas", 18, "bold"), wraplength=450)
        label.pack(padx=15, pady=10)

        self.tooltip_window.update_idletasks()

        w_tooltip = self.tooltip_window.winfo_width()

        x_new = x - w_tooltip - 10

        self.tooltip_window.wm_geometry(f"+{x_new}+{y}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

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
        self.historial_vuelos = {}

        self.scale_x = 1.0
        self.scale_y = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.main_frame = ctk.CTkFrame(self.root, fg_color="#050a05")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.radar_frame = ctk.CTkFrame(self.main_frame, fg_color="#000000", border_width=2, border_color="#00ff41")
        self.radar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(self.radar_frame, bg="#001a1a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ctk.CTkFrame(self.main_frame, width=450, fg_color="#0a140a")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.control_frame.pack_propagate(False)

        self.lbl_titulo = ctk.CTkLabel(self.control_frame, text="CONTROL DE TRÁFICO Y CLIMA",
                                       font=("Consolas", 18, "bold"), text_color="#00ff41")
        self.lbl_titulo.pack(pady=(20, 10))

        self.row_uio_gye = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.row_uio_gye.pack(fill=tk.X, padx=20, pady=5)

        self.btn_uio_gye = ctk.CTkButton(self.row_uio_gye, text="✈ Despachar UIO -> GYE",
                                         command=lambda: self.crear_vuelo("Quito", "Guayaquil"),
                                         font=("Consolas", 14, "bold"), fg_color="#004d00", hover_color="#00cc00")
        self.btn_uio_gye.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.help_uio_gye = ctk.CTkButton(self.row_uio_gye, text="🛈", width=30, height=30,
                                          fg_color="transparent", hover_color="#00cc00", font=("Consolas", 16))
        self.help_uio_gye.pack(side=tk.LEFT, padx=(10, 0))


        ToolTip(self.help_uio_gye,
                "Solicita un nuevo vuelo de Quito a Guayaquil.\n"
                "El sistema calcula automáticamente la ruta óptima,\n"
                "considerando tormentas y aerovías cerradas.")

        self.row_gye_uio = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.row_gye_uio.pack(fill=tk.X, padx=20, pady=5)

        self.btn_gye_uio = ctk.CTkButton(self.row_gye_uio, text="✈ Despachar GYE -> UIO",
                                         command=lambda: self.crear_vuelo("Guayaquil", "Quito"),
                                         font=("Consolas", 14, "bold"), fg_color="#004d00", hover_color="#00cc00")
        self.btn_gye_uio.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.help_gye_uio = ctk.CTkButton(self.row_gye_uio, text="🛈", width=30, height=30,
                                          fg_color="transparent", hover_color="#00cc00", font=("Consolas", 16))
        self.help_gye_uio.pack(side=tk.LEFT, padx=(10, 0))

        ToolTip(self.help_gye_uio,
                "Solicita un nuevo vuelo de Guayaquil a Quito.\n"
                "El sistema calcula automáticamente la ruta óptima,\n"
                "considerando tormentas y aerovías cerradas.")


        ctk.CTkFrame(self.control_frame, height=2, fg_color="#00ff41").pack(fill=tk.X, padx=20, pady=10)

        self.lbl_consola = ctk.CTkLabel(self.control_frame, text="TRANSMISIONES ATC:", font=("Consolas", 14, "bold"),
                                        text_color="#00ff41")
        self.lbl_consola.pack(anchor="w", padx=20, pady=(0, 5))

        self.consola = ctk.CTkTextbox(self.control_frame, font=("Consolas", 12), fg_color="#000000",
                                      text_color="#00ff41", border_width=1, border_color="#004d00")
        self.consola.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        ctk.CTkFrame(self.control_frame, height=2, fg_color="#00ff41").pack(fill=tk.X, padx=20, pady=10)

        self.lbl_buscar = ctk.CTkLabel(self.control_frame, text="CONSULTAR TRAYECTORIA DE VUELO:",
                                       font=("Consolas", 14, "bold"), text_color="#00ff41")
        self.lbl_buscar.pack(anchor="w", padx=20, pady=(0, 5))

        self.frame_buscar = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.frame_buscar.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.entry_buscar_vuelo = ctk.CTkEntry(self.frame_buscar, placeholder_text="Ej: UIO001",
                                               font=("Consolas", 13), fg_color="#000000",
                                               text_color="#00ff41", border_color="#004d00")
        self.entry_buscar_vuelo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_buscar_vuelo.bind("<Return>", lambda evento: self.buscar_vuelo())

        self.btn_buscar_vuelo = ctk.CTkButton(self.frame_buscar, text="🔍 Buscar", width=90,
                                              command=self.buscar_vuelo,
                                              font=("Consolas", 13, "bold"), fg_color="#004d00",
                                              hover_color="#00cc00")
        self.btn_buscar_vuelo.pack(side=tk.LEFT)

        self.mapa_imagen = None
        self.root.after(100, self.configurar_fondo)
        self.procesar_cola()


    def configurar_fondo(self):
        ruta_mapa = "mapa_ecuador.png"
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if os.path.exists(ruta_mapa):
            try:
                img = Image.open(ruta_mapa)
                orig_img_w, orig_img_h = img.size

                ratio = min(canvas_w / orig_img_w, canvas_h / orig_img_h)
                new_w = int(orig_img_w * ratio)
                new_h = int(orig_img_h * ratio)

                self.offset_x = (canvas_w - new_w) // 2
                self.offset_y = (canvas_h - new_h) // 2

                self.scale_x = ratio
                self.scale_y = ratio

                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                self.mapa_imagen = ImageTk.PhotoImage(img)
                self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.mapa_imagen)
            except Exception as e:
                self.consola.insert(tk.END, f"[Sistema] Error al cargar mapa: {e}\n")
                self.dibujar_fallback_radar(canvas_w, canvas_h)
        else:
            self.dibujar_fallback_radar(canvas_w, canvas_h)

        self.dibujar_grafo()

    def dibujar_fallback_radar(self, width, height):
        cx, cy = width / 2, height / 2
        for r in range(50, 800, 50):
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#003300", width=1,
                                    tags="elements_fallback")
        self.canvas.create_line(cx, 0, cx, height, fill="#003300", width=1, tags="elements_fallback")
        self.canvas.create_line(0, cy, width, cy, fill="#003300", width=1, tags="elements_fallback")

    def dibujar_grafo(self):
        self.canvas.delete("elementos_grafo")
        visitadas = set()

        for nombre, nodo in self.grafo.nodos.items():
            nx1 = (nodo.x * self.scale_x) + self.offset_x
            ny1 = (nodo.y * self.scale_y) + self.offset_y

            for vecino in nodo.vecinos:
                par = tuple(sorted([nombre, vecino.nombre]))
                if par not in visitadas:
                    nx2 = (vecino.x * self.scale_x) + self.offset_x
                    ny2 = (vecino.y * self.scale_y) + self.offset_y

                    self.canvas.create_line(nx1, ny1, nx2, ny2, fill="#00ff41", dash=(4, 4), width=1.5,
                                            tags="elementos_grafo")
                    visitadas.add(par)

        for nombre, nodo in self.grafo.nodos.items():
            nx = (nodo.x * self.scale_x) + self.offset_x
            ny = (nodo.y * self.scale_y) + self.offset_y

            if nodo.es_aeropuerto:
                self.canvas.create_rectangle(nx - 10, ny - 10, nx + 10, ny + 10, fill="#00ff41",
                                             outline="#ffffff", width=1.5, tags="elementos_grafo")
            else:
                color_nodo = "#ff0000" if getattr(nodo, 'tiene_tormenta', False) else "#00bb00"
                outline_nodo = "#ffff00" if getattr(nodo, 'tiene_tormenta', False) else "#00ff41"
                self.canvas.create_oval(nx - 7, ny - 7, nx + 7, ny + 7, fill=color_nodo,
                                        outline=outline_nodo, tags="elementos_grafo")

            self.canvas.create_text(nx + 20, ny - 18, text=nombre, fill="#ffffff",
                                    font=("Consolas", 28, "bold"), tags="elementos_grafo")

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

        self.historial_vuelos[id_vuelo] = {
            "origen": origen,
            "destino": destino,
            "ruta": [n.nombre for n in ruta_nodos],
            "eventos_clima": list(eventos_clima),
            "decisiones": [],
            "estado": "En vuelo",
        }

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

                    v_id = mensaje.get("id")
                    if v_id and v_id in self.historial_vuelos:
                        marca_tiempo = time.strftime("%H:%M:%S")
                        detalle = mensaje.get("detalle", mensaje["mensaje"])
                        self.historial_vuelos[v_id]["decisiones"].append(f"[{marca_tiempo}] {detalle}")

                elif mensaje["tipo"] == "posicion":
                    v_id = mensaje["id"]
                    x, y = mensaje["x"], mensaje["y"]
                    estado = mensaje.get("estado", "volando")
                    color_avion = "#ffaa00" if estado == "espera" else "#ffd700"

                    x_scaled = (x * self.scale_x) + self.offset_x
                    y_scaled = (y * self.scale_y) + self.offset_y

                    if v_id in self.aviones_ui:
                        self.canvas.coords(self.aviones_ui[v_id], x_scaled, y_scaled)
                        self.canvas.itemconfig(self.aviones_ui[v_id], fill=color_avion)
                        self.canvas.coords(self.etiquetas_ui[v_id], x_scaled + 20, y_scaled + 20)
                    else:
                        self.aviones_ui[v_id] = self.canvas.create_text(x_scaled, y_scaled, text="✈", fill=color_avion,
                                                                        font=("Arial", 24))
                        self.etiquetas_ui[v_id] = self.canvas.create_text(x_scaled + 20, y_scaled + 20, text=v_id,
                                                                          fill="#ffffff", font=("Consolas", 12, "bold"))

                elif mensaje["tipo"] == "finalizado":
                    v_id = mensaje["id"]
                    if v_id in self.aviones_ui:
                        self.canvas.itemconfig(self.aviones_ui[v_id], fill="#ff0000")
                        self.canvas.itemconfig(self.etiquetas_ui[v_id], fill="#ff0000")
                    if v_id in self.historial_vuelos:
                        self.historial_vuelos[v_id]["estado"] = "Aterrizado"

        except queue.Empty:
            pass

        self.root.after(40, self.procesar_cola)

    def buscar_vuelo(self):
        id_vuelo = self.entry_buscar_vuelo.get().strip().upper()
        if not id_vuelo:
            return

        historial = self.historial_vuelos.get(id_vuelo)
        if not historial:
            self.consola.insert(tk.END, f"[Sistema] No se encontró el vuelo '{id_vuelo}'.\n")
            self.consola.see(tk.END)
            return

        self.mostrar_historial_vuelo(id_vuelo, historial)

    def mostrar_historial_vuelo(self, id_vuelo, historial):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title(f"Trayectoria del vuelo {id_vuelo}")
        ventana.geometry("600x500")
        ventana.configure(fg_color="#050a05")
        ventana.attributes("-topmost", True)

        lbl_encabezado = ctk.CTkLabel(
            ventana,
            text=f"VUELO {id_vuelo}  |  {historial['origen']} → {historial['destino']}  |  Estado: {historial['estado']}",
            font=("Consolas", 14, "bold"), text_color="#00ff41", wraplength=560, justify="left"
        )
        lbl_encabezado.pack(anchor="w", padx=15, pady=(15, 5))

        lbl_ruta = ctk.CTkLabel(
            ventana, text="Ruta: " + " -> ".join(historial["ruta"]),
            font=("Consolas", 12), text_color="#00ff41", wraplength=560, justify="left"
        )
        lbl_ruta.pack(anchor="w", padx=15, pady=(0, 10))

        texto_historial = ctk.CTkTextbox(ventana, font=("Consolas", 12), fg_color="#000000",
                                         text_color="#00ff41", border_width=1, border_color="#004d00")
        texto_historial.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        if historial["eventos_clima"]:
            texto_historial.insert(tk.END, "--- Meteorología al momento del despacho ---\n")
            for evento in historial["eventos_clima"]:
                texto_historial.insert(tk.END, f"[Meteorología] {evento}\n")
            texto_historial.insert(tk.END, "\n")

        texto_historial.insert(tk.END, "--- Decisiones tomadas durante la trayectoria ---\n")
        if historial["decisiones"]:
            for decision in historial["decisiones"]:
                texto_historial.insert(tk.END, decision + "\n")
        else:
            texto_historial.insert(tk.END, "Aún no hay decisiones registradas para este vuelo.\n")

        texto_historial.configure(state="disabled")