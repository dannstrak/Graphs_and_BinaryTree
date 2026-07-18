import customtkinter as ctk

from src.logica.espacio_aereo import GrafoATC, NodoGrafo
from src.concurrencia.gestor_trafico import GestorTrafico
from src.visualizacion.radar_ui import InterfazRadar


def cerrar_aplicacion(ventana, gestor):
    gestor.detener_todo()
    ventana.destroy()


if __name__ == "__main__":

    red_atc = GrafoATC()

    n_quito = NodoGrafo("Quito", 570, 270, es_aeropuerto=True)
    n_latacunga = NodoGrafo("Latacunga (WP)", 502, 403)
    n_manta = NodoGrafo("Manta (WP)", 175, 362)
    n_guayaquil = NodoGrafo("Guayaquil", 273, 505, es_aeropuerto=True)
    n_cuenca = NodoGrafo("Cuenca (WP)", 415, 668)

    n_quito.agregar_vecino(n_latacunga)
    n_latacunga.agregar_vecino(n_guayaquil)
    n_quito.agregar_vecino(n_manta)
    n_manta.agregar_vecino(n_guayaquil)
    n_latacunga.agregar_vecino(n_cuenca)
    n_cuenca.agregar_vecino(n_guayaquil)

    for n in [n_quito, n_latacunga, n_manta, n_guayaquil, n_cuenca]:
        red_atc.agregar_nodo(n)

    gestor_concurrencia = GestorTrafico()
    gestor_concurrencia.iniciar_procesos()

    ventana = ctk.CTk()
    app = InterfazRadar(ventana, red_atc, gestor_concurrencia)

    ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(ventana, gestor_concurrencia))

    ventana.mainloop()