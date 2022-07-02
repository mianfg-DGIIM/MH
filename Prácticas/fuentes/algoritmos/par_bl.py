from .par import PAR

import random


class BL(PAR):
  def __init__(self, archivo_datos, archivo_restrs, k):
    PAR.__init__(self, archivo_datos, archivo_restrs, k)

  def generar_explorar_vecinos(self, solucion):
    explorar_vecinos = []
    for i in range(self.n):
      for j in range(self.k):
        if j != solucion[i]:
          explorar_vecinos.append((i,j))
    return explorar_vecinos

  def ejecutar_algoritmo(self, max_evals, sol_inicial=None):
    self.max_evals = max_evals
    self.evals = 0
    if not sol_inicial:
      solucion = self.generar_solucion()
    else:
      solucion = sol_inicial
    centroides = self.calcular_centroides(solucion)
    explorar_vecinos = self.generar_explorar_vecinos(solucion)

    random_acceso = list(range(len(explorar_vecinos)))
    random.shuffle(random_acceso)

    stop = False
    restablecer = False
    f_prev = self.f(solucion, centroides)

    while not stop and self.evals < self.max_evals:
      stop = True
      for i in range(len(explorar_vecinos)):
        v = explorar_vecinos[random_acceso[i]]
        index, cluster_to = v[0], v[1]
        cluster_from = solucion[index]
        solucion[index] = cluster_to

        if self.es_solucion(solucion):
          centroides[cluster_to] = self.calcular_centroide(solucion, cluster_to)
          centroides[cluster_from] = self.calcular_centroide(solucion, cluster_from)
          f_vecino = self.f(solucion, centroides)
          if f_vecino < f_prev:
            f_prev = f_vecino
            explorar_vecinos = self.generar_explorar_vecinos(solucion)
            random.shuffle(random_acceso)
            stop = False
            break
          else:
            restablecer = True
        else:
          restablecer = True
        if restablecer:
          solucion[index] = cluster_from
          centroides[cluster_to] = self.calcular_centroide(solucion, cluster_to)
          centroides[cluster_from] = self.calcular_centroide(solucion, cluster_from)
          restablecer = False
    
    info = {
      "evals" :         self.evals,
      "dg" :            self.dg(solucion),
      "infeasibility" : self.infeasibility(solucion),
      "f" :             self.f(solucion)
    }

    return solucion, info
