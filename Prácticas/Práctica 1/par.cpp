#include "par.h"

#include <algorithm>
#include <iostream>
#include <sstream>

double dist(const Dato &d1, const Dato &d2) {
  double suma = 0;
  for ( unsigned i = 0; i < d1.size(); i++ )
    suma += (d1[i] - d2[i])*(d1[i] - d2[i]);
  return sqrt(suma);
}

Dato media(const vector<Dato> &datos) {
  if ( datos.size() > 0 ) {
    Dato media(datos[0].size(), 0);
    for ( Dato dato : datos )
      for ( unsigned i = 0; i < media.size(); i++ )
        media[i] += dato[i] / media.size();
    return media;
  } else {
    return Dato();
  }
}

vector<unsigned> getMinIndices(const vector<int> &v) {
  int min_value = *min_element(v.begin(), v.end());
  vector<unsigned> min_indices;
  for ( unsigned i = 0; i < v.size(); i++ )
    if ( v[i] == min_value )
      min_indices.push_back(i);
  return min_indices;
}

vector<unsigned> vectorAleatorio(unsigned n) {
  // algoritmo de Fisher-Yates
  vector<unsigned> result;
  for ( unsigned i = 0; i < n; i++ )
    result.push_back(i);
  for ( unsigned i = n-1; i > 0; i-- ) {
    unsigned j = Randint(0, i+1);
    unsigned temp = result[i];
    result[i] = result[j];
    result[j] = temp;
  }
  return result;
}


/*************************/
/* Particion             */
/*************************/

vector<Dato> Particion::getClusterDatos(unsigned id_cluster) const {
  vector<Dato> cluster_datos;
  for ( unsigned i = 0; i < _clusters.size(); i++ )
    if ( _clusters[i] == id_cluster )
      cluster_datos.push_back(_datos[i]);
  return cluster_datos;
}

vector<unsigned> Particion::getClusterIndices(unsigned id_cluster) const {
  vector<unsigned> cluster_indices;
  for ( unsigned i = 0; i < _clusters.size(); i++ )
    if ( _clusters[i] == id_cluster )
      cluster_indices.push_back(i);
  return cluster_indices;
}

Dato Particion::calcularCentroide(unsigned id_cluster) const {
  return media(getClusterDatos(id_cluster));
}

void Particion::actualizarCentroides() {
  for ( unsigned i = 0; i < _n_clusters; i++ ) {
    Dato c = calcularCentroide(i);
    if ( c.size() > 0 ) _centroides[i] = c;
  }
}

Particion Particion::aplicarVecino(const Vecino &vecino) const {
  Particion part(*this);
  part._clusters[vecino.first] = vecino.second;
  return part;
}

double Particion::dmic(unsigned id_cluster) const {
  double _dmic = 0;
  vector<Dato> cluster = getClusterDatos(id_cluster);
  Dato centroide = calcularCentroide(id_cluster);
  for ( Dato dato : cluster )
    _dmic += dist(dato, centroide);
  return _dmic/cluster.size();
}

unsigned Particion::h(unsigned ind_dato) const {
  return _clusters[ind_dato];
}

double Particion::dgp() const {
  double _dgp = 0;
  for ( unsigned i = 0; i < _n_clusters; i++ )
    _dgp += dmic(i);
  return _dgp/_n_clusters;
}

bool Particion::esValida() const {
  vector<bool> checker(_n_clusters, false);
  for ( unsigned cluster_id : _clusters )
    checker[cluster_id] = true;
  for ( bool check : checker )
    if ( !check ) return false;
  return true;
}

void Particion::printClusters() const {
  cout << _clusters << endl;
}

void Particion::printCentroides() const {
  for ( unsigned i = 0; i < _n_clusters; i++ )
    cout << "(centroide " << i << ") -> " << _centroides[i] << endl;
}


/*************************/
/* PAR                   */
/*************************/

PAR::PAR(const string &archivo_datos, const string &archivo_restricciones, int n_clusters, unsigned long semilla) {
  _n_clusters = n_clusters;
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

    _datos.push_back(dato);
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

    _restr_mat.push_back(row);
    row.clear();
  }

  Restriccion restr;
  for ( unsigned i = 0; i < _restr_mat.size(); i++ ) {
    for ( unsigned j = i+1; j < _restr_mat[i].size(); j++ ) {
      if ( _restr_mat[i][j] != 0 ) {
        restr.indices = make_pair(i, j);
        restr.tipo = _restr_mat[i][j];
        _restr_list.push_back(restr);
      }
    }
  }

  unsigned most_distant_1 = 0, most_distant_2 = 0;
  _max_dist = 0;
  for ( unsigned i = 0; i < _datos.size(); i++ ) {
    vector<double> dist_row;
    for ( unsigned j = 0; j < _datos.size(); j++ ) {
      double distancia = dist(_datos[i], _datos[j]);
      if ( distancia > _max_dist ) {
        most_distant_1 = i;
        most_distant_2 = j;
        _max_dist = distancia;
      }
      dist_row.push_back(distancia);
    }
    _dists.push_back(dist_row);
  }

  _lambda = _max_dist / _restr_list.size();
  
  Set_random(semilla);

  cout << "Importación satisfactoria" << endl
       << "\tTamaño dataset: " << _datos.size() << endl
       << "\tTamaño restricciones: " << _restr_list.size() << endl;
}

bool PAR::v(const Particion &part, unsigned i, unsigned j) const {
  if ( part.h(i) < 0 || part.h(j) < 0 ) return false;
  switch (_restr_mat[i][j]) {
    case -1:
      return part.h(i) != part.h(j);
    case 1:
      return part.h(i) == part.h(j);
    default:
      return false;
  }
}

int PAR::infeasibility(const Particion &part) const {
  int inf = 0;
  for ( Restriccion restr : _restr_list )
    if ( v(part, restr.indices.first, restr.indices.second) )
      inf++;
  return inf;
}

int PAR::incr_infeasibility(const Particion &part, unsigned i, unsigned j) const {
  int inf_0 = infeasibility(part);
  Particion part2(part);
  part2._clusters[i] = j;
  int inf_1 = infeasibility(part2);
  return inf_1-inf_0;
}

vector<unsigned> PAR::shuffleIndices() const {
  return vectorAleatorio(getSize());
}

Particion PAR::generaCentroidesIniciales() const {
  // tomar valores mínimos y máximos en cada dimensión
  vector<pair<double, double> > min_max;
  for ( unsigned d = 0; d < getDim(); d++ ) {
    double min = _datos[0][d], max = _datos[0][d];
    for ( Dato dato : _datos ) {
      if ( dato[d] < min ) min = dato[d];
      if ( dato[d] > max ) max = dato[d];
    }
    //cout << "d="<<d<<"-> min="<<min<<", max="<<max<<endl;
    min_max.push_back(make_pair(min, max));
  }

  // generamos un dato en [min, max) para cada dimensión, para cada cluster
  vector<Dato> centroides;
  for ( unsigned i = 0; i < _n_clusters; i++ ) {
    Dato centroide;
    for ( unsigned d = 0; d < getDim(); d++ )
      centroide.push_back(Randfloat(min_max[d].first, min_max[d].second));
    centroides.push_back(centroide);
    centroide.clear();
  }

  /*DELETE cout << "memory index: " << &centroides << endl;
  for ( auto c : centroides) {
    for (unsigned d=0; d < getDimension(); d++)
      cout << c[d] << " ";
    cout << endl;
  }*/

  // en principio no asignamos aún los datos al clúster
  vector<int> cluster(_datos.size(), -1);
  Particion part_inicial(_datos, cluster, centroides);

  return part_inicial;
  /*vector<unsigned> indices = shuffleIndices();
  vector<Dato> centroides;
  for ( unsigned i = 0; i < _n_clusters; i++ ) {
    centroides.push_back(_datos[indices[i]]);
  }
  return Particion(_datos, centroides);*/
}

Particion PAR::generaClustersIniciales() const {
  vector<int> clusters(getSize(), -1);
  // suffle de clusters
  vector<unsigned> indices = shuffleIndices();
  // primero aseguramos que se asigna al menos un dato a cada cluster
  for ( unsigned i = 0; i < _n_clusters; i++ )
    clusters[indices[i]] = i;
  // añadimos más asignaciones aleatoriamente
  for ( unsigned i = _n_clusters; i < getSize(); i++ )
    clusters[indices[i]] = Randint(0, _n_clusters);

  return Particion(_datos, clusters, _n_clusters);
}

void PAR::restartVecinoVirtual() {
  vector<unsigned> indices_flat = vectorAleatorio(getSize()*_n_clusters);
  _orden_expl_vecinos.clear();
  for ( unsigned indice : indices_flat )
    _orden_expl_vecinos.push_back(
      make_pair(indice/_n_clusters, indice-indice/_n_clusters*_n_clusters)
    );
  _expl_vecino_next = 0;
}

Particion PAR::busquedaGreedy() const {
  Particion part_prev = generaCentroidesIniciales(), part_nueva(part_prev);
  cout << "Generados centroides iniciales" << endl;
  part_prev.printCentroides();
  vector<unsigned> RSI = shuffleIndices();
  bool hay_cambio = true;
  while (hay_cambio) {
    for ( unsigned i : RSI ) {
      // calcular incremento en infeasibility que produce la asignación
      // de cada x_i a cada c_j
      vector<int> incrs_infeasibility;
      //cout << "part_prev before: " << part_prev->_clusters << endl;
      //cout << "part_nueva before: " << part_nueva->_clusters << endl;
      for ( unsigned j = 0; j < _n_clusters; j++ )
        incrs_infeasibility.push_back(incr_infeasibility(part_nueva, i, j));
      cout << "incrs_infeasibility: " << incrs_infeasibility << endl;
      //cout << "part_prev after: " << part_prev->_clusters << endl;
      //cout << "part_nueva after: " << part_nueva->_clusters << endl;

      vector<unsigned> min_incrs_infeasibility = getMinIndices(incrs_infeasibility);
      unsigned best_j = 0;
      for ( int j = 1; j < min_incrs_infeasibility.size(); j++ )
        if (
          dist(_datos[i], part_prev._centroides[min_incrs_infeasibility[j]])
            < dist(_datos[i], part_prev._centroides[min_incrs_infeasibility[best_j]])
        ) best_j = j;
      cout << "Reasignando x_" << i << " a c_" << min_incrs_infeasibility[best_j] << endl;
      part_nueva._clusters[i] = min_incrs_infeasibility[best_j];
    }
    part_nueva->actualizarCentroides();
    cout << "clusters part_nueva: " << part_nueva->_clusters << endl;
    hay_cambio = (part_nueva->_clusters != part_prev->_clusters);
    part_prev = part_nueva;
  }

  return *part_nueva;
}

void PAR::printMe() const {
  cout << "restrmat" << endl;
  for ( auto row : _restr_mat ) {
    cout << row << endl;
  }
  cout << endl << "restrlist" << endl;
  for ( auto r : _restr_list ) {
    cout << r.indices.first << " " << r.indices.second << "  -- " << r.tipo << endl;
  }
}