import csv, os

keys = {'set': 'Set datos', 'pr': 'Porcentaje restrs.', 'algoritmo': 'Algoritmo', 'reps': 'Num. repeticiones', 'rep': 'Repetición',
  'semilla': 'Semilla', 'sol': 'Solución obtenida', 'time': 'Tiempo',
  'evals': 'Num. evaluaciones', 'dg': 'Desv. general', 'infeasibility': 'Infeasibility',
  'f': 'Func. objetivo', 'time': 'Tiempo empleado', 'generations': 'Num. generaciones',
}

def append_info(data, info):
  for k in data.keys():
    data[k].append(info[k])

def print_info(info_dict):
  for k in info_dict.keys():
    if k in keys.keys():
      print(f"\t{keys[k]:<20} : {info_dict[k]}")

def csv_all(infos, csv_file):
  with open(csv_file, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys.keys(), extrasaction='ignore')
    writer.writeheader()
    for info in infos:
        writer.writerow(info)

def csv_individual(infos, csv_file):
  f, e = os.path.splitext(csv_file)
  for i, info in enumerate(infos):
    with open(f+f'-rep_{i}'+e, 'w') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=info.keys())
      writer.writeheader()
      writer.writerow(info)
