import random
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

# Importa los diccionarios de palabras y vectores desde los archivos
from matriz_palabras_vectores_1_1 import palabras_vectores as vectores_1_1
from matriz_palabras_vectores_1_2 import palabras_vectores as vectores_1_2
from matriz_palabras_vectores_1_3 import palabras_vectores as vectores_1_3
from matriz_palabras_vectores_1_4 import palabras_vectores as vectores_1_4

#from matriz_palabras_vectores_2_1 import palabras_vectores as vectores_2_1
#from matriz_palabras_vectores_2_2 import palabras_vectores as vectores_2_2
#from matriz_palabras_vectores_2_3 import palabras_vectores as vectores_2_3
#from matriz_palabras_vectores_2_4 import palabras_vectores as vectores_2_4

#from matriz_palabras_vectores_3_1 import palabras_vectores as vectores_3_1
#from matriz_palabras_vectores_3_2 import palabras_vectores as vectores_3_2
#from matriz_palabras_vectores_3_3 import palabras_vectores as vectores_3_3
#from matriz_palabras_vectores_3_4 import palabras_vectores as vectores_3_4

#from matriz_palabras_vectores_4_1 import palabras_vectores as vectores_4_1
#from matriz_palabras_vectores_4_2 import palabras_vectores as vectores_4_2
#from matriz_palabras_vectores_4_3 import palabras_vectores as vectores_4_3
#from matriz_palabras_vectores_4_4 import palabras_vectores as vectores_4_4

# Combina los diccionarios en uno solo
palabras_vectores = {**vectores_1_1, **vectores_1_2, **vectores_1_3, **vectores_1_4}

app = Flask(__name__)

# Cargar palabras comunes desde el archivo palabras_filtradas.txt
def cargar_palabras_comunes(ruta_archivo):
    with open(ruta_archivo, 'r') as f:
        contenido = f.read()
        # Convertir el contenido a una lista de Python
        palabras_comunes = eval(contenido)  # eval convierte el string a lista
    return palabras_comunes

# Cargar palabras comunes
palabras_comunes = cargar_palabras_comunes('palabras_filtradas.txt')

# Inicializar la palabra secreta y las palabras cercanas
palabra_secreta = random.choice(palabras_comunes)
palabras_usuario = []  # Lista para almacenar palabras introducidas por el usuario
distancias_usuario = []  # Lista para almacenar las distancias de las palabras del usuario

def calcular_similitud(v1, v2):
    """Calcula la similitud de coseno entre dos vectores."""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def filtrar_palabras_cercanas(palabra_secreta, palabras_candidatas):
    """Filtra las palabras cercanas, excluyendo la palabra secreta y sus primeras 5 letras."""
    palabras_filtradas = []
    for palabra in palabras_candidatas:
        if palabra != palabra_secreta and not palabra.startswith(palabra_secreta[:5]):
            palabras_filtradas.append(palabra)
        if len(palabras_filtradas) >= 5:
            break
    return palabras_filtradas

def obtener_palabras_cercanas(palabra_secreta):
    """Obtiene palabras cercanas a la palabra secreta basándose en los vectores."""
    palabra_secreta_vector = palabras_vectores[palabra_secreta]
    distancias = []

    for palabra, vector in palabras_vectores.items():
        if palabra != palabra_secreta:
            similitud = calcular_similitud(palabra_secreta_vector, vector)
            distancia = 1 - similitud  # La distancia es 1 menos la similitud
            distancias.append((palabra, distancia))

    # Ordenamos por la distancia y tomamos las 100 más cercanas
    distancias_ordenadas = sorted(distancias, key=lambda x: x[1])[:100]
    palabras_cercanas = [palabra for palabra, _ in distancias_ordenadas]

    return filtrar_palabras_cercanas(palabra_secreta, palabras_cercanas)

def simular_entrada_palabras_cercanas():
    """Simula la entrada de palabras cercanas para iniciar el juego."""
    global palabras_usuario, distancias_usuario
    palabras_cercanas_simuladas = obtener_palabras_cercanas(palabra_secreta)

    for palabra in palabras_cercanas_simuladas:
        similitud = calcular_similitud(palabras_vectores[palabra], palabras_vectores[palabra_secreta])
        distancia = 1 - similitud  # Calcular la "distancia"
        palabras_usuario.insert(0, palabra)  # Añadir la nueva palabra al principio de la lista de usuario
        distancias_usuario.insert(0, distancia)  # Almacenar la distancia al principio de la lista

@app.route('/', methods=['GET', 'POST'])
def index():
    global palabra_secreta, palabras_usuario, distancias_usuario

    # Simular la entrada de palabras cercanas al inicio
    if not palabras_usuario:  # Solo simula la entrada si no hay palabras del usuario
        simular_entrada_palabras_cercanas()

    if request.method == 'POST':
        nueva_palabra = request.form.get('palabra')
        
        # Si la nueva palabra es válida, no es la palabra secreta y no está ya en la lista, añadirla a las palabras del usuario
        if nueva_palabra in palabras_vectores and nueva_palabra not in palabras_usuario:
            similitud = calcular_similitud(palabras_vectores[nueva_palabra], palabras_vectores[palabra_secreta])
            distancia = 1 - similitud  # Calcular la "distancia"
            palabras_usuario.append(nueva_palabra)  # Añadir la nueva palabra a la lista de usuario
            distancias_usuario.append(distancia)  # Almacenar la distancia
    
    # Manejar la solicitud de nuevo juego
    if request.method == 'POST' and 'new_game' in request.form:
        palabra_secreta = random.choice(palabras_comunes)
        palabras_usuario = []
        distancias_usuario = []
        simular_entrada_palabras_cercanas()

    return render_template('index.html', palabra_secreta=palabra_secreta, palabras_cercanas=[], palabras_usuario=palabras_usuario, distancias_usuario=distancias_usuario)

if __name__ == '__main__':
    app.run(debug=True)
