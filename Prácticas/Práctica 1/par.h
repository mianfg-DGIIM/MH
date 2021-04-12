#ifndef __PAR_H
#define __PAR_H

#include <vector>
#include <set>
#include <string>
#include <math.h>
#include <fstream>
#include "random/random.h"

using namespace std;
using Dato = vector<double>;

struct Restriccion {
  pair<unsigned, unsigned> datos;
  short restr;
};

double distancia_euclidea(Dato d1, Dato d2);
Dato media(vector<Dato> datos);

class Cluster {
  public:
    vector<unsigned> indices;
    string nombre;

    Cluster(set<Dato> contenidos, string nombre);
    Dato centroide();
    double dmic();    // distancia media intra-cluster
};

class Particion {
  public:
    unsigned * n_clusters;               // tamaño de la partición
    vector<Dato> * datos;                // datos
    vector<unsigned> * cluster;          // índice de cluster por dato

    vector<Dato> getCluster(unsigned ind_cluster);
    vector<unsigned> getClusterIndices(unsigned ind_cluster);  // índices de datos del clúster
    Dato centroide(unsigned ind_cluster);
    double dmic(unsigned ind_cluster);

    double dgp();     // desviación general de la partición
    bool esValida();  // devuelve si la partición es válida

    Particion(unsigned &tam, vector<Dato> &datos, vector<unsigned> &cluster);
};

class PAR {
  public:
    unsigned tam;           // número de clusters
    vector<Dato> datos;     // vector de datos
    vector<vector<short> > restr_mat;         // restricciones (en matriz)
    vector<Restriccion> restr_list; // restricciones (en lista)

  public:
    PAR(const string &archivo_datos, const string &archivo_restricciones, int n_clusters, unsigned long semilla);
    void busquedaGreedy() {};
    void busquedaLocal() {};

};

#endif