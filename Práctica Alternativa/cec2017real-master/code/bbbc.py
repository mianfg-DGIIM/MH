import wrappers.cec17 as cec17
import solis
import random, numpy.random

def min(v):
  i_min = 0
  f_min = v[i_min]
  for i in range(len(v)):
    if v[i] < f_min:
      i_min = i
      f_min = v[i]
  return i_min


class BBBC:
  evals = 0
  
  def __init__(self, N, dim, alpha=0.75):
    self.N = N
    self.dim = dim
    self.alpha = alpha
    self.max_evals = 10000*self.dim

  def fitness(self, sol):
    self.evals += 1
    return cec17.fitness(sol, self.dim)

  def generar_candidatos(self):
    cand = []
    for _ in range(self.N):
      sol = []
      for _ in range(self.dim):
        sol.append(random.randrange(-100, 100))
      cand.append(sol)
    return cand

  def generar_candidatos_centroide(self, c):
    cand = []
    for _ in range(self.N):
      c_new = c.copy()
      for i in range(self.dim):
        c_new[i] += self.alpha*200*random.uniform(-1,1)/self.evals
      cand.append(c_new)
    return cand

  def fitnesses(self, cand):
    return [self.fitness(sol) for sol in cand]
  
  def centro_masa(self, cand, fit):
    f_sum = sum([1/f for f in fit])
    c = [0]*self.dim
    for i in range(self.N):
      for j in range(self.dim):
        c[j] += cand[i][j]/fit[i]/f_sum
    #print("centromasa:", c)
    return c

  def best_solucion(self, cand, fit):
    m = min(fit)
    return cand[m].copy(), fit[m]
  
  def busqueda_local(self, sol, f, max_evals=1000, delta=0.2):
    function = lambda sol: cec17.fitness(sol, self.dim)
    result, _ = solis.soliswets(function, sol, f, -100, 100, max_evals, delta)
    self.evals += result.evaluations
    return result.solution, result.fitness

  def ejecutar_algoritmo(self, funcid, memetic=False):
    self.evals = 0
    cec17.init("BB-BC"+("-Mem" if memetic else ""), funcid, self.dim)
    cand = self.generar_candidatos()
    fit = self.fitnesses(cand)
    sol_best, f_best = self.best_solucion(cand, fit)
    while self.evals < self.max_evals:
      c = sol_best.copy() #self.centro_masa(cand, fit)
      if memetic: c, _ = self.busqueda_local(c, self.fitness(c))
      cand = self.generar_candidatos_centroide(c)
      fit = self.fitnesses(cand)
      sol_best_new, f_best_new = self.best_solucion(cand, fit)
      if f_best_new < f_best:
        sol_best = sol_best_new
        f_best = f_best_new
    print(f"Fitness[F {funcid}]={cec17.error(f_best)}")
  
  def ejecutar_algoritmo_local(self, funcid):
    self.evals = 0
    cec17.init("Solis-Wets", funcid, self.dim)
    sol = []
    for _ in range(self.dim):
      sol.append(random.randrange(-100, 100))
    r, f = self.busqueda_local(sol, self.fitness(sol), self.max_evals)
    print(f"Fitness[F {funcid}]={cec17.error(f)}")


if __name__ == '__main__':
  dims = [10, 30, 50]
  for dim in dims:
    bbbc = BBBC(N=50, dim=dim)
    for i in range(3):
      random.seed(100)
      numpy.random.seed(100)
      for j in range(30):
        if i == 0:
          bbbc.ejecutar_algoritmo(j+1, memetic=False)
        if i == 1:
          bbbc.ejecutar_algoritmo(j+1, memetic=True)
        if i == 2:
          bbbc.ejecutar_algoritmo_local(j+1)
