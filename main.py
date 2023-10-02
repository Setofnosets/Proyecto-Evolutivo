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
    while not all(objetivo):
        rand = random.randint(0, n - 1)
        while graph[i][rand] == 0:
            rand = random.randint(0, n - 1)
        if visited[rand]:
            continue
        edge[i] = rand
        i = edge[i]
        if rand in puntos:
            objetivo[puntos.index(rand)] = True
        visited[rand] = True
    return edge

def mutacion(graph, steiner, n, puntos, npuntos): #Elegir un punto con conexiones, cortar una de estas y seleccionar a otro punto con conexiones
    pass

if __name__ == '__main__':
    matrix = generaGrafo(10, 0.3)
    puntos = random.sample(range(10), 3)
    puntos.sort()
    print(puntos)
    st = steiner(matrix, 10, 3, puntos)
    print(st)
    """tree = spanningTree(matrix, 10)"""
    print("Matriz: ")
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in matrix]))
    """E = []
    for i in range(10):
        if tree[i] != i and tree[i] > i:
            E.append((i, tree[i]))
        else:
            E.append((tree[i], i))"""
    E = []
    for i in range(10):
        if st[i] == None:
            continue
        if st[i] != i and st[i] > i:
            E.append((i, st[i]))
        else:
            E.append((st[i], i))
    E.sort()
    print("Coordenadas: ")
    print(E)
    print("Pesos: ")
    for i in range(len(E)):
        print(matrix[E[i][0]][E[i][1]], end=' ')
    print()
    G = nx.from_numpy_array(np.matrix(matrix))
    layout = nx.spring_layout(G)
    edge_colors = ['black' if not edge in E else 'red' for edge in G.edges()]
    vertex_colors = ['blue' if not vertex in puntos else 'green' for vertex in G.nodes()]
    nx.draw(G, pos=layout, edge_color=edge_colors, node_color=vertex_colors, with_labels=True)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos=layout, edge_labels=labels)
    plt.show()



