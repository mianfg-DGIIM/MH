from par_greedy import Greedy
from par_bl import BusquedaLocal

import random, time, sys, os
import numpy as np

semilla_fija = 1514280522468089

if (len(sys.argv) < 4):
  print("Error en parámetros. Debe insertar:\n")
  print("\tnombre_set porc_restricciones algoritmo [num_repeticiones] [semilla]")
  print("\t\tnombre_set: nombre de set de datos. Ej.: bupa, glass, zoo")
  print("\t\tporc_restricciones: porcentaje de restricciones. Ej.: 10, 20")
  print("\t\talgoritmo: algoritmo a ejecutar. Puede ser uno de los siguientes:")
  print("\t\t\tgreedy --> algoritmo greedy COPKMN")
  print("\t\t\tbl --> algoritmo de búsqueda local")
  print("\t\tnum_repeticiones: número de repeticiones. Opcional, por defecto: 1")
  print("\t\tsemilla: semilla para generador aleatorio. Opcional, fijada por defecto")
  exit()
else:
  nombre_set = sys.argv[1]
  porc_restricciones = int(sys.argv[2])
  algoritmo = sys.argv[3]
  num_repeticiones = int(sys.argv[4]) if len(sys.argv) >= 5 else 1
  semilla = int(sys.argv[5]) if len(sys.argv) >= 6 else semilla_fija

algoritmos_verbose = {'greedy': "Greedy COPKMN", 'bl': "Búsqueda local"}
if algoritmo not in algoritmos_verbose.keys():
  print(f"[ERROR] Algoritmo \"{algoritmo}\" no implementado")
num_clusters_map = {'bupa': 16, 'glass': 7, 'zoo': 7}
if nombre_set in num_clusters_map.keys():
  num_clusters = num_clusters_map[nombre_set]
else:
  print(f"[ERROR] El set {nombre_set} no está disponible")
  exit()

print("Set seleccionado:   ", nombre_set)
print("Porcentaje restrs.: ", porc_restricciones)
print("Algoritmo:          ", algoritmos_verbose[algoritmo])
print("Número repeticiones:", num_repeticiones)
print("Semilla:            ", semilla)
print("")

dirname = os.path.dirname(__file__)
filename_datos = os.path.join(dirname, f'../bin/datos/{nombre_set}_set.dat')
filename_restrs = os.path.join(dirname, f'../bin/datos/{nombre_set}_set_const_{porc_restricciones}.const')

args = {}
if algoritmo == 'greedy':
  p = Greedy(filename_datos, filename_restrs, num_clusters)
if algoritmo == 'bl':
  args['max_iters'] = 10000
  p = BusquedaLocal(filename_datos, filename_restrs, num_clusters)

print("Datos cargados:")
print(p)

tiempos = []
for i in range(num_repeticiones):
  random.seed(semilla)
  print(f"REPETICIÓN i={i}")
  t_0 = time.time_ns() / (10 ** 9)
  s = p.ejecutar_algoritmo(**args)
  t_1 = time.time_ns() / (10 ** 9)
  print("Solución obtenida:", s)
  tiempos.append(t_1-t_0)
  p.reset()
  print(f"------ Tiempo empleado: {tiempos[-1]} s\n")
  time.sleep(0.5)

print(f"REPETICIONES FINALIZADAS")
print(f"------ Tiempo medio empleado: {np.average(tiempos)} s")
