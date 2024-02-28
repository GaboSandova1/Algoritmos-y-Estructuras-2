from datetime import datetime
import xml.etree.ElementTree as ET
import csv
import json
import pickle
import os
import datetime

class Nodo:
    def __init__(self, elemento, siguiente=None, left = None, right = None):
        self.elemento = elemento
        self.siguiente = siguiente
        self.left = left
        self.right = right

class  ArbolB(object):
    def __init__(self):
        self.raiz = None

        #Metodos para agregar
    def insertar(self, valor):
            if self.raiz is None:
                self.raiz = Nodo(valor)
            else:
                self._insertar_recursivo(valor, self.raiz)

    def _insertar_recursivo(self, valor, nodo_actual):
            if valor < nodo_actual.valor:
                if nodo_actual.left is None:
                    nodo_actual.left = Nodo(valor)
                else:
                    self._insertar_recursivo(valor, nodo_actual.left)
            elif valor > nodo_actual.valor:
                if nodo_actual.right is None:
                    nodo_actual.right = Nodo(valor)
                else:
                    self._insertar_recursivo(valor, nodo_actual.right)

    def eliminar(self, valor):
        self.raiz = self._eliminar_recursivo(valor, self.raiz)

    def _eliminar_recursivo(self, valor, nodo_actual):
        if nodo_actual is None:
            return None
        if valor < nodo_actual.valor:
            nodo_actual.left = self._eliminar_recursivo(valor, nodo_actual.left)
        elif valor > nodo_actual.valor:
            nodo_actual.right = self._eliminar_recursivo(valor, nodo_actual.right)
        else:
            if nodo_actual.left is None:
                return nodo_actual.right
            elif nodo_actual.right is None:
                return nodo_actual.left
            else:
                sucesor = self._encontrar_minimo(nodo_actual.right)
                nodo_actual.valor = sucesor.valor
                nodo_actual.right = self._eliminar_recursivo(sucesor.valor, nodo_actual.right)
                return nodo_actual
            
    def _encontrar_minimo(self, nodo_actual):
        if nodo_actual.left is None:
            return nodo_actual
        return self._encontrar_minimo(nodo_actual.left)
    
    def modificar(self, valor_viejo, valor_nuevo):
        self.eliminar(valor_viejo)
        self.insertar(valor_nuevo)

    def consultar(self, valor):
        return self._consultar_recursivo(valor, self.raiz)
    
    def _consultar_recursivo(self, valor, nodo_actual):
        if nodo_actual is None or nodo_actual.valor == valor:
            return nodo_actual
        if valor < nodo_actual.valor:
            return self._consultar_recursivo(valor, nodo_actual.left)
        return self._consultar_recursivo(valor, nodo_actual.right)
    
    def preorden(self):
        self._preorden_recursivo(self.raiz)

    def _preorden_recursivo(self, nodo_actual):
        if nodo_actual is not None:
            print(nodo_actual.valor, end=" ")
        self._preorden_recursivo(nodo_actual.left)
        self._preorden_recursivo(nodo_actual.right)

    def inorden(self):
        self._inorden_recursivo(self.raiz)

    def _inorden_recursivo(self, nodo_actual):
        if nodo_actual is not None:
            self._inorden_recursivo(nodo_actual.left) 
            print(nodo_actual.valor, end=" ")
            self._inorden_recursivo(nodo_actual.right)

    def postorden(self):
        self._postorden_recursivo(self.raiz)

    def _postorden_recursivo(self, nodo_actual):
        if nodo_actual is not None:
            self._postorden_recursivo(nodo_actual.left)
            self._postorden_recursivo(nodo_actual.right)
            print(nodo_actual.valor, end=" ")

class Pila:
    def __init__(self):
        self.cima = None

    def esta_vacia(self):
        return self.cima == None

    def apilar(self, elemento):
        nuevo_nodo = Nodo(elemento)
        if not self.esta_vacia():
            nuevo_nodo.siguiente = self.cima
        self.cima = nuevo_nodo

    def desapilar(self):
        if self.esta_vacia():
            return None
        else:
            elemento = self.cima.elemento
            self.cima = self.cima.siguiente
            return elemento

class Cola:
    def __init__(self):
        self.frente = None
        self.final = None

    def esta_vacia(self):
        return self.frente == None

    def encolar(self, elemento):
        nuevo_nodo = Nodo(elemento)
        if not self.esta_vacia():
            self.final.siguiente = nuevo_nodo
            self.final = nuevo_nodo
        else:
            self.frente = nuevo_nodo
            self.final = nuevo_nodo

    def desencolar(self):
        if self.esta_vacia():
            return None
        else:
            elemento = self.frente.elemento
            self.frente = self.frente.siguiente
            if self.frente == None:
                self.final = None
            return elemento

# Clase para los ficheros
class NodoDirectorio:
    def __init__(self, nombre, elemento,  padre=None, siguiente=None):
        self.nombre = nombre
        self.padre = padre
        self.subdirectorios = []
        self.archivos = []
        self.elemento = elemento
        self.siguiente = siguiente

    def listar_archivos(self):
        archivos = []
        for archivo in self.archivos:
            archivos.append(archivo.nombre)
        return archivos

class Directorio:
    def __init__(self, nombre, unidad, ubicacion):
        self.unidad = unidad
        self.nombre = nombre
        self.nodo = NodoDirectorio(nombre, None, self)
        self.nodo.padre = self
        self.ubicacion = ubicacion
        self.nodo = NodoDirectorio('root', ubicacion)
        self.nodo.padre = None
        self.archivos = []

    def agregar_subdirectorio(self, nombre):
        nodo = NodoDirectorio(nombre, self.nodo)
        self.nodo.subdirectorios.append(nodo)

    def eliminar_subdirectorio(self, nombre):
        for subdir in self.nodo.subdirectorios:
            if subdir.nombre == nombre:
                self.nodo.subdirectorios.remove(subdir)
                return
    
    def listar_subdirectorios(self):
        subdirectorios = []
        for subdir in self.nodo.subdirectorios:
            subdirectorios.append(subdir.nombre)
        return subdirectorios

    def agregar_archivo(self, nombre, contenido):
        nodo = NodoArchivo(nombre, contenido, self.nodo)
        self.nodo.archivos.append(nodo)

    def eliminar_archivo(self, nombre):
        for archivo in self.nodo.archivos:
            if archivo.nombre == nombre:
                self.nodo.archivos.remove(archivo)
                return

    def listar_archivos(self):
        archivos = []
        for archivo in self.nodo.archivos:
            archivos.append(archivo.nombre)
        return archivos
    
class NodoArchivo:
    def __init__(self, nombre, contenido, padre=None):
        self.nombre = nombre
        self.padre = padre
        self.contenido = contenido
        self.size = len(contenido)


class Fichero:
    def _init_(self, ID, nombre, tamaño, extensión, fechaCreación, fechaModificación, contenido):
        self.ID = ID
        self.nombre = nombre
        self.tamaño = tamaño
        self.extensión = extensión
        self.fechaCreación = fechaCreación
        self.fechaModificación = fechaModificación
        self.contenido = contenido

# Clase para las carpetas
class Carpeta:
    def _init_(self, ID, nombre, listaFicheros, fechaCreación, listaCarpetas):
        self.ID = ID
        self.nombre = nombre
        self.listaFicheros = listaFicheros
        self.fechaCreación = fechaCreación
        self.listaCarpetas = listaCarpetas
        self.tamañoTotal = sum(fichero.tamaño for fichero in listaFicheros)
        self.lista_archivos = Pila()
        self.lista_carpetas = Cola()

    def agregar_archivo(self, fichero):
        self.lista_archivos.apilar(fichero)

    def eliminar_archivo(self):
        return self.lista_archivos.desapilar()

    def listar_archivos(self):
        archivos = []
        actual = self.lista_archivos.cima
        while actual != None:
            archivos.append(actual.elemento.nombre)
            actual = actual.siguiente
        return archivos

    def agregar_carpeta(self, carpeta):
        self.lista_carpetas.encolar(carpeta)

    def eliminar_carpeta(self):
        return self.lista_carpetas.desencolar()

    def listar_carpetas(self):
        carpetas = []
        actual = self.lista_carpetas.frente
        while actual != None:
            carpetas.append(actual.elemento.nombre)
            actual = actual.siguiente
        return carpetas

# Clase para las unidades
class Unidad:
    def _init_(self, ID, nombre, capacidadTotal, espacioDisponible, listaCarpetas, tipoUnidad, letra, directorio_raiz):
        self.ID = ID
        self.nombre = nombre
        self.capacidadTotal = capacidadTotal
        self.espacioDisponible = espacioDisponible
        self.listaCarpetas = listaCarpetas
        self.tipoUnidad = tipoUnidad
        self.carpeta_raiz = Carpeta(nombre)
        self.letra = letra
        self.directorio_raiz = Directorio(directorio_raiz)
        self.siguiente = None

    def agregar_unidad(self, letra, directorio_raiz):
        nueva_unidad = Unidad(letra, directorio_raiz)
        nueva_unidad.siguiente = self.siguiente
        self.siguiente = nueva_unidad

    def listar_unidades(self):
        unidades = []
        actual = self
        while actual is not None:
            unidades.append((actual.letra, actual.directorio_raiz.nombre))
            actual = actual.siguiente
        return unidades

    def agregar_archivo(self, nombre_carpeta, nombre_archivo, contenido):
        carpeta = self.buscar_carpeta(nombre_carpeta)
        if carpeta != None:
            fichero = Fichero(nombre_archivo, contenido)
            carpeta.agregar_archivo(fichero)
        else:
            print("Carpeta no encontrada")

    def eliminar_archivo(self, nombre_carpeta, nombre_archivo):
        carpeta = self.buscar_carpeta(nombre_carpeta)
        if carpeta != None:
            carpeta.eliminar_archivo()
        else:
            print("Carpeta no encontrada")

    def listar_archivos(self, nombre_carpeta):
        carpeta = self.buscar_carpeta(nombre_carpeta)
        if carpeta != None:
            return carpeta.listar_archivos()
        else:
            print("Carpeta no encontrada")

    def agregar_carpeta(self, nombre_carpeta_padre, nombre_carpeta_hija):
        carpeta_padre = self.buscar_carpeta(nombre_carpeta_padre)
        if carpeta_padre != None:
            nueva_carpeta = Carpeta(nombre_carpeta_hija)
            carpeta_padre.agregar_carpeta(nueva_carpeta)
        else:
            print("Carpeta padre no encontrada")

    def eliminar_carpeta(self, nombre_carpeta):
        carpeta_raiz = self.carpeta_raiz
        if carpeta_raiz.nombre == nombre_carpeta:
            self.carpeta_raiz = None
        else:
            self.buscar_carpeta(nombre_carpeta).eliminar_carpeta()

    def listar_carpetas(self):
        return self.carpeta_raiz.listar_carpetas()

    def buscar_carpeta(self, nombre_carpeta):
        actual = self.carpeta_raiz
        while actual != None:
            if actual.nombre == nombre_carpeta:
                return actual
            actual = actual.lista_carpetas.frente
        return None

# Clase para los comandos
class Comando:
    def _init_(self, ID, nombreComando, descripción, rolRequerido):
        self.ID = ID
        self.nombreComando = nombreComando
        self.descripción = descripción
        self.rolRequerido = rolRequerido

# Lógica para manejar los archivos xml, csv, json o serializados
# Función para guardar los datos en un archivo XML
def guardar_en_xml(datos, nombre_archivo):
    root = ET.Element("datos")
    for dato in datos:
        elemento = ET.SubElement(root, "dato")
        for key, value in dato.items():
            subelemento = ET.SubElement(elemento, key)
            subelemento.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(nombre_archivo)

# Función para cargar los datos desde un archivo XML
def cargar_desde_xml(nombre_archivo):
    tree = ET.parse(nombre_archivo)
    root = tree.getroot()
    datos = []
    for elemento in root.findall("dato"):
        dato = {}
        for subelemento in elemento:
            dato[subelemento.tag] = subelemento.text
        datos.append(dato)
    return datos

# Función para guardar los datos en un archivo CSV
def guardar_en_csv(datos, nombre_archivo):
    with open(nombre_archivo, 'w', newline='') as csvfile:
        fieldnames = datos[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for dato in datos:
            writer.writerow(dato)

# Función para cargar los datos desde un archivo CSV
def cargar_desde_csv(nombre_archivo):
    with open(nombre_archivo, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        datos = [dict(row) for row in reader]
    return datos

# Función para guardar los datos en un archivo JSON
def guardar_en_json(datos, nombre_archivo):
    with open(nombre_archivo, 'w') as jsonfile:
        json.dump(datos, jsonfile)

# Función para cargar los datos desde un archivo JSON
def cargar_desde_json(nombre_archivo):
    with open(nombre_archivo, 'r') as jsonfile:
        datos = json.load(jsonfile)
    return datos

# Función para guardar los datos en un archivo serializado
def guardar_serializado(datos, nombre_archivo):
    with open(nombre_archivo, 'wb') as file:
        pickle.dump(datos, file)

# Función para cargar los datos desde un archivo serializado
def cargar_serializado(nombre_archivo):
    with open(nombre_archivo, 'rb') as file:
        datos = pickle.load(file)
    return datos


# Lógica para cargar los datos al iniciar el programa y manejar excepciones
def guardar_datos(unidades, formato):
    if formato == "json":
        with open("unidades.json", "w") as f:
            json.dump([unidad.to_dict() for unidad in unidades], f)
    elif formato == "serializado":
        with open("unidades.pickle", "wb") as f:
            pickle.dump(unidades, f)

def cargar_datos(nombre_archivo, formato):
    try:
        if formato == "json":
            with open("unidades.json", "r") as f:
                unidades = [Unidad.from_dict(d) for d in json.load(f)]
        elif formato == "serializado":
            with open("unidades.pickle", "rb") as f:
                unidades = pickle.load(f)
        else:
            raise ValueError("Formato de archivo no válido")
    except FileNotFoundError:
        print(f"El archivo de datos no existe")
        unidades = []
    except Exception as e:
        print(f"Ocurrió un error al cargar los datos: {e}")
        unidades = []
    return unidades

# Cargar los datos al iniciar el programa
nombre_archivo = "datos.xml"
formato = "xml"  # Puedes cambiar el formato según tus necesidades
datos = cargar_datos(nombre_archivo, formato)
print(datos)  # Hacer algo con los datos cargados


# Implementación del comando "dir" con algoritmos de ordenamiento

def obtener_tamaño_archivo(ubicacion, archivo):
    ruta_completa = os.path.join(ubicacion, archivo)
    return os.path.getsize(ruta_completa)

def listar_archivos_por_tamaño(ubicacion):
    archivos = []
    for archivo in os.listdir(ubicacion):
        if os.path.isfile(os.path.join(ubicacion, archivo)):
            tamaño = obtener_tamaño_archivo(ubicacion, archivo)
            archivos.append((archivo, tamaño))
    return archivos

def particion(arr, low, high):
    i = (low - 1)
    pivot = arr[high].size

    for j in range(low, high):
        if arr[j].size <= pivot:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return (i + 1)

def quickSort(arr, low, high):
    if len(arr) == 1:
        return arr
    if low < high:
        pi = particion(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)

def dir_ordenar_por_tamaño(directorio, ubicacion, orden):
    actual = directorio.nodo
    actual.listar_archivos()
    factor_orden = 1 if orden == "ascendente" else -1
    quickSort(directorio.nodo.archivos, 0, len(directorio.nodo.archivos) - 1)
    if factor_orden == -1:
        directorio.nodo.archivos = directorio.nodo.archivos[::-1]
    return directorio.nodo.archivos

# Ubicación de los archivos
ubicacion_archivos = 'C:\\Users\\Gabo Sandoval\\OneDrive\\Escritorio\\algoritmos2'

# Listar archivos por tamaño
archivos = listar_archivos_por_tamaño(ubicacion_archivos)

directorio = Directorio('nombre_directorio', 'C:\\', 'C:\\Users\\Gabo Sandoval\\OneDrive')
ubicacion_archivos = 'C:\\Users\\Gabo Sandoval\\OneDrive\\Escritorio\\algoritmos2'
orden = 'ascendente'
archivos_ordenados = dir_ordenar_por_tamaño(directorio, ubicacion_archivos, orden)
for archivo in archivos_ordenados:
    print(archivo.nombre)

# Ordenar archivos por tamaño usando QuickSort
archivos_ordenados = dir_ordenar_por_tamaño(directorio, ubicacion_archivos, "ascendente")
for archivo in archivos_ordenados:
    print(archivo.nombre)


def dir_ordenar_por_fecha_modificación(unidad, ubicacion, orden):
    # Lógica para ordenar por fecha de modificación usando mergesort
    lista_archivos = os.listdir(ubicacion)
    lista_rutas = [os.path.join(ubicacion, archivo) for archivo in lista_archivos]
    lista_fechas_modificacion = [os.path.getmtime(archivo) for archivo in lista_rutas]
    actual = unidad.directorio_raiz
    actual.listar_archivos()

    def merge_sort(arr):
        if len(arr) > 1:
            mid = len(arr) // 2
            L = arr[:mid]
            R = arr[mid:]

            merge_sort(L)
            merge_sort(R)

            i = j = k = 0

            while i < len(L) and j < len(R):
                if L[i] < R[j]:
                    arr[k] = L[i]
                    i += 1
                else:
                    arr[k] = R[j]
                    j += 1
                k += 1

            while i < len(L):
                arr[k] = L[i]
                i += 1
                k += 1

            while j < len(R):
                arr[k] = R[j]
                j += 1
                k += 1

    merge_sort(lista_fechas_modificacion)

    if orden == 'ascendente':
        lista_fechas_modificacion_ordenadas = lista_fechas_modificacion
    elif orden == 'descendente':
        lista_fechas_modificacion_ordenadas = lista_fechas_modificacion[::-1]
    else:
        raise ValueError("El parámetro 'orden' debe ser 'ascendente' o 'descendente'")

    archivos_ordenados = [archivo for fecha, archivo in sorted(zip(lista_fechas_modificacion, lista_rutas))]
    return archivos_ordenados

unidad = Unidad('C', 'C:\\', 1000000, 100000)
ubicacion = 'C:\\'
orden = 'ascendente'
archivos_ordenados = dir_ordenar_por_fecha_modificación(unidad, ubicacion, orden)
for archivo in archivos_ordenados:
    print(archivo.nombre)


def dir_buscar_por_rango_y_extension(unidad, ubicacion, rango, extension, orden):
    actual = unidad.directorio_raiz
    actual.listar_archivos()
    # Lógica para buscar por rango y extensión usando shellsort
    lista_archivos = os.listdir(ubicacion)
    lista_rutas = [os.path.join(ubicacion, archivo) for archivo in lista_archivos]
    lista_fechas_modificacion = [os.path.getmtime(archivo) for archivo in lista_rutas]

    # Filtrar por rango de fechas
    fecha_minima = datetime.datetime.strptime(rango[0], "%Y-%m-%d")
    fecha_maxima = datetime.datetime.strptime(rango[1], "%Y-%m-%d")
    archivos_filtrados = [archivo for archivo, fecha in zip(lista_rutas, lista_fechas_modificacion) if fecha_minima <= datetime.datetime.fromtimestamp(fecha) <= fecha_maxima]

    # Filtrar por extensión
    archivos_filtrados = [archivo for archivo in archivos_filtrados if os.path.splitext(archivo)[1] == extension]

    # Implementación del algoritmo Shell Sort para ordenar las rutas de archivos filtradas
    def shell_sort(arr):
        n = len(arr)
        gap = n // 2
        while gap > 0:
            for i in range(gap, n):
                temp = arr[i]
                j = i
                while j >= gap and arr[j - gap] > temp:
                    arr[j] = arr[j - gap]
                    j -= gap
                arr[j] = temp
            gap //= 2

    shell_sort(archivos_filtrados)

    if orden == 'ascendente':
        archivos_ordenados = archivos_filtrados
    elif orden == 'descendente':
        archivos_ordenados = archivos_filtrados[::-1]
    else:
        raise ValueError("El parámetro 'orden' debe ser 'ascendente' o 'descendente'")

    return archivos_ordenados

unidad = 'C:'
ubicacion = 'C:\\Users\\Gabo Sandoval\\OneDrive\\Escritorio\\algoritmos2'
rango = ['2022-01-01', '2022-12-31']
extension = '.txt'
orden = 'ascendente'

archivos_ordenados = dir_buscar_por_rango_y_extension(unidad, ubicacion, rango, extension, orden)
print(archivos_ordenados)


def dir_filtrar_por_tamaño_y_extension(unidad, ubicacion, tamaño, operador, extension, orden):
    actual = unidad.directorio_raiz
    actual.listar_archivos()
    # Lógica para filtrar archivos por tamaño y extensión
    lista_archivos = os.listdir(ubicacion)
    lista_rutas = [os.path.join(ubicacion, archivo) for archivo in lista_archivos]
    archivos_filtrados = [archivo for archivo in lista_rutas if os.path.getsize(archivo) > tamaño and archivo.endswith(extension)]

    # Implementación del algoritmo Heap Sort para ordenar los archivos por tamaño
    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and arr[l] > arr[largest]:
            largest = l

        if r < n and arr[r] > arr[largest]:
            largest = r

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    def heap_sort(arr):
        n = len(arr)

        for i in range(n // 2 - 1, -1, -1):
            heapify(arr, n, i)

        for i in range(n - 1, 0, -1):
            arr[i], arr[0] = arr[0], arr[i]
            heapify(arr, i, 0)

    heap_sort(archivos_filtrados)

    if orden == 'ascendente':
        archivos_ordenados = archivos_filtrados
    elif orden == 'descendente':
        archivos_ordenados = archivos_filtrados[::-1]
    else:
        raise ValueError("El parámetro 'orden' debe ser 'ascendente' o 'descendente'")

    return archivos_ordenados

def dir_ordenar_por_fecha_creacion(unidad, ubicacion, orden):
    # Lógica para ordenar por fecha de creación usando algoritmo de ordenamiento específico
    lista_archivos = os.listdir(ubicacion)
    lista_rutas = [os.path.join(ubicacion, archivo) for archivo in lista_archivos]

    # Obtener la fecha de creación de cada archivo
    fechas_creacion = [datetime.datetime.fromtimestamp(os.path.getctime(archivo)) for archivo in lista_rutas]

    # Implementación del algoritmo Merge Sort para ordenar las rutas de archivos por fecha de creación
    def merge_sort(arr):
        if len(arr) > 1:
            mid = len(arr) // 2
            L = arr[:mid]
            R = arr[mid:]

            merge_sort(L)
            merge_sort(R)

            i = j = k = 0

            while i < len(L) and j < len(R):
                if L[i] < R[j]:
                    arr[k] = L[i]
                    i += 1
                else:
                    arr[k] = R[j]
                    j += 1
                k += 1

            while i < len(L):
                arr[k] = L[i]
                i += 1
                k += 1

            while j < len(R):
                arr[k] = R[j]
                j += 1
                k += 1

    merge_sort()