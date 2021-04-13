#include <iostream>
#include <string>

#include "par.h"

using namespace std;

int main() {
  /*Restriccion r;
  r.restr = -1;
  cout << r.restr << endl;*/
  cout << "Importando..." << endl;
  PAR p("./datos/zoo_set.dat", "./datos/zoo_set_const_10.const", 7, 5);
  //PAR p;
  
  /*auto inds = p.shuffleIndices();
  for ( auto ind : inds )
    cout << ind << " ";*/

  /*cout << "CONSTRUCTOR 1" << endl;
  auto part = p.generaCentroidesIniciales();
  part.printMe();
  cout << "CONSTRUCTOR 2" << endl;
  auto part2 = Particion(part);
  part2._clusters[2] = 0;
  part2._centroides[2][0] = -10000;
  part2.printMe();
  cout << "CONSTRUCTOR 1" << endl;
  part.printMe();*/

  //p.restartVecinoVirtual();
  Particion part = p.busquedaLocal(10000);
  //part.printMe();
}
