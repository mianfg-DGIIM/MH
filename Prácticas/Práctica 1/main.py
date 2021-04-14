from par_greedy import Greedy
from par_bl import BusquedaLocal

import random, time

seed = 457958018911888190
random.seed(seed)

#greedy = Greedy('./datos/zoo_set.dat', './datos/zoo_set_const_10.const', 7)
#print(greedy)
#print(greedy.ejecutar_algoritmo())
#busqueda_local = BusquedaLocal('./datos/zoo_set.dat', './datos/zoo_set_const_10.const', 7)
#print(busqueda_local)
#print(busqueda_local.ejecutar_algoritmo(10000))


"""
import cProfile
busqueda_local = BusquedaLocal('./datos/zoo_set.dat', './datos/zoo_set_const_10.const', 7)
i_time = time.time_ns() / (10 ** 9)
print(busqueda_local.ejecutar_algoritmo(10000))
f_time = time.time_ns() / (10 ** 9)
print('\nElapsed Time: ' + str(f_time - i_time))
#cProfile.run('busqueda_local.ejecutar_algoritmo(10000)')
"""
import cProfile
greedy = Greedy('./datos/glass_set.dat', './datos/glass_set_const_10.const', 7)
cProfile.run('greedy.ejecutar_algoritmo()')
#i_time = time.time_ns() / (10 ** 9)
#print(greedy.ejecutar_algoritmo())
#f_time = time.time_ns() / (10 ** 9)
#print('\nElapsed Time: ' + str(f_time - i_time))
