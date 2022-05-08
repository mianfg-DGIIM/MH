import algoritmos
from utilidades import parser, printer, vars

import random, time, sys, os
import numpy as np

print(vars.descripcion)
print()

# imprimir opciones
run_info = {
  'set'       : parser.args.nombre_set,
  'pr'        : parser.args.porc_restricciones,
  'algoritmo' : vars.algoritmos[parser.args.algoritmo],
  'reps'      : parser.args.num_repeticiones,
  'semilla'   : parser.args.semilla
}
printer.print_info(run_info)
if parser.args.csv:
  print(f"Se imprimirán resultados en {parser.args.csv_file}")
print()

dirname = os.path.dirname(__file__)
filename_datos = os.path.join(dirname, f'../bin/datos/{parser.args.nombre_set}_set.dat')
filename_restrs = os.path.join(dirname, f'../bin/datos/{parser.args.nombre_set}_set_const_{parser.args.porc_restricciones}.const')

args = {
  'archivo_datos': os.path.join(dirname, f'../bin/datos/{parser.args.nombre_set}_set.dat'),
  'archivo_restrs': os.path.join(dirname, f'../bin/datos/{parser.args.nombre_set}_set_const_{parser.args.porc_restricciones}.const'),
  'k': vars.num_clusters_map[parser.args.nombre_set]
}
args_ej = {}
if parser.args.algoritmo == 'bl':
  p = algoritmos.BL(**args)
  args_ej['max_evals'] = parser.args.max_evals
if parser.args.algoritmo == 'agg':
  p = algoritmos.AGG(**args)
  args_ej['max_evals'] = parser.args.max_evals
  args_ej['tam_poblacion'] = parser.args.tam_poblacion
  args_ej['p_cruce'] = parser.args.p_cruce
  args_ej['p_mutacion'] = parser.args.p_mutacion
  args_ej['cruce'] = parser.args.funcion_cruce
  args_ej['elitismo'] = not parser.args.no_elitismo
if parser.args.algoritmo == 'age':
  p = algoritmos.AGE(**args)
  args_ej['max_evals'] = parser.args.max_evals
  args_ej['tam_poblacion'] = parser.args.tam_poblacion
  args_ej['p_mutacion'] = parser.args.p_mutacion
  args_ej['cruce'] = parser.args.funcion_cruce
if parser.args.algoritmo == 'am':
  p = algoritmos.AM(**args)
  args_ej['max_evals'] = parser.args.max_evals
  args_ej['tam_poblacion'] = parser.args.tam_poblacion
  args_ej['p_cruce'] = parser.args.p_cruce
  args_ej['p_mutacion'] = parser.args.p_mutacion
  args_ej['cruce'] = parser.args.funcion_cruce
  args_ej['elitismo'] = not parser.args.no_elitismo
  args_ej['gens_ls'] = parser.args.gens_ls
  args_ej['p_ls'] = parser.args.p_ls
  args_ej['mej_ls'] = parser.args.mej_ls
  args_ej['lim_fallos_ls'] = parser.args.lim_fallos_ls
if parser.args.algoritmo == 'es':
  p = algoritmos.ES(**args)
  args_ej['max_evals'] = parser.args.max_evals
  args_ej['max_vecinos'] = parser.args.max_vecinos
  args_ej['max_exitos'] = parser.args.max_exitos
if parser.args.algoritmo == 'bmb':
  p = algoritmos.BMB(**args)
  args_ej['max_evals'] = parser.args.max_evals
  args_ej['num_ejecuciones'] = parser.args.num_ejecuciones
if parser.args.algoritmo == 'ils':
  p = algoritmos.ILS(**args)
  args_ej['max_evals'] = parser.args.max_evals
  args_ej['num_ejecuciones'] = parser.args.num_ejecuciones
  args_ej['v'] = parser.args.v
  args_ej['algoritmo'] = parser.args.algoritmo_ils

print("Datos cargados. Ejecutando algoritmo...\n")

random.seed(parser.args.semilla)

infos = []
for i in range(parser.args.num_repeticiones):
  print(f"\nRepetición {i+1:>2}:", end=' ')
  run_info['rep'] = i+1
  t_0 = time.time_ns() / (10 ** 9)
  sol, info = p.ejecutar_algoritmo(**args_ej)
  t_1 = time.time_ns() / (10 ** 9)
  print()
  info['sol'] = sol
  info['time'] = t_1-t_0
  printer.print_info(info)
  infos.append(dict(run_info, **info))
  time.sleep(0.5)

if parser.args.csv:
  printer.csv_all(infos, parser.args.csv_file)
  #printer.json_all(infos, parser.args.csv_file)

print(f"\nREPETICIONES FINALIZADAS :)")
