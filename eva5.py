import datetime  # Importamos el módulo datetime para trabajar con fechas y horas
import logging  # Importamos el módulo logging para registrar información
from linked_l import Pila, Cola

import helper
import configparser

# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

# Leemos la configuración del archivo config.ini utilizando la función read_config() del módulo helper
config = helper.read_config()
logger = logging.getLogger("mylogger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(config["Logger"]["logfilepath"])

# Configuramos el logger para registrar información en un archivo de registro
# Establecemos el nivel de registro en INFO y especificamos el formato del registro
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Definición de la función guardarObjeto() que se utiliza para guardar objetos utilizando el módulo pickle
def guardarObjeto(obj):
    try:
        with open("data.pickle", "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)
        logger.error("Exception occurred", exc_info=True)

# Definición de la función cargarObjeto() que se utiliza para cargar objetos utilizando el módulo pickle
# Captura excepciones y registra errores utilizando el logger
def cargarObjeto(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)
        logger.error("Exception occurred", exc_info=True)

# Definición de la clase Estructura que controla la estructura de directorios y archivos
class Estructura():
    def __init__(self, path) -> None:
        self.path = path  # Ruta del directorio actual
        self.cDir = Directorio("C:", self.path)  # Directorio raíz
        self.pathlist = [self.cDir]  # Lista de directorios
        self.currentDir = self.cDir  # Directorio actual
        self.pathlist = cargarObjeto("data.pickle")  # Carga la lista de directorios desde un archivo pickle
        while True:
            try:
                guardarObjeto(self.pathlist)  # Guarda la lista de directorios en un archivo pickle
                self.currentDir = self.pathlist[-1]  # Actualiza el directorio actual al último de la lista
                self.path = self.currentDir.path  # Actualiza la ruta del directorio actual
                orden = input(self.currentDir.path + "> ")  # Solicita una orden al usuario
                logger.info(orden)  # Registra la orden en el log
                if orden[:2] == "cd":  # Si la orden es 'cd', cambia de directorio
                    self.changeDir(orden[2:])
                elif orden[:5] == "mkdir":  # Si la orden es 'mkdir', crea un nuevo directorio
                    check = 0
                    for i in self.currentDir.directorios:
                        if i.nombre == orden[6:]:
                            check = 1
                    if check == 0:
                        self.currentDir.directorios.append(self.mkDir(orden[6:]))
                    else:
                        print('Este directorio ya existe con el nombre "' + orden[6:] + '"')
                elif orden[:3] == "dir":  # Si la orden es 'dir', lista los directorios
                    self.listDir(self.currentDir)
                elif orden[:5] == "rmdir":  # Si la orden es 'rmdir', elimina un directorio
                    self.rmDir(orden[6:])
                elif orden[:6] == "rename":  # Si la orden es 'rename', renombra un directorio
                    try:
                        self.rename(orden.split(" ")[1], orden.split(" ")[2])
                    except IndexError:
                        print("Por favor, indique el viejo y el nuevo nombre.")
                        logger.exception("Exception occurred")
                elif orden[:4] == "type":  # Si la orden es 'create', crea un nuevo archivo
                    check = 0
                    for i in self.currentDir.directorios:
                        if i.tipo != "<DIR>":
                            if i.nombre == orden[7:]:
                                check = 1
                    if check == 0:
                        self.create(orden[7:])    
                    else:
                        print('Este fichero ya existe, con nombre "' + orden[6:] + '"')
                elif orden[:6] == "remove":  # Si la orden es 'remove', elimina un archivo
                    self.remove(orden[7:])
                elif orden[:4] == "open":  # Si la orden es 'type', abre un archivo
                    self.open(orden[5:])
                    input()
                elif orden[:3] == "log":  # Si la orden es 'log', muestra el log
                    file = open(config["AppSettings"]["pathlog"], "r")
                    print(file.read())
                elif orden[:9] == "clear log":  # Si la orden es 'clear log', limpia el log
                    file = open(config["AppSettings"]["pathlog"], "w")
                    print(file.truncate(0))
                elif orden[:6] == "config":  # Si la orden es 'config', muestra la configuración
                    file = open(config["AppSettings"]["pathconfig"], "r")
                    print(file.read())
                elif orden[:4] == "help":  # Si la orden es 'help', muestra la ayuda
                    file = open(config["AppSettings"]["pathhelp"], "r")
                    print(file.read())
                else:
                    print('"'+ orden + '" ' + 'No se reconoce como un comando interno o externo, programa o archivo por lotes ejecutable. \n')
            except Exception as e:
                logger.exception("Exception occurred")  # Registra la excepción en el log

    #******************DIRECTORIOS******************
                
    def changeDir(self, orden):
        try:
            nombre = orden[1:]
            if orden == "..": # Si la orden es "..", sube un nivel en el directorio
                if len(self.pathlist) > 1:
                    self.pathlist.pop() # Elimina el último directorio de la lista de directorios
        
                
            elif self.currentDir.directorios == []: # Si no hay directorios en el directorio actual
                print('No existe ningun directorio con el nombre "' + nombre + '"')
                 # Imprime un mensaje de error
            else: # Si hay directorios en el directorio actual
                check = 0
                for i in self.currentDir.directorios: # Recorre los directorios en el directorio actual
                    if i.nombre == nombre:  #Si encuentra un directorio con el nombre indicado
                        self.pathlist.append(i)#Añade el directorio a la lista de directorios
                        check = 1
                if check == 0:
                    print('No existe ningun directorio con el nombre "' + nombre + '"')# Si no encuentra un directorio con el nombre indicado
        except Exception as e:  # Imprime un mensaje de error
            logger.exception("Exception occurred")# Registra la excepción en el log
                    
    def mkDir(self, nombre):  # Crea un nuevo directorio
     try:
        return Directorio(nombre, self.path + "\\" + nombre)  # Retorna una nueva instancia de la clase Directorio
     except Exception as e:
        logger.exception("Exception occurred")  # Registra la excepción en el log
    def listDir(self, dir):  # Lista los directorios en el directorio actual
     try:
        for i in dir.directorios:  # Recorre los directorios en el directorio actual
            print(("{:11} {:11} {:8} {:15}").format(i.fCreacion, i.hCreacion, i.tipo, i.nombre))  # Imprime los detalles de cada directorio
     except Exception as e:
        logger.exception("Exception occurred")  # Registra la excepción en el log

    def rmDir(self, dir):  # Elimina un directorio
     try:
        ch = 0
        for i in self.currentDir.directorios:  # Recorre los directorios en el directorio actual
            if dir == i.nombre:  # Si encuentra un directorio con el nombre indicado
                ch = 1
                self.currentDir.directorios.remove(i)  # Elimina el directorio de la lista de directorios
        if ch == 0:  # Si no encuentra un directorio con el nombre indicado
            print('No existe ningun directorio con el nombre "' + dir + '"')  # Imprime un mensaje de error

     except Exception as e:
        logger.exception("Exception occurred")  # Registra la excepción en el log

    def rename(self, old, new):  # Renombra un directorio
     try:
        if self.currentDir.directorios == []:  # Si no hay directorios en el directorio actual
            print('No existe ningun directorio con el nombre "' + old + '"')  # Imprime un mensaje de error

        for i in self.currentDir.directorios:  # Recorre los directorios en el directorio actual
            if old == i.nombre:  # Si encuentra un directorio con el nombre antiguo
                setattr(i, "nombre", new)  # Cambia el nombre del directorio al nombre nuevo
                setattr(i, "path", self.path + "\\" + new)  # Actualiza la ruta del directorio
            else:
                print('No existe ningun directorio con el nombre "' + old + '"')  # Imprime un mensaje de error
     except Exception as e:
        logger.exception("Exception occurred")  # Registra la excepción en el log

#**********************DIRECTORIOS*********************
    def create(self, args):  # Crea un nuevo archivo
     if len(args.split(" ")) == 1:  # Si solo se proporciona el nombre del archivo
        try:
            self.currentDir.directorios.append(Fichero(args, args.split(".")[1]))  # Añade un nuevo archivo a la lista de directorios
        except IndexError:
            print("Por favor indique una extension del archivo")  # Imprime un mensaje de error si no se proporciona una extensión de archivo
     elif len(args.split(" ")) > 1:  # Si se proporciona el nombre del archivo y contenido
        self.currentDir.directorios.append(Fichero(args.split(" ")[0], args.split(" ")[0].split(".")[1]))  # Añade un nuevo archivo a la lista de directorios
        setattr(self.currentDir.directorios[-1], "contenido", args.split(" ", 1)[1])  # Añade el contenido al archivo

    def remove(self, arg):  # Elimina un archivo
     if arg == "":  # Si no se proporciona el nombre del archivo
        print("Por favor, indique el nombre del archivo")  # Imprime un mensaje de error
     else:
        check = 0
        for i in self.currentDir.directorios:  # Recorre los directorios en el directorio actual
            if i.tipo != "<DIR>":  # Si el directorio es en realidad un archivo
                if arg == i.nombre:  # Si encuentra un archivo con el nombre indicado
                    self.currentDir.directorios.remove(i)  # Elimina el archivo de la lista de directorios
                    check = 1
        if check == 0:  # Si no encuentra un archivo con el nombre indicado
            print('No existe ningun archivo con el nombre "' + arg + '"')  # Imprime un mensaje de error

    def open(self, arg):  # Abre un archivo
     if arg == "":  # Si no se proporciona el nombre del archivo
        print("Por favor, indique el nombre del archivo")  # Imprime un mensaje de error
     else:
        check = 0
        for i in self.currentDir.directorios:  # Recorre los directorios en el directorio actual
            if i.tipo != "<DIR>":  # Si el directorio es en realidad un archivo
                if i.nombre == arg:  # Si encuentra un archivo con el nombre indicado
                    print(i.contenido)  # Imprime el contenido del archivo
                    check = 1
        if check == 0:  # Si no encuentra un archivo con el nombre indicado
            print('No existe un archivo con el nombre "' + arg + '"')  # Imprime un mensaje de error


    #******************FICHEROS******************

class Directorio():
    def __init__(self, nombre, path) -> None:
        self.nombre = nombre  # Nombre del directorio
        self.path = path  # Ruta del directorio
        self.fCreacion = datetime.datetime.now().strftime("%x")  # Fecha de creación del directorio
        self.hCreacion = datetime.datetime.now().strftime("%X")  # Hora de creación del directorio
        self.tipo = "<DIR>"  # Tipo de objeto (en este caso, un directorio)
        self.directorios = []  # Lista de directorios dentro de este directorio

class Fichero():
    def __init__(self, nombre, tipo) -> None:
        self.nombre = nombre  # Nombre del archivo
        self.tipo = tipo  # Extensión del archivo
        self.contenido = ""  # Contenido del archivo
        self.fCreacion = datetime.datetime.now().strftime("%x")  # Fecha de creación del archivo
        self.hCreacion = datetime.datetime.now().strftime("%X")  # Hora de creación del archivo

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.siguiente = None


class Pila:
    def __init__(self):
        self.cabeza = None

    def apilar(self, valor):
        nuevo_nodo = Nodo(valor)

        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            nuevo_nodo.siguiente = self.cabeza
            self.cabeza = nuevo_nodo

    def desapilar(self):
        if self.cabeza is None:
            return None

        nodo_desapilado = self.cabeza
        self.cabeza = self.cabeza.siguiente
        return nodo_desapilado.valor

    def esta_vacia(self):
        return self.cabeza is None


class Cola:
    def __init__(self):
        self.cabeza = None
        self.cola = None

    def encolar(self, valor):
        nuevo_nodo = Nodo(valor)

        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo

    def desencolar(self):
        if self.cabeza is None:
            return None

        nodo_desencolado = self.cabeza
        self.cabeza = self.cabeza.siguiente

        if self.cabeza is None:
            self.cola = None

        return nodo_desencolado.valor

    def esta_vacia(self):
        return self.cabeza is None


def main():
    lista = [1, 2, 3, 4, 5]
    
    # Convertir lista enlazada en una pila
    pila = Pila()
    for elemento in lista:
        pila.apilar(elemento)

    # Desapilar elementos de la pila
    print("Pila:")
    while not pila.esta_vacia():
        elemento = pila.desapilar()
        print(elemento)

    # Convertir lista enlazada en una cola
    cola = Cola()
    for elemento in lista:
        cola.encolar(elemento)

    # Desencolar elementos de la cola
    print("Cola:")
    while not cola.esta_vacia():
        elemento = cola.desencolar()
        print(elemento)


if __name__ == "__main__":
    main()

path = config["AppSettings"]["path"]  # Ruta del directorio raíz
usename = config["AppSettings"]["username"]  # Nombre de usuario
main = Estructura(path)  # Crea una nueva instancia de la clase Estructura

class NodoArbol:
    def __init__(self, dato):
        # Constructor para inicializar un nodo con un dato dado.
        self.dato = dato
        self.izquierda = None
        self.derecha = None

class ArbolBinario:
    def __init__(self):
        # Constructor para inicializar un árbol binario vacío sin raíz.
        self.raiz = None

    def agregar(self, dato):
        # Agrega un nuevo nodo con el dato dado al árbol.
        if self.raiz is None:
            self.raiz = NodoArbol(dato)
        else:
            self._agregar_recursivo(self.raiz, dato)

    def _agregar_recursivo(self, nodo, nuevo_dato):
        # Método privado recursivo para agregar un nodo al árbol.
        if nuevo_dato < nodo.dato:
            if nodo.izquierda is None:
                nodo.izquierda = NodoArbol(nuevo_dato)
            else:
                self._agregar_recursivo(nodo.izquierda, nuevo_dato)
        else:
            if nodo.derecha is None:
                nodo.derecha = NodoArbol(nuevo_dato)
            else:
                self._agregar_recursivo(nodo.derecha, nuevo_dato)

    def mostrar(self):
        # Muestra todo el árbol utilizando un método recursivo auxiliar.
        self._mostrar_recursivo(self.raiz, 0)

    def _mostrar_recursivo(self, nodo, nivel):
        # Método privado recursivo para mostrar el árbol de forma rotada.
        if nodo is not None:
            self._mostrar_recursivo(nodo.derecha, nivel + 1)
            print("  00000     " * nivel + str(nodo.dato))
            self._mostrar_recursivo(nodo.izquierda, nivel + 1)

    def buscar(self, dato):
        # Inicia la búsqueda de un dato específico en el árbol.
        return self._buscar_recursivo(self.raiz, dato)

    def _buscar_recursivo(self, nodo, dato):
        # Método privado recursivo para buscar un dato en el árbol.
        if nodo is None or nodo.dato == dato:
            return nodo
        if dato < nodo.dato:
            return self._buscar_recursivo(nodo.izquierda, dato)
        return self._buscar_recursivo(nodo.derecha, dato)

    def eliminar(self, dato):
        # Inicia la eliminación de un nodo con el dato especificado.
        self.raiz = self._eliminar_recursivo(self.raiz, dato)

    def _eliminar_recursivo(self, nodo, dato):
        # Método privado recursivo para eliminar un nodo con el dato dado.
        if nodo is None:
            return nodo
        if dato < nodo.dato:
            nodo.izquierda = self._eliminar_recursivo(nodo.izquierda, dato)
        elif dato > nodo.dato:
            nodo.derecha = self._eliminar_recursivo(nodo.derecha, dato)
        else:
            if nodo.izquierda is None:
                return nodo.derecha
            elif nodo.derecha is None:
                return nodo.izquierda
            nodo.dato = self._encontrar_minimo(nodo.derecha)
            nodo.derecha = self._eliminar_recursivo(nodo.derecha, nodo.dato)
        return nodo

    def _encontrar_minimo(self, nodo):
        # Encuentra el valor mínimo en un subárbol dado.
        actual = nodo
        while actual.izquierda is not None:
            actual = actual.izquierda
        return actual.dato

    def recorrer_preorden(self):
        # Realiza un recorrido en preorden y devuelve una lista de nodos visitados.
        resultado = []
        self._preorden(self.raiz, resultado)
        return resultado

    def _preorden(self, nodo, resultado):
        # Método auxiliar para recorrido en preorden.
        if nodo is not None:
            resultado.append(nodo.dato)
            self._preorden(nodo.izquierda, resultado)
            self._preorden(nodo.derecha, resultado)

    def recorrer_inorden(self):
        # Realiza un recorrido en inorden y devuelve una lista de nodos visitados.
        resultado = []
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo, resultado):
        # Método auxiliar para recorrido en inorden.
        if nodo is not None:
            self._inorden(nodo.izquierda, resultado)
            resultado.append(nodo.dato)
            self._inorden(nodo.derecha, resultado)

    def recorrer_postorden(self):
        # Realiza un recorrido en postorden y devuelve una lista de nodos visitados.
        resultado = []
        self._postorden(self.raiz, resultado)
        return resultado

    def _postorden(self, nodo, resultado):
        # Método auxiliar para recorrido en postorden.
        if nodo is not None:
            self._postorden(nodo.izquierda, resultado)
            self._postorden(nodo.derecha, resultado)
            resultado.append(nodo.dato)

# Llamada a la ejecución de la clase
arbol = ArbolBinario()