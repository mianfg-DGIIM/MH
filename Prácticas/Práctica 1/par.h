#ifndef __PAR_H
#define __PAR_H

#include <vector>
#include <utility>
#include <fstream>
#include "random/random.h"
#include <string>
#include <math.h>

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
  short tipo;   // -1 CL, 1 ML
};

double dist(const Dato &d1, const Dato &d2);
Dato media(const vector<Dato> &datos);
vector<unsigned> getMinIndices(const vector<int> &v);
vector<unsigned> vectorAleatorio(unsigned n);

class Particion {
private:
  const vector<Dato> &_datos;   // referencia a los datos
  unsigned _n_clusters;         // número de clusters
public:
  vector<int> _clusters;        // vector de índices de clusters (-1: no asignado)
  vector<Dato> _centroides;     // vector de centroides (uno por cada cluster)

  Particion(const vector<Dato> &datos, vector<Dato> &centroides)
    : _datos(datos)
    , _n_clusters(centroides.size())
    , _clusters(vector<int>(datos.size(), -1))
    , _centroides(std::move(centroides)) {};
  Particion(const vector<Dato> &datos, vector<int> &clusters, unsigned n_clusters)
    : _datos(datos)
    , _n_clusters(n_clusters)
    , _clusters(clusters)
    , _centroides() {};   // WIP review
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
  
  unsigned getSize() const { return _datos.size(); }
  unsigned getDim() const { return _datos.at(0).size(); }
  vector<Dato> getClusterDatos(unsigned id_cluster) const;
  vector<unsigned> getClusterIndices(unsigned id_cluster) const;
  Dato calcularCentroide(unsigned id_cluster) const;
  void actualizarCentroides();
  Particion aplicarVecino(const Vecino &vecino) const;

  double dmic(unsigned id_cluster) const;
  unsigned h(unsigned ind_dato) const;
  double dgp() const;
  bool esValida() const;

  void printClusters() const;
  void printCentroides() const;
};

class PAR {
private:
  vector<Dato> _datos;                  // vector de datos (n datos)
  unsigned _n_clusters;                 // número de clusters (k)
  vector<vector<short> > _restr_mat;    // restricciones (en matriz)
  vector<Restriccion> _restr_list;      // restricciones (en lista, únicamente si tipo!=0)
  vector<vector<double> > _dists;       // distancias
  double _max_dist;                     // distancia máxima entre datos
  double _lambda;                       // lambda

  vector<Vecino> _orden_expl_vecinos;     // orden en el que se exploran vecinos
  int _expl_vecino_next;                  // -1 si ha acabado exploración
public:
  PAR(const string &archivo_datos, const string &archivo_restricciones, int n_clusters, unsigned long semilla);

  unsigned getSize() const { return _datos.size(); }
  unsigned getDim() const { return _datos.at(0).size(); }
  double getDist(unsigned i, unsigned j) const { return _dists[i][j]; }
  bool v(const Particion &part, unsigned i, unsigned j) const;
  int infeasibility(const Particion &part) const;
  int incr_infeasibility(const Particion &part, unsigned i, unsigned j) const;
  vector<unsigned> shuffleIndices() const;
  Particion generaCentroidesIniciales() const;
  Particion generaClustersIniciales() const;
  void restartVecinoVirtual();
  Vecino nextVecinoVirtual(const Particion &part);

  Particion busquedaGreedy() const;
  Particion busquedaLocal(unsigned max_iters);

  void printMe() const;
};

#endif
