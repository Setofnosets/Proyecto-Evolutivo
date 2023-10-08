import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import sys

def generaGrafo(nombre):
    
    arch = open(nombre)
    size = int(arch.readline())
    puntos = list(map(int, arch.readline().split()))
    matriz = []
    for i in range(size):
        fila = list(map(int, arch.readline().split()))
        matriz.append(fila[:size])  # Agrega solo las primeras 'columnas' columnas de la fila

    print("DATOS DEL CASO DEL PROBLEMA")
    print("Nombre:", nombre)
    print("Numero de puntos de Steiner:", len(puntos))
    print("Puntos de Steiner:", puntos)

    print("Matriz: ")
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in matriz]))

    arch.close()
    return matriz, puntos, size

def steiner(graph, n, nPuntos, puntos):
    objetivo = [False for i in range(nPuntos)]
    objetivo[0] = True
    visited = [False for i in range(n)]
    visited[puntos[0]] = True
    edge = [None for i in range(n)]

    i = puntos[0]
    timeout = 100
    while not all(objetivo):
        if timeout == 0:
            i = random.randint(0,
                               n - 1)  # Si no se encuentra un camino, se elige un punto aleatorio que ya fue visitado
            while not visited[i]:
                i = random.randint(0, n - 1)
        rand = random.randint(0, n - 1)
        timeout = 100
        while graph[i][rand] == 0:
            if timeout == 0:
                continue
            timeout -= 1
            rand = random.randint(0, n - 1)
        edge[i] = rand
        prev = i
        i = edge[i]
        if rand in puntos:
            objetivo[puntos.index(rand)] = True
        visited[rand] = True
    edge[i] = prev
    print("Solucion:",edge)

    return edge


def mutacion_reconexion_nodo(steiner, puntos, graph):
    nodos_validos = [True if steiner[i] != None else False for i in range(len(steiner))]

    if any(nodos_validos) == False:
        print(nodos_validos)
        return steiner  # Evitar mutar si no hay nodos válidos en la solución

    nodo_origen = random.randint(0, (len(steiner)) - 1)
    while nodos_validos[nodo_origen] == False:
        nodo_origen = random.randint(0, (len(steiner)) - 1)

    # print(nodo_origen)
    # Filtrar los nodos de destino válidos que estén en el árbol y sean conectables desde el nodo origen
    # nodos_destino_validos = [p for p in puntos if p != nodo_origen and any(graph[nodo_origen][p] != 0 for p in range (len(graph[nodo_origen]))) and p in steiner and nodos_validos[p]== True]
    nodos_destinos_validos = [True if graph[nodo_origen][i] != 0 and nodos_validos[i] == True else False for i in
                              range(len(graph[nodo_origen]))]

    if any(nodos_destinos_validos) == False:
        return steiner  # Evitar mutar si no hay nodos de destino válidos

    # nodo_destino = random.choice(nodos_destino_validos)
    nodo_destino = random.randint(0, (len(steiner)) - 1)
    while nodos_destinos_validos[nodo_destino] == False:
        nodo_destino = random.randint(0, (len(steiner)) - 1)
        while nodo_destino == nodo_origen:
            nodo_destino = random.randint(0, (len(steiner)) - 1)

    steiner[nodo_origen] = nodo_destino

    steiner = cortar_exceso(puntos, steiner)

    return steiner


def aptitud(steiner, graph, puntos):
    # Función de aptitud inversamente proporcional al peso total del árbol
    # Eliminar redundancia de aristas
    edge = steiner.copy()
    edge = cortar_exceso(puntos, edge)
    for i in range(len(edge)):
        if edge[i] is not None and edge[edge[i]] == i:
            edge[i] = None

    # Verificar validez del arbol, que todos los aristas sean alcanzables desde el nodo raíz
    if verificar_arbol(edge, puntos) == False:
        return 1000000

    peso_total = sum(graph[i][edge[i]] for i in range(len(edge)) if edge[i] is not None)
    return peso_total


def algoritmo_evolutivo(graph, nPuntos, puntos, generaciones_max):
    print("\n*** Inicio:\n")
    mejor_solucion = steiner(graph, len(graph), nPuntos, puntos)
    imprimir_grafo(matrix, mejor_solucion, puntos)
    mejor_aptitud = aptitud(mejor_solucion, graph, puntos)
    print("\nAptitud Inicial: ", mejor_aptitud)
    mejor_generacion = 0
    for generacion in range(generaciones_max):
        
        solucion_mutada = mutacion_reconexion_nodo(mejor_solucion.copy(), puntos, graph)
        aptitud_mutada = aptitud(solucion_mutada, graph, puntos)
        if aptitud_mutada < mejor_aptitud:
            mejor_solucion = solucion_mutada
            mejor_aptitud = aptitud_mutada
            mejor_generacion = generacion
            #print("*** Generación ", mejor_generacion, ":\n f(x) =", mejor_aptitud, "\n x = ", mejor_solucion, "\n")


    #print("\nAptitud Final : ", mejor_aptitud)
    return mejor_solucion,mejor_generacion


def imprimir_grafo(matrix, edges, puntos):
   
    E = []
    for i in range(len(matrix)):
        if edges[i] is not None:
            if edges[i] != i and edges[i] > i:
                E.append((i, edges[i]))
            else:
                E.append((edges[i], i))
    E.sort()
    #Eliminar duplicados
    E = list(dict.fromkeys(E))

    print("Coordenadas: ",E)
    #print(E)
    print("Pesos: ")
    for i in range(len(E)):
        print(matrix[E[i][0]][E[i][1]], end=' ')

    # Imprimir grafo
    G = nx.from_numpy_array(np.matrix(matrix))
    layout = nx.spring_layout(G)
    edge_colors = ['black' if not edges in E else 'red' for edges in G.edges()]
    vertex_colors = ['blue' if not vertex in puntos else 'green' for vertex in G.nodes()]
    nx.draw(G, pos=layout, edge_color=edge_colors, node_color=vertex_colors, with_labels=True)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos=layout, edge_labels=labels)
    #Cambiar tamaño de la imagen
    plt.rcParams['figure.figsize'] = [10, 10]
    plt.show()

def verificar_arbol(steiner, puntos):
    #Obtener coordenadas de los puntos
    coordenadas = []
    for i in range(len(steiner)):
        if steiner[i] is not None:
            if steiner[i] != i and steiner[i] > i:
                coordenadas.append((i, steiner[i]))
            else:
                coordenadas.append((steiner[i], i))
    coordenadas.sort()

    T = nx.from_edgelist(coordenadas)

    for punto in puntos:
        try:
            if not nx.has_path(T, puntos[0], punto):
                return False
        except nx.NodeNotFound:
            return False

    if not nx.is_tree(T):
        return False

    if not nx.is_connected(T):
        return False

    return True

def cortar_exceso(puntos, steiner):
    coordenadas = []
    for i in range(len(steiner)):
        if steiner[i] is not None:
            if steiner[i] != i and steiner[i] > i:
                coordenadas.append((i, steiner[i]))
            else:
                coordenadas.append((steiner[i], i))
    coordenadas.sort()
    T = nx.from_edgelist(coordenadas)
    nuevo_steiner = steiner.copy()
    if not nx.is_connected(T):
        sub_grafos = nx.connected_components(T)
        for sub_grafo in sub_grafos:
            if puntos[0] not in sub_grafo:
                for nodo in sub_grafo:
                    nuevo_steiner[nodo] = None
    # Quitar nodos finales que no sean puntos
    coordenadas = []
    for i in range(len(steiner)):
        if steiner[i] is not None:
            if steiner[i] != i and steiner[i] > i:
                coordenadas.append((i, steiner[i]))
            else:
                coordenadas.append((steiner[i], i))
    coordenadas.sort()
    T = nx.from_edgelist(coordenadas)
    for node in T.degree:
        if node[1] == 1 and node[0] not in puntos:
            nuevo_steiner[node[0]] = None
    return nuevo_steiner

if __name__ == "__main__":
    if(len(sys.argv) < 3):
        #print("Sintaxis: main.py <nombre_archivo> <tamaño_del_archivo> <puntos_steiner> <número_generaciones>")
        print("Sintaxis: main.py <nombre_archivo> <número_generaciones>")
    else:
        
        matrix, puntos, size = generaGrafo(sys.argv[1])
        #puntos = random.sample(range(int(sys.argv[2])), int(sys.argv[3]))
        #puntos.sort()
        #print(puntos)

        # Usar el algoritmo evolutivo
        solucion_final,mejor_generacion = algoritmo_evolutivo(matrix, len(puntos), puntos, int(sys.argv[2]))
        print("\n**** Mejor Generacion ",mejor_generacion,": \n")
        print("Mejor Solucion:",solucion_final)
        # Imprimir grafo final
        imprimir_grafo(matrix, solucion_final, puntos)
        print("\nMejor Aptitud: ",aptitud(solucion_final, matrix, puntos))