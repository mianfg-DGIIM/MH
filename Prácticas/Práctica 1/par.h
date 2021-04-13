#ifndef __PAR_H
#define __PAR_H

#include <vector>
#include <set>
#include <string>
#include <math.h>
#include <fstream>
#include "random/random.h"
#include <iostream>

#include <iterator> // needed for std::ostram_iterator

template <typename T>
std::ostream& operator<< (std::ostream& out, const std::vector<T>& v) {
  if ( !v.empty() ) {
    out << '[';
    std::copy (v.begin(), v.end(), std::ostream_iterator<T>(out, ", "));
    out << "\b\b]";
  }
  return out;
}

using namespace std;
using Dato = vector<double>;
using Vecino = pair<unsigned, int>;

struct Restriccion {
  pair<unsigned, unsigned> indices;
  short tipo; // -1 CL, 1 ML
};

double distancia_euclidea(Dato d1, Dato d2);
Dato media(const vector<Dato> &datos);
vector<unsigned> getMinIndices(const vector<int> &v);
vector<unsigned> randomVector(unsigned n);

class Particion {
private:
  const vector<Dato> &_datos;   // puntero a los datos
  unsigned _n_clusters;
public:
  vector<int> _clusters;       // índice de cluster por dato
  vector<Dato> _centroides;    // centroides

  Particion(const vector<Dato> &datos, vector<Dato> &centroides)
    : _datos(datos)
    , _n_clusters(centroides.size())
    , _clusters(vector<int>(datos.size(), -1))
    , _centroides(std::move(_centroides)) {};
  Particion(const vector<Dato> &datos, vector<int> &clusters)
    : _datos(datos)
    , _n_clusters(datos.size())
    , _clusters(std::move(clusters))
    , _centroides(vector<Dato>(_datos.size(), Dato())) {};
  Particion(const vector<Dato> &datos, vector<int> &clusters, vector<Dato> &centroides)
    : _datos(datos)
    , _n_clusters(centroides.size())
    , _clusters(std::move(clusters))
    , _centroides(std::move(centroides)) {};
  Particion(const Particion &part)
    : _datos(part._datos)
    , _n_clusters(part._n_clusters)
    , _clusters(vector<int>(part._clusters))
    , _centroides(vector<Dato>(part._centroides)) {};
  ~Particion();

  unsigned getSize() const;
  unsigned getDimension() const;
  vector<Dato> getCluster(unsigned ind_cluster) const;
  vector<unsigned> getClusterIndices(unsigned ind_cluster) const; // índices de datos del clúster
  Dato centroide(unsigned ind_cluster) const;
  void actualizarCentroides();
  double dmic(unsigned ind_cluster) const;
  unsigned h(unsigned ind_dato) const; // devuelve índice del cluster al que pertenece el dato con índice ind_dato
  Particion apply(const Vecino &vecino) const;

  double dgp() const;    // desviación general de la partición
  bool esValida() const; // devuelve si la partición es válida

  void fixMe();

  void printClusters();
  void printCentroides();
  void printMe();
};

class PAR {
private:
  unsigned _n_clusters;                   // número de clusters
  vector<Dato> _datos;                    // vector de datos
  vector<vector<short>> _restr_mat;       // restricciones (en matriz)
  vector<Restriccion> _restr_list;        // restricciones (en lista)
  vector<vector<double>> _dists;          // distancias
  pair<unsigned, unsigned> _most_distant; // par de datos más distantes
  double _max_dist;                       // distancia máxima entre datos
  double _lambda;                         // lambda

  vector<Vecino> _orden_expl_vecinos;     // orden en el que se exploran vecinos
  int _expl_vecino_next;                  // -1 si ha acabado exploración

public:
  PAR(const string &archivo_datos, const string &archivo_restricciones, int n_clusters, unsigned long semilla);

  unsigned getSize() const;
  unsigned getDimension() const;
  double getDistancia(unsigned i, unsigned j);
  bool v(const Particion &part, unsigned i, unsigned j) const; // true si viola restricción
  double f(const Particion &part) const; // función objetivo
  int infeasibility(const Particion &part) const;
  // infeasibility total de una partición
  int incr_infeasibility(Particion part, unsigned i, unsigned j) const;
  // incremento de infeasibility de asignar x_i a c_j
  vector<unsigned> shuffleIndices() const;
  Particion generaCentroidesIniciales() const;
  Particion generaClustersIniciales() const;
  void restartVecinoVirtual();
  Vecino * nextVecinoVirtual(const Particion &part);

  Particion busquedaGreedy() const;
  Particion busquedaLocal(unsigned max_iters);
};

#endif