from par import PAR, dist

import random
import numpy as np


class Greedy(PAR):
  def __init__(self, archivo_datos, archivo_restrs, k):
    PAR.__init__(self, archivo_datos, archivo_restrs, k)
    self._generar_centroides_aleatorios()

  def ejecutar_algoritmo(self):
    rsi = list(range(self.n))
    random.shuffle(rsi)
    hay_cambio = True
    while hay_cambio:
      clusters_prev = self.clusters.copy()
      for i in rsi:
        # incrs_inf[j] = incremento en infeasibility de asignar x_i a c_j
        incrs_inf = [self.get_incr_infeasibility(i, j) for j in range(self.k)]
        # lista de los j con el menor incrs_inf[j]
        mins = [j for j in range(len(incrs_inf)) if incrs_inf[j] == min(incrs_inf)]
        # j de mins tal que u_j es el más cercano a x_i
        mins_dist = [dist(self.datos[i], self.centroides[j]) for j in mins]
        self.clusters[i] = mins[mins_dist.index(min(mins_dist))]
      self._actualizar_centroides()
      print(self.clusters)
      hay_cambio = clusters_prev != self.clusters
    return self.clusters