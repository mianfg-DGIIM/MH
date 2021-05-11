from .par import PAR

import random
import numpy as np

class Genetico(PAR):

  def seleccionar(self, pob, fs, num_seleccionar):
    """
    Operador de selección: turno aleatorio.

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

  def cruzar(self, pob, p_cruce, v, cruce):
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
      hijo1 = cruce(pob[i], pob[i+1], v)
      hijo2 = cruce(pob[i], pob[i+1], v)
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
    for _ in range(int(p_mutacion*self.n*len(pob))): #WIP ceil?
      crom, gen = random.randrange(0, len(pob)), random.randrange(0, self.n)
      self.mutacion_uniforme(pob, crom, gen)

  def reemplazar(self, pob, pob_new, fs, solucion, elitismo):
    """
    Operador de reemplazo.
    
    Nota
    ----
    Necesita implementación en herencia.
    """
    pass

  def cruce_uniforme(self, padre_1, padre_2, v):
    # en caso de ser n impar, hay más de 1 que de 2
    random.shuffle(self.asignaciones)
    asignar = {1: padre_1, 2: padre_2}
    hijo = [asignar[self.asignaciones[i]][i] for i in range(self.n)]
    #      equivale a: [asignar[asignacion][i] for i, asignacion in enumerate(asignaciones)]
    self.reparar_solucion(hijo)
    return hijo
  
  def cruce_segmento_fijo(self, padre_1, padre_2, v):
    corte = random.randrange(0, self.n)
    hijo = [None]*self.n
    i = corte
    for _ in range(v):
      hijo[i%self.n] = padre_1[i%self.n]
      i += 1
    while not hijo[i%self.n]:
      hijo[i%self.n] = padre_1[i%self.n] if random.randint(1,2) == 1 else padre_2[i%self.n]
    self.reparar_solucion(hijo)
    return hijo

  def mutacion_uniforme(self, pob, crom, gen):
    cambio = random.randrange(0, self.k)
    # hacemos una reparación in-situ
    pob[crom][gen] = cambio
    while not self.es_solucion(pob[crom]):
      pob[crom][gen] = (pob[crom][gen]+1)%self.k

  def ejecutar_algoritmo(self, max_evals, tam_poblacion, tam_seleccion, p_cruce, p_mutacion, cruce, elitismo, v):
    if cruce == 'segmento_fijo':
      cruce = self.cruce_segmento_fijo
    elif cruce == 'uniforme':
      cruce = self.cruce_uniforme
    else:
      return None
    
    t = 0
    self.evals = 0
    self.max_evals = max_evals
    progress = []
    # inicializar P(t)
    pob = []
    for _ in range(tam_poblacion):
      pob.append(self.generar_solucion())
    # evaluar P(t)
    #print("pob inicial: ", pob)
    fs = [self.f(ind) for ind in pob]
    # guardamos el mejor individuo de P(t)
    i_min = np.argmin(fs)
    solucion = pob[i_min].copy()
    f_solucion = fs[i_min]

    

    while self.evals <= self.max_evals:
      progress.append((t, f_solucion))
      t += 1
      pob_new = self.seleccionar(pob, fs, tam_seleccion)
      self.cruzar(pob_new, p_cruce, v, cruce)
      self.mutar(pob_new, p_mutacion)
      pob = self.reemplazar(pob, pob_new, fs, solucion, elitismo)
      fs = [self.f(ind) for ind in pob]

      # tomamos la mejor solución y la reemplazamos en caso de ser
      # mejor de la que ya tenemos
      best_solucion = pob[np.argmin(fs)].copy()
      f_best_solucion = self.f(best_solucion)
      if f_best_solucion < f_solucion:
        #WIP incrementar evals en 2?
        solucion = best_solucion
        f_solucion = f_best_solucion

    info = {
      "progress" :      progress,
      "evals" :         self.evals,
      "generations" :   t,
      "dg" :            self.dg(solucion),
      "infeasibility" : self.infeasibility(solucion),
      "f" :             f_solucion
    }
    return solucion, info

  def __init__(self, archivo_datos, archivo_restrs, k):
    """
    Inicializador de clase

    Parámetros
    ----------
    archivo_datos : string
      Ruta al archivo de datos. Puede ser relativa.
    archivo_restrs : string
      Ruta al archivo de restricciones. Puede ser relativa.
    k : int
      Número de clusters.
    max_evals : int
      Número máximo de evaluaciones (para parada).
    tam_poblacion : int
      Tamaño de población.
    p_cruce : float
        Probabilidad de cruce.
    p_mutacion : float
      Probabilidad de mutación.
    elitismo : bool
      True si hay elitismo, False en otro caso.
    """
    PAR.__init__(self, archivo_datos, archivo_restrs, k)
    self.asignaciones = [1]*(self.n-int(self.n/2)) + [2]*(int(self.n/2))  # para cruce uniforme


class AGG(Genetico):
  def reemplazar(self, pob, pob_new, fs, solucion, elitismo):
    if elitismo:
      pob_new[-1] = solucion.copy()
    return pob_new

  def __init__(self, archivo_datos, archivo_restrs, k):
    Genetico.__init__(self, archivo_datos, archivo_restrs, k)
  
  def ejecutar_algoritmo(self, max_evals, tam_poblacion, p_cruce, p_mutacion, cruce, elitismo, v):
    if p_mutacion < 0: p_mutacion = 1/self.n
    return Genetico.ejecutar_algoritmo(self, max_evals, tam_poblacion, tam_poblacion, p_cruce, p_mutacion, cruce, elitismo, v)


class AGE(Genetico):
  def reemplazar(self, pob, pob_new, fs, solucion, elitismo):
    # reemplazamos el peor de pob con el mejor de pob_new
    # fs contiene los valores de pob
    # wip copy?
    pob[np.argmax(fs)] = pob_new[np.argmin([self.f(ind) for ind in pob_new])].copy()

  def __init__(self, archivo_datos, archivo_restrs, k):
    Genetico.__init__(self, archivo_datos, archivo_restrs, k)

  def ejecutar_algoritmo(self, max_evals, tam_poblacion, p_mutacion, cruce, v):
    if p_mutacion < 0: p_mutacion = 1/(self.n*2)
    return Genetico.ejecutar_algoritmo(self, max_evals, tam_poblacion, 2, 1, p_mutacion, cruce, None, v)
