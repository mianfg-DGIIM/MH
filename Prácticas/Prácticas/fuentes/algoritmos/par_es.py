from .par import PAR, dist, min, avg

import random, math
import numpy as np


class ES(PAR):
  def __init__(self, archivo_datos, archivo_restrs, k):
    PAR.__init__(self, archivo_datos, archivo_restrs, k)

  def ejecutar_algoritmo(self, max_evals, max_vecinos=-1, max_exitos=-1, sol_inicial=None):
    self.max_evals = max_evals
    self.evals = 0
    if max_vecinos < 0: max_vecinos = 10*self.n
    if max_exitos < 0: max_exitos = int(0.1*max_vecinos)
    mu = phi = 0.3
    alpha = 0.95

    if not sol_inicial:
      s = self.generar_solucion()
    else:
      s = sol_inicial
    f = self.f(s)
    s_best = s.copy()
    f_best = f
    t = mu*f/(-math.log(phi))
    n_vecinos, n_exitos = -1, -1
    while self.evals <= self.max_evals and n_exitos != 0:
      n_vecinos, n_exitos = 0, 0
      while n_vecinos < max_vecinos and n_exitos < max_exitos and self.evals <= self.max_evals:
        s_new = self.generar_vecino(s)
        f_new = self.f(s_new)
        n_vecinos += 1
        incr_f = f_new - f
        if incr_f < 0 or (random.uniform(0, 1) <= math.exp(-incr_f/t)):
          n_exitos += 1
          s = s_new.copy()
          f = f_new
          if f < f_best:
            s_best = s.copy()
            f_best = f
      t *= alpha  # enfriamos
    
    info = {
      "evals" :         self.evals,
      "dg" :            self.dg(s_best),
      "infeasibility" : self.infeasibility(s_best),
      "f" :             f_best
    }
    return s_best, info
