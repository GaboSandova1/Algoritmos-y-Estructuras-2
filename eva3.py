from datetime import datetime
import xml.etree.ElementTree as ET
import csv
import json
import pickle
import os
import datetime

# Clase para los ficheros
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

# Clase para las unidades
class Unidad:
    def _init_(self, ID, nombre, capacidadTotal, espacioDisponible, listaCarpetas, tipoUnidad):
        self.ID = ID
        self.nombre = nombre
        self.capacidadTotal = capacidadTotal
        self.espacioDisponible = espacioDisponible
        self.listaCarpetas = listaCarpetas
        self.tipoUnidad = tipoUnidad

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
def cargar_datos(nombre_archivo, formato):
    try:
        if formato == "xml":
            return cargar_desde_xml(nombre_archivo)
        elif formato == "csv":
            return cargar_desde_csv(nombre_archivo)
        elif formato == "json":
            return cargar_desde_json(nombre_archivo)
        elif formato == "serializado":
            return cargar_serializado(nombre_archivo)
        else:
            raise ValueError("Formato de archivo no válido")
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no existe")
    except Exception as e:
        print(f"Ocurrió un error al cargar los datos: {e}")
        return []

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
    pivot = arr[high][1]

    for j in range(low, high):
        if arr[j][1] <= pivot:
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

def dir_ordenar_por_tamaño(unidad, ubicacion, orden):
    factor_orden = 1 if orden == "ascendente" else -1
    quickSort(unidad, 0, len(unidad) - 1)
    if factor_orden == -1:
        unidad = unidad[::-1]
    return unidad

# Ubicación de los archivos
ubicacion_archivos = 'C:\\Users\\Gabo Sandoval\\OneDrive\\Escritorio\\algoritmos2'

# Listar archivos por tamaño
archivos = listar_archivos_por_tamaño(ubicacion_archivos)

# Ordenar archivos por tamaño usando QuickSort
archivos_ordenados = dir_ordenar_por_tamaño(archivos, ubicacion_archivos, "ascendente")

# Imprimir archivos ordenados
for archivo in archivos_ordenados:
    print(f"{archivo[0]} - {archivo[1]} bytes")


def dir_ordenar_por_fecha_modificación(unidad, ubicacion, orden):
    # Lógica para ordenar por fecha de modificación usando mergesort
    lista_archivos = os.listdir(ubicacion)
    lista_rutas = [os.path.join(ubicacion, archivo) for archivo in lista_archivos]
    lista_fechas_modificacion = [os.path.getmtime(archivo) for archivo in lista_rutas]

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

unidad = 'C:'
ubicacion = 'C:\\Users\\Gabo Sandoval\\OneDrive\\Escritorio\\algoritmos2'

orden = 'ascendente'

archivos_ordenados = dir_ordenar_por_fecha_modificación(unidad, ubicacion, orden)
print(archivos_ordenados)


def dir_buscar_por_rango_y_extension(unidad, ubicacion, rango, extension, orden):
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