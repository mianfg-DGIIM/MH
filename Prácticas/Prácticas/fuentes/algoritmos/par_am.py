from .par import PAR, dist, min, avg

import random
import numpy as np


class AM(PAR):

  def seleccionar(self, pob, fs, num_seleccionar):
    """
    Operador de selección: torneo binario.

    Parámetros
    ----------
    pob : list
      Población de la que hacer selección.
    fs : list
      Valor de f sobre cada individuo de la población, en correspondencia
      uno a uno con pob.
    num_seleccionar : 
      Número de individuos a seleccionar.
    
    Returns
    -------
    padres : list
      Lista de los padres seleccionados.
    """
    padres = []
    for _ in range(num_seleccionar):
      ind1, ind2 = random.randrange(0, len(pob)), random.randrange(0, len(pob))
      padres.append(pob[ind1 if fs[ind1] < fs[ind2] else ind2].copy())
    return padres

  def cruzar(self, pob, p_cruce, cruce):
    """
    Operador de cruce.

    Parámetros
    ----------
    pob : list
      Población a la que someter al cruce. Será modificada.
    p_cruce : float
      Probabilidad de cruce.
    """
    # IMPORTANTE: asumimos que tam_poblacion SIEMPRE es par
    for i in range(0, int(p_cruce*len(pob)/2), 2):
      hijo1 = cruce(pob[i], pob[i+1])
      hijo2 = cruce(pob[i], pob[i+1])
      pob[i] = hijo1
      pob[i+1] = hijo2

  def mutar(self, pob, p_mutacion):
    """
    Operador de mutación.

    Parámetros
    ----------
    pob : list
      Población a la que someter a mutaciones. Será modificada.
    p_mutacion : float
      Probabilidad de mutación.
    """
    num_mut = p_mutacion*self.n*len(pob)
    if num_mut >= 1:
      for _ in range(int(num_mut)):
        crom, gen = random.randrange(0, len(pob)), random.randrange(0, self.n)
        self.mutacion_uniforme(pob, crom, gen)
    else: # 0 <= num_mut < 1
      if random.uniform(0, 1) < num_mut:
        crom, gen = random.randrange(0, len(pob)), random.randrange(0, self.n)
        self.mutacion_uniforme(pob, crom, gen)

  def reemplazar(self, pob, pob_new, fs, solucion, elitismo):
    """
    Operador de reemplazo.
    """
    if elitismo:
      pob_new[-1] = solucion.copy()
    return pob_new

  def cruce_uniforme(self, padre_1, padre_2):
    # en caso de ser n impar, hay más de 1 que de 2
    random.shuffle(self.asignaciones)
    asignar = {1: padre_1, 2: padre_2}
    hijo = [asignar[self.asignaciones[i]][i] for i in range(self.n)]
    #      equivale a: [asignar[asignacion][i] for i, asignacion in enumerate(asignaciones)]
    self.reparar_solucion(hijo)
    return hijo
  
  def cruce_segmento_fijo(self, padre_1, padre_2):
    v = random.randrange(0, self.n)
    corte = random.randrange(0, self.n)
    hijo = [None]*self.n
    i = corte
    for _ in range(v):
      hijo[i] = padre_1[i]
      i = (i+1)%self.n
    while not hijo[i]:
      hijo[i] = padre_1[i] if random.randint(1,2) == 1 else padre_2[i]
      i = (i+1)%self.n
    self.reparar_solucion(hijo)
    return hijo

  def mutacion_uniforme(self, pob, crom, gen):
    cambio = random.randrange(0, self.k)
    # hacemos una reparación in-situ
    pob[crom][gen] = cambio
    while not self.es_solucion(pob[crom]):
      pob[crom][gen] = (pob[crom][gen]+1)%self.k
  
  def local_boost(self, pob, gens, prob, mej, lim_fallos):
    if self.t % gens == 0:
      if mej:
        # seleccionamos los mejores tam_pob*prob cromosomas
        fs = [(i, self.f(ind)) for i, ind in enumerate(pob)]
        fs.sort(key=lambda tup: tup[1])
        seleccionar = [tup[0] for tup in fs[:int(len(pob)*prob)]]
      else:
        # seleccionamos aleatoriamente un subconjunto de tam_pob*prob cromosomas
        seleccionar = random.sample(range(0, len(pob)), int(len(pob)*prob))
      for i in seleccionar:
        self.soft_local_search(pob[i], lim_fallos)

  def soft_local_search(self, solucion, lim_fallos):
    random.shuffle(self.rsi)
    f_solucion = self.f(solucion)
    fallos = 0
    mejora = True
    i = 0
    while (mejora or fallos < lim_fallos) and i < self.n and self.evals <= self.max_evals:
      mejora = False
      # asignar la instancia rsi[i] al cluster que minimice f
      fs = [f_solucion+1]*self.k  # sólo queremos mejorar
      cc = self.contar_por_cluster(solucion)
      for j in range(self.k):
        if cc[j] > 1 and cc[solucion[self.rsi[i]]] > 1:
          solucion_aux = solucion.copy()
          solucion_aux[self.rsi[i]] = j
          fs[j] = self.f(solucion_aux)
      best_cluster = min(fs)
      if fs[best_cluster] < f_solucion:
        solucion[self.rsi[i]] = best_cluster
        f_solucion = fs[best_cluster]
        mejora = True
      else:
        fallos += 1
      i += 1

  def ejecutar_algoritmo(self, max_evals, tam_poblacion, p_cruce, p_mutacion, cruce, elitismo,
    gens_ls, p_ls, mej_ls, lim_fallos_ls):
    if p_mutacion < 0: p_mutacion = 0.1/self.n
    if lim_fallos_ls < 0: lim_fallos_ls = 0.1*self.n

    # especificamos qué algoritmo queremos ejecutar
    if cruce == 'sf':
      cruce = self.cruce_segmento_fijo
    elif cruce == 'un':
      cruce = self.cruce_uniforme
    else:
      return None
    
    self.t = 0
    self.evals = 0
    self.max_evals = max_evals
    progress = []

    # inicializar P(t)
    pob = []
    for _ in range(tam_poblacion):
      pob.append(self.generar_solucion())

    # evaluar P(t)
    fs = [self.f(ind) for ind in pob]

    # guardamos el mejor individuo de P(t)
    i_min = min(fs)
    solucion = pob[i_min].copy()
    f_solucion = fs[i_min]

    while self.evals <= self.max_evals:
      progress.append((self.t, self.evals, f_solucion))  # para gráfica del progreso del algoritmo
      self.t += 1
      pob_new = self.seleccionar(pob, fs, tam_poblacion)
      self.cruzar(pob_new, p_cruce, cruce)
      self.mutar(pob_new, p_mutacion)
      self.local_boost(pob_new, gens_ls, p_ls, mej_ls, lim_fallos_ls)
      pob = self.reemplazar(pob, pob_new, fs, solucion, elitismo)
      
      fs = [self.f(ind) for ind in pob]
      # tomamos la mejor solución y la reemplazamos en caso de ser
      # mejor de la que ya tenemos
      best_solucion = pob[min(fs)].copy()
      f_best_solucion = self.f(best_solucion)
      if f_best_solucion < f_solucion:
        solucion = best_solucion
        f_solucion = f_best_solucion

    info = {
      "progress" :      progress,
      "evals" :         self.evals,
      "generations" :   self.t,
      "dg" :            self.dg(solucion),
      "infeasibility" : self.infeasibility(solucion),
      "f" :             f_solucion
    }
    return solucion, info

  def __init__(self, archivo_datos, archivo_restrs, k):
    PAR.__init__(self, archivo_datos, archivo_restrs, k)
    self.asignaciones = [1]*(self.n-int(self.n/2)) + [2]*(int(self.n/2))  # para cruce uniforme
    self.rsi = list(range(0, self.n))
