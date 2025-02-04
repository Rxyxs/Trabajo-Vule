# Trabajo-Vule
Trabajo para consolidar datos para empresa de buses

# Plantilla Interactiva para Consolidación de Datos
### Por Pablo Reyes

## Propósito General del Código
El propósito es crear una herramienta automatizada para procesar y consolidar múltiples archivos Excel que contengan datos. 
Permite:
•	Normalizar datos importantes (como horas y patentes).
•	Eliminar información irrelevante.
•	Generar un archivo consolidado, que esté listo para análisis o reportes.

## ¿Qué es el PATH?
•	El PATH es una lista de ubicaciones en tu computadora donde el sistema operativo busca los programas que intentas ejecutar.

# Requisitos Técnicos 
•	Versión de Python Recomendado:
o	Python 3.8 o 3.9 es ideal para garantizar compatibilidad con las bibliotecas utilizadas. Descargar desde python.org.
o	Versiones más nuevas, como Python 3.10, pueden funcionar, pero algunas bibliotecas podrían necesitar actualizaciones.
•	Visual Studio:
o	Descargar Visual Studio 2019 o superior desde Visual Studio.
o	Durante la instalación, selecciona la carga de trabajo de Desarrollo con Python.

•	Configurar Python en Visual Studio:
o	Hay que asegurar tener instalado Python 3.8 o 3.9. 
o	Al instalar Python, hay una opción llamada "Add Python to PATH". Esta opción es clave para garantizar que Python funcione correctamente desde la línea de comandos o desde programas como Visual Studio.

## Librerías Necesarias
¿Qué es una "librería"?
En programación, las librerías son conjuntos de herramientas y funciones ya creadas que te ayudan a realizar tareas específicas sin tener que programarlas desde cero. 
El código utiliza varias librerías, cada una con un propósito específico:
1.	Pandas:
o	Uso: Manipula y analiza datos estructurados (tablas, hojas Excel).
o	Instalación: pip install pandas.
2.	Openpyxl:
o	Uso: Trabaja con archivos Excel en formato .xlsx. Permite leer, escribir y manipular estos archivos.
o	Instalación: pip install openpyxl.
3.	IPython:
o	Uso: Ofrece herramientas interactivas para Jupyter Notebooks, como la capacidad de mostrar widgets y contenido dinámico.
o	Instalación: pip install ipython.
4.	Ipywidgets:
o	Uso: Crea interfaces gráficas en Jupyter Notebooks (botones, campos de texto, carga de archivos, etc.).
o	Instalación: pip install ipywidgets.
5.	Os:
o	Uso: Gestiona funciones del sistema operativo como rutas de archivos. Es una biblioteca estándar de Python, por lo que no necesita instalación.
6.	Re:
o	Uso: Trabaja con expresiones regulares para buscar, reemplazar y analizar texto. Es una biblioteca estándar de Python, por lo que no necesita instalación.
7.	Io:
o	Uso: Maneja flujos de datos en memoria (lectura/escritura). Es una biblioteca estándar de Python, por lo que no necesita instalación.
8.	Unicodedata:
o	Uso: Normaliza texto en caracteres Unicode (útil para limpiar texto o manejar caracteres especiales). Es una biblioteca estándar de Python, por lo que no necesita instalación.

## Análisis Funcional del Código
El código se centra en procesar y consolidar datos de múltiples archivos Excel. 
Se divide en varias funciones principales:
### 1. Procesar Hora
Esta función estandariza el formato de horas. Convierte entradas como "20 25" o "0:033" al formato estándar HH:MM:SS. Si no puede procesar el valor, lo devuelve tal cual. Esto asegura que todas las horas en el archivo sigan un formato uniforme.
### 2. Normalizar Patentes
La normalización de patentes elimina caracteres especiales como puntos, guiones y espacios, y convierte todo a mayúsculas. Por ejemplo, una patente como "AB.123-CD" se convierte en "AB123CD". Esto facilita análisis posteriores y garantiza uniformidad.
### 3. Eliminar Filas Vacías Condicionalmente
Esta función elimina filas de una tabla donde todas las columnas claves (por ejemplo, "TERMINAL", "PATENTE") estén vacías o contengan solo espacios en blanco. Esto es útil para limpiar datos y eliminar información irrelevante.


### 4. Procesar Archivos
Esta función realiza un procesamiento completo de un archivo Excel:
•	Elimina columnas innecesarias: Identifica columnas irrelevantes como "Unnamed: 14" o "REJILLA" y las elimina.
•	Estandariza horas y patentes: Aplica las funciones anteriores para uniformizar datos.
•	Elimina filas vacías: Usa la función de eliminación condicional para limpiar la tabla.
•	Añade columnas vacías: Inserta columnas sin título cuando faltan ciertas combinaciones de datos.
### 5. Consolidar Archivos
Esta función interactiva permite al usuario cargar múltiples archivos Excel desde su computadora. 
Una vez cargados:
•	Los procesa uno por uno, limpiando y ajustando su contenido.
•	Consolida todos los datos en un único archivo Excel.
•	Ofrece una interfaz para seleccionar la carpeta donde guardar el archivo final.

## Ejecución en terminal para instalar librerías de Python
¿Qué es la terminal o CMD?
La terminal (o CMD, "Command Prompt") es una herramienta de texto de tu computadora donde puedes dar instrucciones directamente al sistema operativo. Aquí es donde se instalan las librerías necesarias.
Asegurar de tener Python instalado:
•	Abre la terminal:
En Windows: Presiona Win + R, escribe cmd y presiona Enter.
Copia y pega el siguiente comando y presiona Enter:
python --version

Abre la terminal para instalar las librerías:
•	En Windows, abre CMD como se describió antes.
•	Copia y pega el siguiente comando y presiona Enter:
pip install pandas openpyxl ipython ipywidgets notebook

¿Qué hace este comando?
•	pip: Es el instalador de Python. Le estás diciendo que descargue e instale librerías.

## Resumen de Beneficios
•	Automatización: Limpia y consolida datos automáticamente.
•	Interactividad: Ofrece una interfaz gráfica fácil de usar.
•	Uniformidad: Estandariza formatos clave como horas y patentes.
•	Flexibilidad: Permite procesar múltiples archivos simultáneamente.

¿Qué es Kernel?
Un kernel es el núcleo del entorno de ejecución en un Jupyter Notebook. Es responsable de:
1.	Ejecutar el Código:
o	El kernel interpreta las instrucciones escritas en las celdas (en este caso, Python) y devuelve los resultados.
2.	Mantener el Estado:
o	Recuerda variables, funciones y otros datos definidos mientras ejecutas el notebook, permitiendo que las celdas compartan información.
3.	Manejar Librerías y Dependencias:
o	El kernel utiliza el entorno de Python que configures, incluyendo las versiones de librerías instaladas.

## Interacción Usuario con el Codigo
Abrir y Ejecutar el Archivo .ipynb en Visual Studio
1.	Abrir Visual Studio:
o	Inicia Visual Studio y selecciona Abrir un Proyecto o Solución
2.	Abrir el Archivo .ipynb:
o	Navega hasta la ubicación de tu archivo Jupyter Notebook (“plantilla _interactiva_para_consolidar.ipynb”).
o	Selecciónalo y haz clic en Abrir.
3.	Interfaz de Jupyter en Visual Studio:
o	Visual Studio detectará automáticamente que es un archivo Jupyter Notebook y lo abrirá en el Editor de Notebooks.
o	Verás las celdas del archivo organizadas, con opciones para ejecutarlas individualmente o todas juntas.
4.	Ejecutar el Código:
o	Configura el kernel parte superior del editor de Jupyter Notebook, hay un menú desplegable llamado "Kernel" o similar. (asegúrate de seleccionar la versión correcta de Python instalada en tu sistema).
o	Haz clic en Ejecutar todo o selecciona celda por celda y presiona Shift + Enter.
o	
5.	Interactuar con el Código
Una vez que el archivo esté abierto y listo para ejecutarse:
•	Subir Archivos Excel:
o	Usa el widget “Upload” de carga de archivos para seleccionar y cargar los archivos .xlsx o .xlsm que deberían ser 20 a consolidar. ( “BCG1”,” CARLOS VALDOVINOS”,” DIEGO PORTALES”, “DUCAUD ”, “EL MAÑIO”, “GABRIELA”, “LAS PERDICES DIA”, “LAS PERDICES NOCHE”, “LAS TORRES”, “LLANQUIHUE”, “LO BLANCO”, “MARCOLETA DIA”, “MARCOLETA NOCHE”, “MICHIMALONCO”, “PLAZA OESTE”, “RENE OLIVARES”, “SAN JUAN”, “SANTA ANA”, “SANTA MARGARITA DIA”, “SANTA MARGARITA NOCHE”)
•	Especificar Ruta de Guardado:
o	Usa el widget “Ruta:” de texto para ingresar la carpeta donde se guardará el archivo consolidado.
•	Procesar y Consolidar:
o	Haz clic en el botón interactivo “Guardar archivo como...” que inicia el procesamiento y espera la confirmación en la salida.
•	Revisar que se haya creado el archivo en la ruta especificada.
