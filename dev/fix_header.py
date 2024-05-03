import os
import pdb

"""Descubrimientos:
    1) Longitud de lineas en bytes:
        - SPU (20210730): [78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 0, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 0]
        - EAFIT (2022/04/13/): [78, 88, 78, 78, 78, 78, 78, 0, 65520, 8000, 65520, 8000, 0]
"""

def contar_bytes_por_linea(file_path):
    with open(file_path, 'rb') as file:
        contenido = file.read()  # Leer todo el archivo

    lineas = contenido.split(b'\r\n')  # Dividir en líneas usando CRLF como delimitador
    bytes_por_linea = [len(linea) for linea in lineas]  # Lista de la longitud de cada línea en bytes

    return bytes_por_linea


def modify_header(file_path):
    # Intenta abrir el archivo para leer y escribir en binario
    try:
        with open(file_path, 'rb+') as file:
            # Supongamos que el encabezado tiene un tamaño fijo de 1024 bytes
            pdb.set_trace()
            original_header = file.read(1024)
            
            # Aquí modificas el encabezado como necesites, esto es solo un ejemplo
            modified_header = original_header  # Cambia esto según lo que necesites arreglar

            # Regresa al inicio del archivo para sobreescribir el encabezado
            file.seek(0)
            file.write(modified_header)
            # No tocamos el resto del archivo, solo el encabezado
    except IOError as e:
        print(f"Ojo, hubo un problema con el archivo {file_path}: {e}")

def iterate_directories(root_directory):
    # Camina por todos los directorios y archivos empezando desde root_directory
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            # Construye el path completo al archivo
            file_path = os.path.join(root, file)
            # Modifica el encabezado del archivo
            modify_header(file_path)

        # Mensaje de confirmación que se procesó el directorio
        print(f"Hecho con: {dirs}")

# Aquí especificas el directorio raíz desde donde empezar a buscar archivos
root_dir = '/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/Dataset1/LiMon Raw Data cc/2022/' #EAFIT
# root_dir = '/home/medico_eafit/WORKSPACES/sebastian_carmona/REPOSITORIOS/LPP/signalsTest/Brazil/SPU/20210730/' #SPU


iterate_directories(root_dir)