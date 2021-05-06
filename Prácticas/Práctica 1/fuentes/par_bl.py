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
    self._generar_explorar_vecinos()
  
  def reset(self):
    PAR.reset(self)
    self._generar_clusters_iniciales()
    self._generar_explorar_vecinos()
  
  def _calcular_lambda(self):
    self.l = self.get_dist_maxima() / self.nr
  
  def f(self):
    return self.get_dg() + self.get_infeasibility() * self.l
  
  def _generar_explorar_vecinos(self):
    if len(self._explorar_vecinos) > 0:
      self._explorar_vecinos.clear()
    for i in range(self.n):
      for j in range(self.k):
        if j != self.clusters[i]:
          self._explorar_vecinos.append((i,j))

  def restart_vecino_virtual(self):
    self._next_vecino = 0
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
    restore = self.clusters[v[0]]
    self.clusters[v[0]] = v[1]
    es_valido = self.es_clusters_valido()
    self.clusters[v[0]] = restore
    return es_valido
  
  def apply_vecino(self, v):
    self.clusters[v[0]] = v[1]

  def ejecutar_algoritmo(self, max_iters):
    self._generar_clusters_iniciales()
    self._generar_explorar_vecinos()

    random_acceso = list(range(len(self._explorar_vecinos)))
    random.shuffle(random_acceso)

    stop = False
    restablecer = False
    f_prev = self.f()
    it = 0

    while not stop and it < max_iters:
      stop = True
      for i in range(len(self._explorar_vecinos)):
        v = self._explorar_vecinos[random_acceso[i]]
        index, cluster_to = v[0], v[1]
        cluster_from = self.clusters[index]
        self.clusters[index] = cluster_to

        if self.es_clusters_valido():
          it += 1
          self._actualizar_centroide(cluster_to)
          self._actualizar_centroide(cluster_from)
          f_vecino = self.f()
          if f_vecino < f_prev:
            f_prev = f_vecino
            self._generar_explorar_vecinos()
            random.shuffle(random_acceso)
            stop = False
            break
          else:
            restablecer = True
        else:
          restablecer = True
        if restablecer:
          self.clusters[index] = cluster_from
          self._actualizar_centroide(cluster_to)
          self._actualizar_centroide(cluster_from)
          restablecer = False
    
    print("\tIteraciones empleadas:", it)
    print("\tDesviación general:   ", self.get_dg())
    print("\tInfeasibility:        ", self.get_infeasibility())
    print("\tFunc. objetivo:       ", self.f())
    return self.clusters
