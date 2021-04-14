from par import PAR

import random

class BusquedaLocal(PAR):
  l = -1          # lambda
  _explorar_vecinos = []
  _next_vecino = 0

  def __init__(self, archivo_datos, archivo_restrs, k):
    PAR.__init__(self, archivo_datos, archivo_restrs, k)
    self._calcular_lambda()
    self._generar_clusters_iniciales()
  
  def _calcular_lambda(self):
    print("max_dist: ", self.get_dist_maxima())
    self.l = self.get_dist_maxima() / self.nr
  
  def f(self):
    return self.get_dg() + self.get_infeasibility() * self.l

  def restart_vecino_virtual(self):
    self._next_vecino = 0
    self._explorar_vecinos = []
    for i in range(self.n):
      for j in range(self.k):
        if j != self.clusters[i] and len(self.get_cluster_indices(j)) > 1:
          self._explorar_vecinos.append((i,j))
    random.shuffle(self._explorar_vecinos)
  
  def get_next_vecino_virtual(self):
    if self._next_vecino < len(self._explorar_vecinos):
      v = self._explorar_vecinos[self._next_vecino]
    else:
      return None
    while not self.vecino_valido(v):
      self._next_vecino += 1
      if self._next_vecino < len(self._explorar_vecinos):
        v = self._explorar_vecinos[self._next_vecino]
      else:
        return None
    self._next_vecino += 1
    return v
  
  def vecino_valido(self, v):
    # suponiendo que configuración anterior es válida
    index, cluster_to, cluster_from = v[0], v[1], self.clusters[v[0]]
    self.clusters[index] = cluster_to
    cond1 = sum(1 for i in self.clusters if i == cluster_to) > 0
    cond2 = sum(1 for i in self.clusters if i == cluster_from) > 0
    self.clusters[index] = cluster_from
    return cond1 and cond2
    #restore = self.clusters[v[0]]
    #self.clusters[v[0]] = v[1]
    #es_valido = self.es_clusters_valido()
    #self.clusters[v[0]] = restore
    #return es_valido
  
  def apply_vecino(self, v):
    self.clusters[v[0]] = v[1]

  def ejecutar_algoritmo(self, max_iters):
    self._generar_clusters_iniciales()
    it = 0
    stop = False
    f_prev = self.f()
    while it < max_iters and not stop:
      self.restart_vecino_virtual()
      while True:
        v = self.get_next_vecino_virtual()
        if v:
          index, cluster_to, cluster_from = v[0], v[1], self.clusters[v[0]]
          self.clusters[index] = cluster_to
          centroide_prev_cluster_to = self.centroides[cluster_to]
          centroide_prev_cluster_from = self.centroides[cluster_from]
          self._actualizar_centroide(cluster_to)
          self._actualizar_centroide(cluster_from)
          f_new = self.f()
          if f_new < f_prev:
            f_prev = f_new
            break
          else:
            self.clusters[index] = cluster_from
            self.centroides[cluster_to] = centroide_prev_cluster_to
            self.centroides[cluster_from] = centroide_prev_cluster_from
        else:
          stop = True
          break
      it += 1

    print("f: ", self.f())
    print("it: ", it)
    print("desv: ", self.get_dg())
    print("infe: ", self.get_infeasibility())
    return self.clusters
