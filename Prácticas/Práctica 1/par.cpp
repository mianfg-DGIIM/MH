#include "par.h"
#include <iostream>
#include <sstream>
#include <algorithm>

double distancia_euclidea(Dato d1, Dato d2) {
  double suma = 0;
  for ( int i = 0; i < d1.size(); i++ ) {
    suma += (d1[i] - d2[i])*(d1[i] - d2[i]);
  }
  return sqrt(suma);
}

Dato media(const vector<Dato> &datos) {
  //cout << "entered media ";
  if (datos.size() > 0) {
    Dato media(datos[0].size(), 0);
    for ( Dato dato : datos )
      for ( unsigned i = 0; i < media.size(); i++ )
        media[i] += dato[i];
    for ( unsigned i = 0; i < media.size(); i++ )
      media[i] /= datos.size();
    //cout << "left media";
    return media;
  } else
    return Dato();
}

vector<unsigned> getMinIndices(const vector<int> &v) {
  int min_value = *min_element(v.begin(), v.end());
  vector<unsigned> min_indices;

  for ( unsigned i = 0; i < v.size(); i++ )
    if ( v[i] == min_value )
      min_indices.push_back(i);
  
  return min_indices;
}

vector<unsigned> randomVector(unsigned n) {
  // usa algoritmo de Fisher-Yates
  vector<unsigned> result;
  for ( unsigned i=0; i < n; i++ )
    result.push_back(i);
  
  for ( unsigned i = n-1; i > 0; i-- ) {
    unsigned j = Randint(0, i+1);

    unsigned temp = result[i];
    result[i] = result[j];
    result[j] = temp;
  }
  
  return result;
}


// --- Particion ---

/*Particion* Particion::clone() const {
  vector<int> clusters = vector<int>(_clusters);
  vector<Dato> centroides = vector<Dato>(_centroides);

  return new Particion(_datos, clusters, centroides);
}*/

Particion::~Particion() {
  //cout << "deleting particion..." << endl;
  vector<int>().swap(_clusters);
  vector<Dato>().swap(_centroides);
  //cout << "particion deleted " << endl;
}

void Particion::printClusters() {
  for ( int c : _clusters ) {
    cout << c << " ";
  }
  cout << endl;
}

void Particion::printCentroides() {
  for ( Dato centroide: _centroides ) {
    cout << centroide << ", " << endl;
  }
  cout << endl;
}
void Particion::printMe() {
  cout << endl << "clusters: ";
  for ( int c : _clusters ) {
    cout << c << " ";
  }

  cout << endl << "centroides: ";
  for ( Dato centroide: _centroides ) {
    cout << "Leyendo un centroide" << endl;
    for (unsigned i = 0; i < getDimension(); i++) {
      cout << "("<<i<<") " <<centroide[i] << " ";
    }
    cout << endl;
  }
  cout << endl;
}

unsigned Particion::getSize() const {
  return _clusters.size();
}
unsigned Particion::getDimension() const {
  return _datos.at(0).size();
}

vector<Dato> Particion::getCluster(unsigned ind_cluster) const {
  //cout << "entered getCluster" << endl;
  vector<Dato> cluster;

  //cout<<"cluster has: ";
  for ( unsigned i = 0; i < _clusters.size(); i++ )
    if ( _clusters.at(i) == ind_cluster ) {
      //cout << i << " ";
      cluster.push_back(_datos.at(i));
    }
  //cout << endl << "leaving getcluster, cluster("<<ind_cluster<<")=";
  //for ( Dato d: cluster ) cout << d << ", " << endl;
  //cout << endl;
  return cluster;
}

vector<unsigned> Particion::getClusterIndices(unsigned ind_cluster) const {
  vector<unsigned> cluster;

  for ( unsigned i = 0; i < _clusters.size(); i++ )
    if ( _clusters.at(i) == ind_cluster )
      cluster.push_back(i);
  
  return cluster;
}

Dato Particion::centroide(unsigned ind_cluster) const {
  return media(getCluster(ind_cluster));
}

void Particion::actualizarCentroides() {
  //cout << "entered AC" << endl;
  //cout << "cleared centroides, nclusters: " << _n_clusters << endl;

  //cout << "centroide at i="<<0<<": "<<centroide(0)<<endl; 
  for ( unsigned i = 0; i < _n_clusters; i++ ) {
    //cout << "centroide at i="<<i<<": "<<centroide(i)<<endl;
    Dato c = centroide(i);
    if ( c.size() > 0 )
      _centroides[i] = c;
  }
}

double Particion::dmic(unsigned ind_cluster) const {
  double _dmic = 0;
  vector<Dato> cluster = getCluster(ind_cluster);

  for ( Dato dato : cluster )
    _dmic += distancia_euclidea(dato, centroide(ind_cluster));
  
  return _dmic/cluster.size();
}

unsigned Particion::h(unsigned ind_dato) const {
  return _clusters.at(ind_dato);
}

Particion Particion::apply(const Vecino &vec) const {
  Particion part(*this);
  part._clusters[vec.first] = vec.second;
}

double Particion::dgp() const {
  double _dgp = 0;

  for ( unsigned i = 1; i <= _n_clusters; i++ )
    _dgp += dmic(i);
  
  return _dgp / _n_clusters;
}

bool Particion::esValida() const {
  cout << "entered esvalida" << endl;
  for ( unsigned i = 0; i < _n_clusters; i++ ) {
    cout << "buscando instancia de cluster " << i << "...\n";
    for ( unsigned j = 0; j < getSize(); j++ ) {
      cout << "   en el j="<<j<<" es " << _clusters.at(j) << endl;
      if ( _clusters.at(j) == i ) break;
      if ( j == _clusters.size()-1 ) return false;
    }
  }
  cout << "left esvalida" << endl;

  return true;
}


// --- PAR ---

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
    for ( unsigned j = i; j < _restr_mat[i].size(); j++ ) {
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
      double distancia = distancia_euclidea(_datos[i], _datos[j]);
      if ( distancia > _max_dist ) {
        most_distant_1 = i;
        most_distant_2 = j;
        _max_dist = distancia;
      }
      dist_row.push_back(distancia);
    }
    _dists.push_back(dist_row);
  }
  _most_distant = make_pair(most_distant_1, most_distant_2);

  _lambda = _max_dist / _restr_list.size();
  
  Set_random(semilla);

  cout << "Importación satisfactoria" << endl
       << "\tTamaño dataset: " << _datos.size() << endl
       << "\tTamaño restricciones: " << _restr_list.size() << endl;
}

unsigned PAR::getSize() const {
  return _datos.size();
}

unsigned PAR::getDimension() const {
  return _datos[0].size();
}

bool PAR::v(const Particion &part, unsigned i, unsigned j) const {
  if ( i > j ) {
    unsigned temp = i;
    i = j;
    j = temp;
  } else if ( i == j ) {
    return false;
  }

  switch (_restr_mat[i][j]) {
    case -1:
      return part.h(i) != part.h(j);
    case 1:
      return part.h(i) == part.h(j);
    default:
      return false;
  }
  //return restr.tipo != 0 && restr.tipo == 1 && h(restr.indices.first) == h(restr.indices.second);
}

double PAR::f(const Particion &part) const {
  return part.dgp() +  _lambda*infeasibility(part);
}

int PAR::infeasibility(const Particion &part) const {
  int infeasibility = 0;
  for (Restriccion restr : _restr_list) {
    if ( v(part, restr.indices.first, restr.indices.second) )
      infeasibility += 1;
  }
}

int PAR::incr_infeasibility(Particion part, unsigned i, unsigned j) const {
  int inf_0 = infeasibility(part);
  part._clusters[i] = j;
  int inf_1 = infeasibility(part);
  /*int inf_0 = 0;
  for ( unsigned k = 0; k < getSize(); k++ )
    if ( v(part, i, k) ) inf_0 += 1;
  part._clusters[i] = j;
  int inf_1 = 0;
  for ( unsigned k = 0; k < getSize(); k++ )
    if ( v(part, i, k) ) inf_1 += 1;*/
  
  return inf_1-inf_0;
}

vector<unsigned> PAR::shuffleIndices() const {
  return randomVector(_datos.size());
}

Particion PAR::generaCentroidesIniciales() const {
  // tomar valores mínimos y máximos en cada dimensión
  vector<pair<double, double> > min_max;
  for ( unsigned d = 0; d < getDimension(); d++ ) {
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
    for ( unsigned d = 0; d < getDimension(); d++ )
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
}

Particion PAR::generaClustersIniciales() const {
  vector<int> clusters(getSize(), -1);
  // shuffle de clusters
  vector<unsigned> indices = randomVector(getSize());
  
  // primero aseguramos que se asigna al menos un dato a cada cluster
  for ( int i = 0; i < _n_clusters; i++ )
    clusters[indices[i]] = i;
  // añadimos más asignaciones aleatoriamente
  for ( int i = _n_clusters; i < getSize(); i++ )
    clusters[indices[i]] = Randint(0, _n_clusters);
  
  return Particion(_datos, clusters);
}

void PAR::restartVecinoVirtual() {
  vector<unsigned> indices_flat = randomVector(getSize()*_n_clusters);
  _orden_expl_vecinos.clear();
  for ( unsigned indice : indices_flat )
    _orden_expl_vecinos.push_back(make_pair(indice/_n_clusters, indice-indice/_n_clusters*_n_clusters));
  _expl_vecino_next = 0;
}

Vecino *PAR::nextVecinoVirtual(const Particion &part) {
  Particion candidata_inicial = part.apply(_orden_expl_vecinos[_expl_vecino_next]);
  cout << "applied" << endl;
  Particion * candidata = &candidata_inicial;
  while (!candidata->esValida()) {
    cout << "candidate invalid " << endl;
    _expl_vecino_next++;
    if (_expl_vecino_next < _orden_expl_vecinos.size()) {
      Particion c = part.apply(_orden_expl_vecinos[_expl_vecino_next]);
      candidata = &c;
    } else {
      return NULL;
    }
  }
  cout << "outofwhile" << endl;
  _expl_vecino_next++;
  return &_orden_expl_vecinos[_expl_vecino_next-1];
}

Particion PAR::busquedaGreedy() const {
  Particion part_inicial = generaCentroidesIniciales();
  cout << "Generandos centroides iniciales. Centroides: ";
  part_inicial.printCentroides();
  Particion *part_prev = &part_inicial, *part_nueva;
  vector<unsigned> RSI = shuffleIndices();
  cout << endl << "Recorrido indices: " << endl;
  cout << RSI << endl;
  cout << endl;
  bool hay_cambio = true;
  while (hay_cambio) {
    part_nueva = new Particion(*part_prev);
    for ( unsigned i : RSI ) {
      // calcular incremento en infeasibility que produce la asignación
      // de cada x_i a cada c_j
      //cout << "********* i= " << i<< endl;
      vector<int> incrs_infeasibility;
      for ( int j = 0; j < _n_clusters; j++ ) {
        incrs_infeasibility.push_back(incr_infeasibility(*part_prev, i, j));
      }

      //cout << "incr. infeasibility: " << incrs_infeasibility << endl;

      vector<unsigned> min_incrs_infeasibility = getMinIndices(incrs_infeasibility);
      //cout << "min incr. infeasibility: " << min_incrs_infeasibility << endl << "dists: ";
      unsigned best_j = 0;
      for ( int j = 1; j < min_incrs_infeasibility.size(); j++ ) {
        //cout << distancia_euclidea(_datos.at(i), part_prev->_centroides.at(min_incrs_infeasibility[j]))
        //<< ", ";
        
        if (
          distancia_euclidea(_datos.at(i), part_prev->_centroides.at(min_incrs_infeasibility[j]))
          < distancia_euclidea(_datos.at(i), part_prev->_centroides.at(min_incrs_infeasibility[best_j]))
        ) best_j = j;
      }

      //cout << endl << "best j (closest) : " << min_incrs_infeasibility[best_j] << endl;

      // actualizar partición (generar nueva)
      part_nueva->_clusters.at(i) = min_incrs_infeasibility[best_j];
      
      //part_nueva->actualizarCentroides();
      //cout << "centroides actualizados " << endl;
      //incrs_infeasibility.clear();
      //hay_cambio = (part_nueva->_clusters != part_prev->_clusters);
      
    }
    part_nueva->actualizarCentroides();
    cout << "clusters part nueva: " << part_nueva->_clusters << endl;
    hay_cambio = (part_nueva->_clusters != part_prev->_clusters);
    delete part_prev;
    part_prev = part_nueva;
  }

  //part_nueva->fixMe();

  return *part_nueva;
}

Particion PAR::busquedaLocal(unsigned max_iters) {
  Particion part_inicial = generaClustersIniciales();
  cout << "Generandos clusters iniciales. Clusters: ";
  part_inicial.printClusters();
  restartVecinoVirtual();
  Particion *part_prev = &part_inicial, *part_nueva;
  unsigned iter = 0;

  while (iter <= max_iters) {
    while (true) {
      Vecino * nvv = nextVecinoVirtual(*part_prev);
      cout << "nvv: " << nvv->first << " " << nvv->second << endl;
      if ( nvv ) {
        Particion part = part_prev->apply(*nextVecinoVirtual(*part_prev));
        part_nueva = &part;
        if ( f(*part_nueva) < f(*part_prev) ) {
          delete part_prev;
          part_prev = part_nueva;
          break;
        }
      } else {
        // no hay más vecinos que explorar, terminamos
        iter = max_iters;
      }
    }
    iter++;
  }

  return *part_nueva;
}