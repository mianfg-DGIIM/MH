import random
import numpy as np
from math import sqrt


def dist(d1, d2):
  #suma = 0
  #for i in range(len(d1)):
  #  suma += (d1[i]-d2[i])**2
  #return sqrt(suma)
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
  cluster_indices = []

  def __init__(self, archivo_datos, archivo_restrs, k):
    self.k = k
    self._leer_datos(archivo_datos)
    self._leer_restrs(archivo_restrs)
    self._calcular_dists_datos()
    self._inicializar_clusters()
  
  def __str__(self):
    return f"datos: {self.datos}\n" \
      + f"clusters: {self.clusters}\n" \
      + f"n: {self.n}\n" \
      + f"k: {self.k}\n" \
      + f"d: {self.d}\n" \
      + f"nr: {self.nr}\n"
    #print("restr_mat: ", self.restr_mat)
    #print("restr_list: ", self.restr_list)
    #print("centroides: ", self.centroides)
  
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
    self.cluster_indices = [None]*self.k

  def _actualizar_centroides(self):
    self.centroides = []
    for i in range(self.k):
      #c = self.get_centroide(i) 
      self.centroides.append(self.get_centroide(i))
  
  def _actualizar_centroide(self, id_cluster):
    self.centroides[id_cluster] = self.get_centroide(id_cluster)

  def _generar_clusters_iniciales(self):
    self.clusters = list(range(self.k))
    for _ in range(self.k, self.n):
      self.clusters.append(random.randrange(0, self.k))
    random.shuffle(self.clusters)
    self._actualizar_centroides()
  
  def _generar_centroides_aleatorios(self):
    inds = list(range(self.n))
    random.shuffle(inds)
    for i in range(self.n):
      self.centroides.append(self.datos[inds[i]].copy())

  def get_dist_maxima(self):
    return max([max(row) for row in self.datos])

  def calcular_cluster_indices(self, id_cluster, clusters):
    return [i for i in range(self.n) if clusters[i] == id_cluster]
  
  def get_cluster_indices(self, id_cluster):
    if not self.cluster_indices[id_cluster]:
      self.cluster_indices[id_cluster] = self.calcular_cluster_indices(id_cluster, self.clusters)
    return self.cluster_indices[id_cluster]
    #return [i for i in range(self.n) if self.clusters[i] == id_cluster]
    #return self.calcular_cluster_indices(id_cluster, self.clusters)

  def calcular_cluster_datos(self, id_cluster, clusters):
    return self.datos[self.calcular_cluster_indices(id_cluster, clusters)]
  
  def get_cluster_datos(self, id_cluster):
    #return self.datos[self.get_cluster_indices(id_cluster)]
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
    inf_0 = self.get_infeasibility()#0
    #inf_0 = 0
    #for j in range(self.n):
    #  if self.v(self.clusters, (i, j, self.restr_mat[i][j])):
    #    inf_0 += 1
    restore = self.clusters[i]
    self.clusters[i] = j
    
    inf_1 = self.get_infeasibility()#0
    #inf_1 = 0
    #for j in range(self.n):
    #  if self.v(self.clusters, (i, j, self.restr_mat[i][j])):
    #    inf_1 += 1
    self.clusters[i] = restore
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