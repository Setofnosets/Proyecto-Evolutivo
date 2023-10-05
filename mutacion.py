import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


def generaGrafo(n, p):
    matriz = []
    for i in range(n):
        matriz.append([])
        for j in range(n):
            matriz[i].append(0)
    for i in range(n):
        for j in range(n):
            if random.random() <= p and i != j:
                weight = random.randint(1, 100)
                matriz[i][j] = weight
                matriz[j][i] = weight
    return matriz


def spanningTree(graph, n):
    visited = [False for i in range(n)]
    visited[0] = True
    edge = [None for i in range(n)]
    edge[0] = 0
    for i in range(1, n):
        j = i
        while not visited[j]:
            rand = 0
            while graph[j][rand] == 0:
                rand = random.randint(0, n - 1)
            edge[j] = rand
            j = edge[j]
        j = i
        while not visited[j]:
            visited[j] = True
            j = edge[j]
    return edge


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
    print(edge)

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
    mejor_solucion = steiner(graph, len(graph), nPuntos, puntos)
    imprimir_grafo(matrix, mejor_solucion, puntos)
    mejor_aptitud = aptitud(mejor_solucion, graph, puntos)
    print("\nAptitud Inicial: ", mejor_aptitud)

    for generacion in range(generaciones_max):
        solucion_mutada = mutacion_reconexion_nodo(mejor_solucion.copy(), puntos, graph)
        aptitud_mutada = aptitud(solucion_mutada, graph, puntos)
        if aptitud_mutada < mejor_aptitud:
            mejor_solucion = solucion_mutada
            mejor_aptitud = aptitud_mutada

    print("\nAptitud Final : ", mejor_aptitud)
    return mejor_solucion


def imprimir_grafo(matrix, edges, puntos):
    print("Matriz: ")
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in matrix]))

    E = []
    for i in range(len(matrix)):
        if edges[i] is not None:
            if edges[i] != i and edges[i] > i:
                E.append((i, edges[i]))
            else:
                E.append((edges[i], i))
    E.sort()

    print("Coordenadas: ")
    print(E)

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

    """#Verificar que todos los puntos sean alcanzables desde el nodo raíz

    visited = [False for i in range(len(steiner))]
    objective = [False for i in range(len(puntos))]
    objective[0] = True
    visited[puntos[0]] = True
    i = puntos[0]
    prev = None
    while not all(objective):
        if steiner[i] is None:
            return False
        if visited[steiner[i]] and steiner[i] != prev:
            return False
        elif visited[steiner[i]] and steiner[i] == prev:
            # Encontrar otra rama
            get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
            ocurrence = get_indexes(prev, steiner)
            while len(ocurrence) == 1:
                #backtrack
                prev = steiner.index(prev)
                ocurrence = get_indexes(prev, steiner)
                if ocurrence[0] == prev:
                    return False
            if ocurrence == []:
                return False

        visited[steiner[i]] = True
        if steiner[i] in puntos:
            objective[puntos.index(steiner[i])] = True
        prev = i
        i = steiner[i]
    # Revisar si hay ciclo, si hay, no es un arbol"""

    return True
 # TODO: Preguntar si se deberia utilizar
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

    """if verificar_arbol(steiner, puntos) == False:
        return steiner
    visited = [False for i in range(len(steiner))]
    objective = [False for i in range(len(puntos))]
    objective[0] = True
    visited[puntos[0]] = True
    i = puntos[0]
    nuevo_steiner = steiner.copy()
    while not all(objective):
        visited[steiner[i]] = True
        if steiner[i] in puntos:
            objective[puntos.index(steiner[i])] = True
        i = steiner[i]
    for i in range(len(steiner)):
        if visited[i] == False:
            nuevo_steiner[i] = None
    return nuevo_steiner"""


if __name__ == '__main__':
    matrix = generaGrafo(15, 0.2)
    puntos = random.sample(range(15), 5)
    puntos.sort()
    print(puntos)

    # Usar el algoritmo evolutivo
    solucion_final = algoritmo_evolutivo(matrix, 5, puntos, 10000)
    print("\n Mejor solución:")
    print(solucion_final)

    # Imprimir grafo final
    imprimir_grafo(matrix, solucion_final, puntos)