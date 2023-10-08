import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def crear(nombre):

    archivo = open(nombre, "r")
    #sizes[0] = cantidad de puntos, sizes[1] = cantidad de conexiones
    sizes = list(map(int, archivo.readline().split()))
    #Genera matriz con ceros
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
    puntos = list(map(int, archivo.readline().split()))

    archivo.close()

    return matriz, puntos, sizes[0]

matriz, puntos, size = crear("steinb2.txt")
G = nx.from_numpy_array(np.array(matriz))
layout = nx.spring_layout(G)
nx.draw(G, layout, with_labels=True)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos=layout, edge_labels=labels)
plt.show()
