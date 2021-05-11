import random, sys
import numpy as np
from math import sqrt


def dist(d1, d2):
  return np.linalg.norm(d2-d1)

class PAR:
  datos = []        # datos: datos[i] = x_i
  clusters = []     # clusters: clusters[i] = c_i
  n = 0             # número de datos: n
  k = 0             # número de clusters: k
  d = 0             # dimensión: d
  nr = 0            # número de restricciones
  restr_mat = []    # (list<int>) matriz de restricciones:
                    #   restr_mat[i][j] = ML(x_i, x_j) if 1
                    #                   = CL(x_i, x_j) if -1
  restr_list = []   # (list<(i, j, tipo)> lista de restricciones:
                    #   restr_list[.] = (x_i, x_j, {-1 ó 1})
  centroides = []   # centroides: centroides[i] = u_i
  dists_datos = []  # distancias entre datos:
                    #   dists_datos[i][j] = d(x_i, x_j)
  evals = 0         # evaluaciones de f

  def __init__(self, archivo_datos, archivo_restrs, k):
    self.k = k
    self._leer_datos(archivo_datos)
    self._leer_restrs(archivo_restrs)
    self._calcular_dists_datos()
    self._inicializar_clusters()
    self._calcular_lambda()
  
  def reset(self):
    self._inicializar_clusters()
  
  def __str__(self):
    return "" \
      + f"\tNum. datos:         {self.n}\n" \
      + f"\tNum. clusters:      {self.k}\n" \
      + f"\tDimensión:          {self.d}\n" \
      + f"\tNum. restricciones: {self.nr}\n"

  def _leer_datos(self, archivo_datos):
    datos = []
    with open(archivo_datos) as archivo:
      for line in archivo:
        datos.append([float(x) for x in line.split(',')])
    self.datos = np.array(datos)
    self.n = len(self.datos)
    self.d = len(self.datos[0])

  def _leer_restrs(self, archivo_restr):
    with open(archivo_restr) as archivo:
      for line in archivo:
        self.restr_mat.append([int(x) for x in line.split(',')])
    
    for i in range(self.n):
      for j in range(i+1, self.n):
        if self.restr_mat[i][j] != 0:
          self.restr_list.append((i, j, self.restr_mat[i][j]))
    
    self.nr = len(self.restr_list)

  def _calcular_dists_datos(self):
    self.dists_datos = \
      [ [dist(self.datos[i], self.datos[j]) for j in range(self.n)] \
        for i in range(self.n) ]
  
  def _inicializar_clusters(self):
    self.clusters = [-1]*self.n

  def _actualizar_centroides(self):
    self.centroides = []
    for i in range(self.k):
      self.centroides.append(self.get_centroide(i))
  
  def _actualizar_centroide(self, id_cluster):
    self.centroides[id_cluster] = self.get_centroide(id_cluster)
  
  def _generar_clusters_iniciales(self):
    self.clusters = list(range(self.k))
    for _ in range(self.k, self.n):
      self.clusters.append(random.randrange(0, self.k))
    random.shuffle(self.clusters)
    self._actualizar_centroides()

  def get_dist_maxima(self):
    return max([max(row) for row in self.datos])

  def calcular_cluster_indices(self, id_cluster, clusters):
    return [i for i in range(self.n) if clusters[i] == id_cluster]
  
  def get_cluster_indices(self, id_cluster):
    return self.calcular_cluster_indices(id_cluster, self.clusters)

  def calcular_cluster_datos(self, id_cluster, clusters):
    return self.datos[self.calcular_cluster_indices(id_cluster, clusters)]
  
  def get_cluster_datos(self, id_cluster):
    return self.datos[self.get_cluster_indices(id_cluster)]

  def v(self, clusters, restr):
    r0, r1, r2 = restr[0], restr[1], restr[2]
    c0, c1 = clusters[r0], clusters[r1]
    return c0 >= 0 and c1 >= 0 \
      and ((r2 == 1 and c0 != c1) \
      or (r2 == -1 and c0 == c1))

  def calcular_infeasibility(self, clusters):
    inf = 0
    for restr in self.restr_list:
      if self.v(clusters, restr):
        inf += 1
    return inf

  def get_infeasibility(self):
    return self.calcular_infeasibility(self.clusters)
  
  def get_incr_infeasibility(self, i, j):
    prev_cluster = self.clusters[i]
    inf_0 = 0
    for k in range(self.n):
      if self.v(self.clusters, (i, k, self.restr_mat[i][k])):
        inf_0 += 1
    self.clusters[i] = j
    inf_1 = 0
    for j in range(self.n):
      if self.v(self.clusters, (i, j, self.restr_mat[i][j])):
        inf_1 += 1
    self.clusters[i] = prev_cluster
    return inf_1 - inf_0

  def calcular_centroide(self, id_cluster, clusters):
    if len(self.calcular_cluster_indices(id_cluster, clusters)) > 0:
      return np.mean(self.datos[self.calcular_cluster_indices(id_cluster, clusters), -self.d:], axis=0)
    else:
      return None
  
  def get_centroide(self, id_cluster):
    return self.calcular_centroide(id_cluster, self.clusters)
  
  def es_clusters_valido(self):
    for i in range(self.k):
      for j in range(self.n):
        if self.clusters[j] == i: break
        if j == len(self.clusters)-1: return False
    return True

  def calcular_dmic(self, id_cluster, clusters):
    return np.average([dist(self.datos[i], self.centroides[id_cluster]) \
      for i in self.calcular_cluster_indices(id_cluster, clusters)])

  def get_dmic(self, id_cluster):
    return self.calcular_dmic(id_cluster, self.clusters)
  
  def calcular_dg(self, clusters):
    return np.average([self.calcular_dmic(i, clusters) \
      for i in range(self.k)])

  def get_dg(self):
    return self.calcular_dg(self.clusters)



# =================================================================================



  def _calcular_lambda(self):
    self.l = self.get_dist_maxima() / self.nr

  def contar_por_cluster(self, solucion):
    per_cluster = [0]*self.k
    for i in solucion:
      per_cluster[i] += 1
    return per_cluster

  def es_solucion(self, solucion):
    return self.contar_por_cluster(solucion).count(0) == 0

  def generar_solucion(self):
    solucion = list(range(self.k))
    for _ in range(self.k, self.n):
      solucion.append(random.randrange(0, self.k))
    random.shuffle(solucion)
    return solucion
  
  def reparar_solucion(self, solucion):
    per_cluster = self.contar_por_cluster(solucion)
    index = per_cluster.index(0) if 0 in per_cluster else -1
    while index >= 0:
      new_cluster = random.randrange(0, self.k)
      while per_cluster[new_cluster] <= 1:
        new_cluster = random.randrange(0, self.k)
      per_cluster[solucion[index]] -= 1
      solucion[index] = new_cluster
      per_cluster[new_cluster] += 1
      index = per_cluster.index(0) if 0 in per_cluster else -1

  def calcular_centroides(self, solucion):
    vs = [[np.array([0]*self.d)]]*self.n
    for i in range(len(solucion)):
      vs[solucion[i]].append(self.datos[i])
    return [np.mean(v, axis=0) for v in vs]
  
  def dmic(self, id_cluster, solucion, centroides):
    s = []
    for i in range(self.n):
      if solucion[i] == id_cluster:
        s.append(dist(self.datos[i], centroides[id_cluster]))
    return np.average(s)
  
  
  """def dmic(self, id_cluster, solucion):
    # recalculando centroides
    centroides = self.calcular_centroides(solucion)
    return self.dmic(id_cluster, solucion, centroides)"""

  def dg(self, solucion):
    centroides = self.calcular_centroides(solucion)
    return np.average([self.dmic(i, solucion, centroides) for i in range(self.k)])
  
  def infeasibility(self, solucion):
    inf = 0
    for restr in self.restr_list:
      if self.v(solucion, restr):
        inf += 1
    return inf

  def f(self, solucion):
    self.evals += 1
    if self.max_evals:#show_pb:
      if self.evals % int(self.max_evals/40) == 0: print('.', end='')
    sys.stdout.flush()
    return self.dg(solucion) + self.infeasibility(solucion) * self.l
