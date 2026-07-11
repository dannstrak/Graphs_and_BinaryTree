import tkinter as tk
from Prototype import GrafoATC, NodoGrafo, InterfazRadar

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