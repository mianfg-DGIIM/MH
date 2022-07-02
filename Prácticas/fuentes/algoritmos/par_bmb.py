from .par import PAR
from .par_bl import BL

import random, math
import numpy as np


class BMB(PAR):
  def __init__(self, archivo_datos, archivo_restrs, k):
    PAR.__init__(self, archivo_datos, archivo_restrs, k)
    self.bl = BL(archivo_datos, archivo_restrs, k)

  def ejecutar_algoritmo(self, max_evals, num_ejecuciones):
    self.max_evals = max_evals
    self.evals = 0

    print("\n\tEjecutando arranque  1: ", end="")
    s_best, data = self.bl.ejecutar_algoritmo(max_evals=max_evals/num_ejecuciones)
    f_best = data['f']
    self.evals += data['evals']
    
    for i in range(num_ejecuciones-1):
      print(f"\n\tEjecutando arranque {i+2:>2}: ", end="")
      s, data = self.bl.ejecutar_algoritmo(max_evals=max_evals/num_ejecuciones)
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
