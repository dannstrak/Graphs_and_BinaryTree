class NodoArbol:
    def __init__(self, pregunta=None, si_nodo=None, no_nodo=None, es_hoja=False, resultado=None):
        self.pregunta = pregunta
        self.si_nodo = si_nodo
        self.no_nodo = no_nodo
        self.es_hoja = es_hoja
        self.resultado = resultado

def generar_arbol_aterrizaje():

    # Hojas del árbol (Resultados finales)
    hoja_aterrizaje = NodoArbol(es_hoja=True, resultado="Autorizado para aterrizar. Pista libre.")
    hoja_espera = NodoArbol(es_hoja=True, resultado="Tráfico en pista. Entrando en patrón de espera.")
    hoja_desvio = NodoArbol(es_hoja=True, resultado="Clima severo. Desvío a aeropuerto alterno.")

    # Nodos de decisión
    nodo_trafico = NodoArbol(pregunta="¿Pista libre de tráfico?", si_nodo=hoja_aterrizaje, no_nodo=hoja_espera)
    raiz_clima = NodoArbol(pregunta="¿Clima óptimo para aproximación?", si_nodo=nodo_trafico, no_nodo=hoja_desvio)

    return raiz_clima