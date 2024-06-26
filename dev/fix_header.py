import re
import os
import pdb
import numpy as np

"""Descubrimientos:
    1) Longitud de lineas en bytes (sin contar los dos bites de \\r\\n):
        - SPU (20210730): [78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 0, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 16000, 0]
        - EAFIT (2022/04/13/): [78, 88, 78, 78, 78, 78, 78, 0, 65520, 8000, 65520, 8000, 0], ¿La longitud de las líneas correspindiente a los canal es diferente?
        - El problema de las coordenadas no es que no se leean correctamente, si no que aumenta la longitud de bytes de la línea. Aparentemento, esto no es un problema
        - La cantidad de bit y los disparos por canal no se leen bien, se pierded byes al inicio del dato.
        - El ángulo Cenital no se gaurda bien, por ejemplo: [90.0,0.0,0.0,0.0,0.0,...]
        - Duda sobre la lectura de la polarización, ya que en el conjunto de prueba se tienen 11 vaslores pero son 12 DS y en e EAFIT se tiene 3 valorers pero son 4 canales
        """     

def contar_bytes_por_linea(file_path):
    with open(file_path, 'rb') as file:
        contenido = file.read()  # Leer todo el archivo

    lineas = contenido.split(b'\r\n')  # Dividir en líneas usando CRLF como delimitador
    bytes_por_linea = [len(linea) for linea in lineas]  # Lista de la longitud de cada línea en bytes

    return bytes_por_linea

def fix_coodinates(header):

    lines = re.split("(\r\n)", header)
    lines = [lines[i] + lines[i + 1] for i in range(0, len(lines) - 1, 2)]
    
    
    # Patron de longitud y latitud a buscar
    patron = r"-?\d{3,4}\.\d+"

    longitude, latitude = re.findall(patron, lines[1])

    fixed_header = header.replace(longitude, f"{float(longitude):06.1f}")
    fixed_header = fixed_header.replace(latitude, f"{float(latitude):06.1f}")

    return fixed_header

def es_archivo_binario(ruta):
    # Obtener la extensión del archivo
    _, extension = os.path.splitext(ruta)
    
    # Verificar si la extensión es numérica
    if extension and extension[1:].isdigit():
        return True

    return False


def fix_wavelength(header, wavelength:str = "00532", fix_pol:bool =False):

    pol = {'s': 'l',
           'p': 's'}

    # Función para realizar el reemplazo
    def replace_match(match, fix_pol=False):
        number = wavelength  # Nuevo número que quieres usar
        suffix = match.group().split('.')[-1]  # Conservar el sufijo original (.p o .s)
        if fix_pol:
            return f"{number}.{pol[suffix]}" # No corregir
        else:
            return f"{number}.{suffix}"


    lines = re.split("(\r\n)", header)
    lines = [lines[i] + lines[i + 1] for i in range(0, len(lines) - 1, 2)]
    
    
    # Patron de longitud y latitud a buscar
    patron = r"\d{5}\.[ps]"

    # Lista para guardar las cadenas modificadas
    modified_lines = []

    # Iterar sobre cada línea en la lista
    for line in lines:
        # Reemplazar todas las coincidencias en la línea actual

        modified_line = re.sub(patron, replace_match, line)
        # Agregar la línea modificada a la lista de líneas modificadas
        modified_lines.append(modified_line)

    # pdb.set_trace()
    return ''.join(modified_lines)

    #return fixed_header

def modify_header(file_path):
    # Intenta abrir el archivo para leer y escribir en binario
    if es_archivo_binario(file_path):
        print(f'Procesando {file_path}')
        try:
            with open(file_path, 'rb+') as file:
                # Supongamos que el encabezado tiene un tamaño fijo de 80 bytes
                File = file.read()
                file.seek(0)
                header_lines_len = contar_bytes_por_linea(file_path)
                header_lines = header_lines_len.index(0)
                header_bytes = (np.array(header_lines_len[:header_lines]) + 2)
                
                original_header = file.read(header_bytes.sum())
                original_header_str = original_header.decode('utf-8')
                
                # Aquí modificas el encabezado como necesites, esto es solo un ejemplo
                modified_header = fix_coodinates(original_header_str) # Cambia esto según lo que necesites arreglar
                modified_header = fix_wavelength(modified_header, fix_pol=False)
                # pdb.set_trace()
                #####
                
                modified_header = modified_header.encode('utf-8')
                modified_header_lines_len = [len(linea) for linea in modified_header.split(b'\r\n')] 
                modified_header_lines = modified_header_lines_len.index(0)
                # modified_header_bytes = (np.array(modified_header_lines_len[:modified_header_lines]) + 2)


                # Regresa al inicio del archivo para sobreescribir el encabezado

                new_file = b'\r\n'.join(modified_header.split(b'\r\n') + File.split(b'\r\n')[header_lines+1:])

                file.seek(0)
                file.write(new_file)
                file.truncate(len(new_file))

        except IOError as e:
            print(f"Hubo un problema con el archivo {file_path}: {e}")

def iterate_directories(root_directory):
    # Camina por todos los directorios y archivos empezando desde root_directory
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            # Construye el path completo al archivo
            file_path = os.path.join(root, file)
            # Modifica el encabezado del archivo
            modify_header(file_path)

        # Mensaje de confirmación que se procesó el directorio
        # print(f"Hecho con: {dirs}")

# Aquí especificas el directorio raíz desde donde empezar a buscar archivos
root_dir = '/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/Dataset1/' #EAFIT
# root_dir = '/home/medico_eafit/WORKSPACES/sebastian_carmona/REPOSITORIOS/LPP/signalsTest/Brazil/SPU/20210730/' #SPU


iterate_directories(root_dir)

