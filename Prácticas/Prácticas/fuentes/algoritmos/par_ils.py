from .par import PAR, dist, min, avg
from .par_bl import BL
from .par_es import ES

import random, math
import numpy as np

class ILS(PAR):
  def mutar(self, solucion, v):
    r0 = random.randrange(0, self.n)
    r = r0
    while v > 0:
      solucion[r] = random.randrange(0, self.k)
      v -= 1
      r = (r+1)%self.n
    self.reparar_solucion(solucion)

  def __init__(self, archivo_datos, archivo_restrs, k):
    PAR.__init__(self, archivo_datos, archivo_restrs, k)
    self.bl = BL(archivo_datos, archivo_restrs, k)
    self.es = ES(archivo_datos, archivo_restrs, k)
  
  def ejecutar_algoritmo(self, max_evals, num_ejecuciones, v, algoritmo):
    self.max_evals = max_evals
    self.evals = 0
    local = self.es if algoritmo == 'es' else self.bl
    if v < 0: v = int(0.1*self.n)

    # el algoritmo ejecuta una búsqueda local sobre una solución generada
    # si no se le especifica un parámetro, por lo que lo ejecutamos directamente
    print(f"\n\tEjecutando {algoritmo.upper()}  1: ", end="")
    s_best, data = local.ejecutar_algoritmo(max_evals=max_evals/num_ejecuciones)
    f_best = data['f']
    self.evals += data['evals']

    for i in range(num_ejecuciones-1):
      print(f"\n\tEjecutando {algoritmo.upper()} {i+2:>2}: ", end="")
      s = s_best.copy()
      self.mutar(s, v)
      s, data = local.ejecutar_algoritmo(max_evals=max_evals/num_ejecuciones, sol_inicial=s)
      self.evals += data['evals']
      if data['f'] < f_best:
        s_best = s
        f_best = data['f']
    print("")

    info = {
      "evals" :         self.evals,
      "dg" :            self.dg(s_best),
      "infeasibility" : self.infeasibility(s_best),
      "f" :             f_best
    }
    return s_best, info
