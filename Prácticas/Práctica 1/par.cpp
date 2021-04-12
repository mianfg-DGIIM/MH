#include "par.h"
#include <iostream>
#include <sstream>

double distancia_euclidea(Dato d1, Dato d2) {
  double suma = 0;
  for ( int i = 0; i < d1.size(); i++ ) {
    suma += (d1[i] - d2[i])*(d1[i] - d2[i]);
  }
  return sqrt(suma);
}

Dato media(vector<Dato> datos) {
  Dato media(datos[0].size(), 0);
  for ( Dato dato : datos )
    for ( unsigned i = 0; i < media.size(); i++ )
      media[i] += dato[i];
  for ( unsigned i = 0; i < media.size(); i++ )
    media[i] /= datos.size();
  
  return media;
}

Particion::Particion(unsigned &n_clusters, vector<Dato> &datos, vector<unsigned> &cluster) {
  n_clusters = *&n_clusters;
  datos = *&datos;
  cluster = *&cluster;
}

vector<Dato> Particion::getCluster(unsigned ind_cluster) {
  vector<Dato> _cluster;

  for ( unsigned i = 0; i < cluster->size(); i++ )
    if ( cluster->at(i) == ind_cluster )
      _cluster.push_back(datos->at(i));
  
  return _cluster;
}

vector<unsigned> Particion::getClusterIndices(unsigned ind_cluster) {
  //assert(ind_cluster >= n_clusters);

  vector<unsigned> _cluster;

  for ( unsigned i = 0; i < cluster->size(); i++ )
    if ( cluster->at(i) == ind_cluster )
      _cluster.push_back(i);
  
  return _cluster;
}

Dato Particion::centroide(unsigned ind_cluster) {
  return media(getCluster(ind_cluster));
}

double Particion::dmic(unsigned ind_cluster) {
  double _dmic = 0;
  vector<Dato> cluster = getCluster(ind_cluster);

  for ( Dato dato : cluster )
    _dmic += distancia_euclidea(dato, centroide(ind_cluster));
  
  return _dmic/cluster.size();
}

double Particion::dgp() {
  double _dgp = 0;

  for ( unsigned i = 1; i <= *n_clusters; i++ )
    _dgp += dmic(i);
  
  return _dgp / *n_clusters;
}

bool Particion::esValida() {
  for ( unsigned i = 1; i <= *n_clusters; i++ ) {
    for ( unsigned j = 0; j < cluster->size(); j++ ) {
      if ( cluster->at(j) == i ) break;
      return false;
    }
  }

  return true;
}


PAR::PAR(const string &archivo_datos, const string &archivo_restricciones, int n_clusters, string semilla) {
  ifstream archivo;
  double read_double; char read_char; short read_int;
  string str;
  
  archivo.open(archivo_datos);
  Dato dato;
  while (getline(archivo, str)) {
    stringstream ss(str);

    while(ss.good()) {
      string substr;
      getline(ss, substr, ',');
      dato.push_back(stod(substr));
    }

    datos.push_back(dato);
    dato.clear();
  }

  archivo.close();
  archivo.clear();

  archivo.open(archivo_restricciones);
  vector<short> row;
  while (getline(archivo, str)) {
    stringstream ss(str);

    while(ss.good()) {
      string substr;
      getline(ss, substr, ',');
      row.push_back(stoi(substr));
    }

    restr_mat.push_back(row);
    row.clear();
  }

  Restriccion restr;
  for ( unsigned i = 0; i < restr_mat.size(); i++ ) {
    for ( unsigned j = i; j < restr_mat[i].size(); j++ ) {
      restr.datos = make_pair(i, j);
      restr.restr = restr_mat[i][j];
      restr_list.push_back(restr);
    }
  }

  Set_random(semilla);
}
