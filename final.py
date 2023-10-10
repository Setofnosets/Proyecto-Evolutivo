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


def generaGrafoOR(nombre):
    archivo = open(nombre, "r")
    sizes = list(map(int, archivo.readline().split()))
    # Genera matriz con ceros
    matriz = []
    for i in range(sizes[0]):
        matriz.append([])
        for j in range(sizes[0]):
            matriz[i].append(0)

    for i in range(sizes[1]):
        linea = list(map(int, archivo.readline().split()))
        matriz[linea[0] - 1][linea[1] - 1] = linea[2]
        matriz[linea[1] - 1][linea[0] - 1] = linea[2]

    npuntos = int(archivo.readline())
    puntos = []
    while npuntos > 0:
        linea = list(map(int, archivo.readline().split()))
        for i in range(len(linea)):
            puntos.append(linea[i] - 1)
        npuntos -= 1

    print("DATOS DEL CASO DEL PROBLEMA")
    print("Nombre:", nombre)
    print("Numero de puntos de Steiner:", len(puntos))
    print("Puntos de Steiner:", puntos)

    print("Matriz: ")
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in matriz]))

    archivo.close()

    return matriz, puntos, sizes[0]


def steiner(graph, n, nPuntos, puntos):
    objetivo = [False for i in range(nPuntos)]
    objetivo[0] = True
    visited = [False for i in range(n)]
    visited[puntos[0]] = True
    edge = []

    i = puntos[0]
    timeout = 100
    while not all(objetivo):
        if timeout == 0:
            exclude = []
            i = random.randint(0,
                               n - 1)  # Si no se encuentra un camino, se elige un punto aleatorio que ya fue visitado
            while not visited[i]:
                i = random.choice(list(set([i for i in range(n)]) - set(exclude)))
                exclude.append(i)
        rand = random.randint(0, n - 1)
        timeout = n
        exclude = []
        while graph[i][rand] == 0 or visited[rand]:
            if timeout == 0:
                break
            timeout -= 1
            rand = random.choice(list(set([i for i in range(n)]) - set(exclude)))
            exclude.append(rand)
        if timeout == 0:
            continue
        edge.append([i, rand])
        prev = i
        i = rand
        if rand in puntos and not objetivo[puntos.index(rand)]:
            objetivo[puntos.index(rand)] = True
        visited[rand] = True
    edge.append([i, prev])
    print("Solucion:", edge)

    tmp = nx.from_edgelist(edge)
    edge = list(tmp.edges)

    return edge


def mutacion_reconexion_nodo(steiner, puntos, graph):
    # Encontrar nodos ya visitados
    nodos_validos = [False for i in range(len(graph))]
    for nodo in steiner:
        if nodo is not None:
            nodos_validos[nodo[0]] = True
            nodos_validos[nodo[1]] = True

    if any(nodos_validos) == False:
        print(nodos_validos)
        return steiner  # Evitar mutar si no hay nodos válidos en la solución

    nodo_origen = random.randint(0, (len(graph)) - 1)
    while nodos_validos[nodo_origen] == False:
        nodo_origen = random.randint(0, (len(graph)) - 1)

    # Filtrar los nodos de destino válidos que estén en el árbol y sean conectables desde el nodo origen
    nodos_destinos_validos = [True if graph[nodo_origen][i] != 0 and nodos_validos[i] == True else False for i in
                              range(len(graph[nodo_origen]))]

    if any(nodos_destinos_validos) == False:
        return steiner  # Evitar mutar si no hay nodos de destino válidos

    nodo_destino = random.randint(0, (len(graph)) - 1)
    while nodos_destinos_validos[nodo_destino] == False:
        nodo_destino = random.randint(0, (len(graph)) - 1)
        while nodo_destino == nodo_origen:
            nodo_destino = random.randint(0, (len(graph)) - 1)

    conexion = []
    for nodo in steiner:
        if nodo is not None and nodo[0] == nodo_origen:
            conexion.append(nodo[1])
        elif nodo is not None and nodo[1] == nodo_origen:
            conexion.append(nodo[0])

    rand = random.randint(0, len(conexion) - 1)
    for n in steiner:
        if n is not None and n[0] == nodo_origen and n[1] == conexion[rand]:
            steiner.remove(n)
            break
        elif n is not None and n[1] == nodo_origen and n[0] == conexion[rand]:
            steiner.remove(n)
            break

    steiner.append((nodo_origen, nodo_destino))

    steiner = cortar_exceso(puntos, steiner)

    return steiner


def aptitud(steiner, graph, puntos):
    # Función de aptitud inversamente proporcional al peso total del árbol
    # Eliminar redundancia de aristas
    if len(steiner) == 0:
        return 1000000
    edge = steiner.copy()
    edge = cortar_exceso(puntos, edge)

    # Verificar validez del arbol, que todos los aristas sean alcanzables desde el nodo raíz
    if verificar_arbol(edge, puntos) == False:
        return 1000000

    peso_total = sum(graph[edge[i][0]][edge[i][1]] for i in range(len(edge)))
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

    return mejor_solucion, mejor_generacion


def imprimir_grafo(matrix, edges, puntos):
    edges = cortar_exceso(puntos, edges)
    print("Coordenadas: ", edges)

    # print(E)
    print("Pesos: ")
    for i in range(len(edges)):
        print(matrix[edges[i][0]][edges[i][1]], end=' ')

    # Imprimir grafo
    G = nx.from_numpy_array(np.matrix(matrix))
    layout = nx.spring_layout(G)
    edge_colors = ['black' if not edge in edges else 'red' for edge in G.edges()]
    edge_list = list(G.edges())

    for edge in edges:
        if tuple(edge) in edge_list:
            edge_colors[edge_list.index(tuple(edge))] = 'red'
        elif tuple(edge[::-1]) in edge_list:
            edge_colors[edge_list.index(tuple(edge[::-1]))] = 'red'

    vertex_colors = ['blue' if not vertex in puntos else 'green' for vertex in G.nodes()]
    nx.draw(G, pos=layout, edge_color=edge_colors, node_color=vertex_colors, with_labels=True)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos=layout, edge_labels=labels)
    # Cambiar tamaño de la imagen
    plt.rcParams['figure.figsize'] = [10, 10]
    plt.show()


def verificar_arbol(steiner, puntos):
    # Obtener coordenadas de los puntos

    T = nx.from_edgelist(list(steiner))

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
    T = nx.from_edgelist(steiner)
    nuevo_steiner = steiner.copy()
    if not nx.is_connected(T):
        sub_grafos = nx.connected_components(T)
        for sub_grafo in sub_grafos:
            if puntos[0] not in sub_grafo:
                for nodo in sub_grafo:
                    for n in nuevo_steiner:
                        if n is not None and nodo in n:
                            nuevo_steiner.remove(n)
    # Quitar nodos finales que no sean puntos
    T = nx.from_edgelist(nuevo_steiner)
    for node in T.degree:
        if node[1] == 1 and node[0] not in puntos:
            for n in nuevo_steiner:
                if n is not None and node[0] in n:
                    nuevo_steiner.remove(n)

    return nuevo_steiner


if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("Sintaxis: main.py <modo: M/OR> <nombre_archivo> <número_generaciones>")
    else:
        if sys.argv[1] == "OR":
            matrix, puntos, size = generaGrafoOR(sys.argv[2])
        elif sys.argv[1] == "M":
            matrix, puntos, size = generaGrafo(sys.argv[2])
        else:
            print("Sintaxis: main.py <modo: M/OR> <nombre_archivo> <número_generaciones>")
            exit()

        # Usar el algoritmo evolutivo
        solucion_final, mejor_generacion = algoritmo_evolutivo(matrix, len(puntos), puntos, int(sys.argv[3]))
        print("\n**** Mejor Generacion ", mejor_generacion, ": \n")
        print("Mejor Solucion:", solucion_final)
        # Imprimir grafo final
        imprimir_grafo(matrix, solucion_final, puntos)
        print("\nMejor Aptitud: ", aptitud(solucion_final, matrix, puntos))