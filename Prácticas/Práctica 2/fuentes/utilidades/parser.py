import argparse
from utilidades.vars import descripcion, algoritmos, semilla_default

parser_alg = argparse.ArgumentParser(description=descripcion, formatter_class=argparse.RawTextHelpFormatter, add_help=False)
group_alg = parser_alg.add_argument_group('algorithm-specific')
group_alg.add_argument('-me', '--max-evals', help="Número máximo de evaluaciones hasta parar.\nAplicable para: agg, age", type=int, default=100000)
group_alg.add_argument('-t', '--tam-poblacion', help="Tamaño de población para algoritmos genéticos.\nAplicable para: agg, age", type=int, default=50)
group_alg.add_argument('-pc', '--p-cruce', help="Probabilidad de cruce para algoritmos genéticos.\nAplicable para: agg, age", type=float, default=0.7)
group_alg.add_argument('-pm', '--p-mutacion', help="Probabilidad de mutación para algoritmos genéticos.\nAplicable para: agg, age", type=float, default=-1)
group_alg.add_argument('-fc', '--funcion-cruce', help="""\
Función de cruce para algoritmos genéticos. Elegir entre:
    uniforme : Operador de cruce uniforme
    segmento_fijo : Operador de cruce por segmento fijo
Aplicable para: agg, age (default: uniforme)
""", choices=['uniforme', 'segmento_fijo'], default="uniforme")
group_alg.add_argument('-ne', '--no-elitismo', help="Especificar no elitismo en algoritmos genéticos (por defecto se usa elitismo).\nAplicable para: agg",
action="store_true")
group_alg.add_argument('-v', help="Tamaño de segmento en operador de cruce por segmento fijo.\nAplicable para: agg, age (default: 3)", default=3) #WIP default

parser = argparse.ArgumentParser(description=descripcion, formatter_class=argparse.RawTextHelpFormatter,
  parents=[parser_alg],
  usage="main.py [-h] -N NOMBRE_SET -P PORC_RESTRICCIONES -A ALGORITMO [-R NUM_REPETICIONES] [-S SEMILLA] ...")
parser.add_argument('-N', '--nombre-set', help="Nombre del set de datos. Ej.: bupa, glass, zoo", required=True)
parser.add_argument('-P', '--porc-restricciones', help="Porcentaje de restricciones. Ej.: 10, 20", type=int, required=True)
parser.add_argument('-A', '--algoritmo', help="""\
Algoritmo a ejecutar. Puede ser uno de los siguientes:
""" + "".join([f"""\
  {algoritmo} : {algoritmos[algoritmo]}
""" for algoritmo in algoritmos.keys()]), choices=algoritmos.keys(), metavar='ALGORITMO', required=True) #wip
parser.add_argument('-R', '--num-repeticiones', help="Número de repeticiones (default: 1)", type=int, default=1)
parser.add_argument('-S', '--semilla', help=f"Semilla para generador aleatorio (default: {semilla_default})", type=int, default=semilla_default)
parser.add_argument('-C', '--csv', help="Guardar resultados en CSV", action="store_true")
parser.add_argument('-CF', '--csv-file', help="Ruta a donde se guardará el archivo CSV (default: \"./output.csv\"", default="./output.csv")

args = parser.parse_args()