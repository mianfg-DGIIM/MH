import random, sys, math
import numpy as np
from math import sqrt


def dist(d1, d2):
  #return np.linalg.norm(d2-d1)
  s = 0
  for i in range(len(d1)):
    s += (d1[i]-d2[i])**2
  return math.sqrt(s)

def min(v):
  i_min = 0
  f_min = v[i_min]
  for i in range(len(v)):
    if v[i] < f_min:
      i_min = i
      f_min = v[i]
  return i_min

def avg(v):
  return sum(v)/len(v)


class PAR:
  datos = []        # datos: datos[i] = x_i
  n = 0             # número de datos: n
  k = 0             # número de clusters: k
  d = 0             # dimensión: d
  nr = 0            # número de restricciones
  restr_mat = []    # (list<int>) matriz de restricciones:
                    #   restr_mat[i][j] = ML(x_i, x_j) if 1
                    #                   = CL(x_i, x_j) if -1
  restr_list = []   # (list<(i, j, tipo)> lista de restricciones:
                    #   restr_list[.] = (x_i, x_j, {-1 ó 1})
  evals = 0         # evaluaciones de f

  def __init__(self, archivo_datos, archivo_restrs, k):
    self.k = k
    self._leer_datos(archivo_datos)
    self._leer_restrs(archivo_restrs)
    self._calcular_lambda()
  
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
    self.datos = datos
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

  def get_dist_maxima(self):
    return max([max(row) for row in self.datos])

  def v(self, clusters, restr):
    r0, r1, r2 = restr[0], restr[1], restr[2]
    c0, c1 = clusters[r0], clusters[r1]
    return c0 >= 0 and c1 >= 0 \
      and ((r2 == 1 and c0 != c1) \
      or (r2 == -1 and c0 == c1))

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
      to_cluster = random.randrange(0, self.n)
      per_cluster[index] += 1
      per_cluster[solucion[to_cluster]] -= 1
      solucion[to_cluster] = index
      index = per_cluster.index(0) if 0 in per_cluster else -1

  def calcular_centroide(self, solucion, id_cluster):
    count = 0
    centroide = [0]*self.d

    for i in range(len(solucion)):
      if solucion[i] == id_cluster:
        count += 1
        for coord in range(self.d):
          centroide[coord] += self.datos[i][coord]
    for i in range(self.d):
      centroide[i] = centroide[i] / count
    return centroide
  
  def calcular_centroides(self, solucion):
    centroides = []
    for _ in range(self.k):
      centroides.append([0]*self.d)
    count = [0]*self.k

    for i in range(len(solucion)):
      count[solucion[i]] += 1
      for coord in range(self.d):
        centroides[solucion[i]][coord] += self.datos[i][coord]
    for i in range(self.k):
      for j in range(self.d):
        centroides[i][j] = centroides[i][j] / count[i]
    return centroides

  def dmic(self, id_cluster, solucion, centroides):
    s = []
    for i in range(self.n):
      if solucion[i] == id_cluster:
        s.append(dist(self.datos[i], centroides[id_cluster]))
    return avg(s)
  
  def dg(self, solucion, centroides=None):
    if not centroides: centroides = self.calcular_centroides(solucion)
    return avg([self.dmic(i, solucion, centroides) for i in range(self.k)])
    
  def infeasibility(self, solucion):
    inf = 0
    for restr in self.restr_list:
      if self.v(solucion, restr):
        inf += 1
    return inf

  def f(self, solucion, centroides=None):
    self.evals += 1
    if self.max_evals:#show_pb:
      if self.evals % int(self.max_evals/40) == 0: print('.', end='')
    sys.stdout.flush()
    #print(self.evals)
    return self.dg(solucion, centroides) + self.infeasibility(solucion) * self.l

  def cambio_cluster(self, solucion, indice, nuevo_cluster, reparar=False):
    solucion[indice] = nuevo_cluster
    if reparar:
      while not self.es_solucion(solucion):
        solucion[indice] = (solucion[indice]+1)%self.k

  def generar_vecino(self, solucion):
    indice = random.randrange(0, self.n)
    nuevo_cluster = random.randrange(0, self.k)
    vecino = solucion.copy()
    self.cambio_cluster(vecino, indice, nuevo_cluster, reparar=True)
    return vecino
