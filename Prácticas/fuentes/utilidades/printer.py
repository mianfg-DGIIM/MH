import csv, os, json

keys = {'set': 'Set datos', 'pr': 'Porcentaje restrs.', 'algoritmo': 'Algoritmo', 'reps': 'Num. repeticiones', 'rep': 'Repetición',
  'semilla': 'Semilla', 'sol': 'Solución obtenida', 'time': 'Tiempo',
  'evals': 'Num. evaluaciones', 'dg': 'Desv. general', 'infeasibility': 'Infeasibility',
  'f': 'Fitness', 'time': 'Tiempo empleado', 'generations': 'Num. generaciones',
}

def append_info(data, info):
  for k in data.keys():
    data[k].append(info[k])

def print_info(info_dict):
  for k in info_dict.keys():
    if k in keys.keys():
      print(f"\t{keys[k]:<20} : {info_dict[k]}")

def csv_all(infos, csv_file):
  with open(csv_file, 'a') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[k for k in keys.keys() if k != 'sol'], extrasaction='ignore')
    writer.writeheader()
    for info in infos:
        writer.writerow(info)

def json_all(infos, csv_file):
  f, _ = os.path.splitext(csv_file)
  with open(f+'.json', 'a') as jsonfile:
    json.dump(infos, jsonfile)