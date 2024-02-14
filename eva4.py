from datetime import datetime
from pprint import pprint
import xml.etree.ElementTree as ET
import csv
import json
import pickle
import os
import datetime

class SistemaArchivos:
    def __init__(self):
        self.directorios = {
            '/': {'nombre': '/', 'padre': None, 'subdirectorios': {}, 'archivos': {}}
        }
        self.ubicacion_actual = '/'

    def cambiarDirectorio(self, ruta):
        if ruta == '..':
            if self.ubicacion_actual != '/':
                self.ubicacion_actual = self.directorios[self.ubicacion_actual]['padre']
        else:
            if ruta in self.directorios[self.ubicacion_actual]['subdirectorios']:
                self.ubicacion_actual = self.directorios[self.ubicacion_actual]['subdirectorios'][ruta]
            elif os.path.isdir(ruta):
                self.agregarDirectorio(ruta)
                self.directorios[self.ubicacion_actual]['subdirectorios'][os.path.basename(ruta)] = self.directorios[ruta]
                self.ubicacion_actual = self.directorios[ruta]
            else:
                raise FileNotFoundError(f"El directorio '{ruta}' no existe")

    def agregarDirectorio(self, ruta):
        if ruta not in self.directorios[self.ubicacion_actual]['subdirectorios']:
            nuevo_directorio = {'nombre': os.path.basename(ruta), 'padre': self.ubicacion_actual, 'subdirectorios': {}, 'archivos': {}}
            self.directorios[self.ubicacion_actual]['subdirectorios'][os.path.basename(ruta)] = nuevo_directorio
            self.directorios[ruta] = nuevo_directorio

    def getRutaAbsoluta(self, ruta):
        if ruta[0] == '/':
            return ruta
        else:
            return os.path.join(self.getRutaAbsoluta(self.ubicacion_actual), ruta)

# Clase para los ficheros
class Fichero:
    def __init__(self, ID, nombre, tamaño, extensión, fechaCreación, fechaModificación, contenido):
        self.ID = ID
        self.nombre = nombre
        self.tamaño = tamaño
        self.extensión = extensión
        self.fechaCreación = fechaCreación
        self.fechaModificación = fechaModificación
        self.contenido = contenido

    def __str__(self):
        return f'Fichero (ID={self.ID}), nombre="{self.nombre}", tamaño={self.tamaño}, extensión="{self.extensión}", fecha_creación={self.fecha_creación}, fecha_modificación={self.fecha_modificación})'

# Clase para las carpetas
class Carpeta:
    def __init__(self, ID, nombre, listaFicheros, fechaCreación, listaCarpetas):
        self.ID = ID
        self.nombre = nombre
        self.listaFicheros = listaFicheros
        self.fechaCreación = fechaCreación
        self.listaCarpetas = listaCarpetas

        def __str__(self):
            return f'Carpeta(ID={self.ID}, nombre="{self.nombre}", lista_ficheros={self.lista_ficheros}, fecha_creación={self.fecha_creación}, lista_carpetas={self.lista_carpetas})'
    
# Clase para las unidades
class Unidad:
    def __init__(self, ID, nombre, capacidadTotal, espacioDisponible, listaCarpetas, tipoUnidad):
        self.ID = ID
        self.nombre = nombre
        self.capacidadTotal = capacidadTotal
        self.espacioDisponible = espacioDisponible
        self.listaCarpetas = listaCarpetas
        self.tipoUnidad = tipoUnidad

# Clase para los comandos
class Comando:
    def __init__(self, ID, nombreComando, descripcion, rolRequerido, funcion=None):
        self.ID = ID
        self.nombreComando = nombreComando
        self.descripcion = descripcion
        self.rolRequerido = rolRequerido
        self.funcion = funcion

    def llamar_funcion(self, argumentos):
        self.funcion(argumentos)

class ComandoCd(Comando):
    def __init__(self, ID, nombreComando, descripcion, rolRequerido, sistema_archivos):
        super().__init__(ID, nombreComando, descripcion, rolRequerido)
        self.sistema_archivos = sistema_archivos
        self.funcion = self.cambiar_directorio

    def cambiar_directorio(self, sistema_archivos, args):
        ruta = args[0]
        sistema_archivos.cambiarDirectorio(ruta)

class ComandoMkdir(Comando):
    def __init__(self, ID, nombreComando, descripcion, rolRequerido, sistema_archivos):
        super().__init__(ID, nombreComando, descripcion, rolRequerido)
        self.sistema_archivos = sistema_archivos

    def ejecutar_comando(self, argumentos):
        if len(argumentos) < 1:
            print("Se necesita especificar el nombre de la nueva carpeta")
            return

        nueva_carpeta = argumentos[0]
        ruta_destino = self.sistema_archivos.getRutaAbsoluta(nueva_carpeta) if nueva_carpeta[0] != '/' else nueva_carpeta

        try:
            os.mkdir(ruta_destino)
            print(f"Se ha creado la carpeta '{nueva_carpeta}'")
            self.sistema_archivos.agregarDirectorio(ruta_destino)
            self.comando_cd = ComandoCd(4, "cd", "Cambia el directorio actual", "usuario", self.sistema_archivos)
            return self.comando_cd.cambiar_directorio  # Devuelve la función self.comando_cd.cambiar_directorio
        except FileExistsError:
            print(f"La carpeta '{nueva_carpeta}' ya existe")
        except Exception as e:
            print(f"Ocurrió un error al crear la carpeta: {e}")

    def cambiar_directorio(self, args):
        self.comando_cd.cambiar_directorio(self.sistema_archivos, args)

class ComandoRmdir(Comando):
    def __init__(self, ID, nombreComando, descripcion, rolRequerido, sistema_archivos):
        super().__init__(ID, nombreComando, descripcion, rolRequerido)
        self.sistema_archivos = sistema_archivos
        self.funcion = self.ejecutar_comando

    def ejecutar_comando(self, argumentos):
        if len(argumentos) < 1:
            print("Se necesita especificar el nombre de la carpeta a eliminar")
            return

        ruta_carpeta = argumentos[0]
        ruta_carpeta_absoluta = self.sistema_archivos.getRutaAbsoluta(ruta_carpeta) if ruta_carpeta[0] != '/' else ruta_carpeta

        try:
            os.rmdir(ruta_carpeta_absoluta)
            print(f"Se ha eliminado la carpeta '{ruta_carpeta}'")
            self.sistema_archivos.eliminarDirectorio(ruta_carpeta_absoluta)
        except FileNotFoundError:
            print(f"La carpeta '{ruta_carpeta}' no existe")
        except OSError as e:
            print(f"Ocurrió un error al eliminar la carpeta: {e}")

sistema_archivos = SistemaArchivos()

class ComandoEjecutor:
    def __init__(self, comandos, sistema_archivos):
        self.comandos = comandos
        self.sistema_archivos = sistema_archivos

    def ejecutar_comando(self, comando_id, argumentos):
        comando = next((comando for comando in self.comandos if comando.ID == comando_id), None)
        if comando:
            comando.funcion(argumentos)
        else:
            print(f"No se encontró el comando con ID {comando_id}")

sistema_archivos = SistemaArchivos()

comandos = [
    ComandoMkdir(1, "mkdir", "Crea una nueva carpeta", "usuario"),
    ComandoCd(2, "cd", "Cambia el directorio actual", "usuario", ComandoCd.cambiar_directorio),
    ComandoRmdir(3, "rmdir", "Elimina una carpeta vacia", "usuario", ComandoRmdir.ejecutar_comando)
]

comando_ejecutor = ComandoEjecutor(comandos, sistema_archivos)

comando_ejecutor.ejecutar_comando(1, ["nueva_carpeta"])

comando_ejecutor.ejecutar_comando(2, ["/ruta/al/directorio"])

comando_ejecutor.ejecutar_comando(3, ["ruta_carpeta"])


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

def dir_ordenar_por_fecha_creacion(unidad, ubicacion, fechas_creacion, orden):
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

    merge_sort(lista_rutas)

    
    
ubicacion_archivos = 'C:\\Users\\Gabo Sandoval\\OneDrive\\algoritmos2'
pprint(dir_buscar_por_rango_y_extension('C:', ubicacion_archivos, ['2022-01-01', '2022-12-31'], '.txt', 'ascendente'))

""""""