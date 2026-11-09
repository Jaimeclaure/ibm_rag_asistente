# IBM RAG Asistente

Aplicación funcional de demostración para explorar información gastronómica mediante una interfaz conversacional. Incluye una interfaz web en Gradio, búsqueda semántica con ChromaDB y un servidor/cliente de herramientas MCP.

El proyecto permite ejecutar los módulos localmente, probar consultas sobre un catálogo de restaurantes de muestra y observar resultados de búsqueda. Las imágenes de [`capturas/`](capturas/) muestran las salidas generadas al ejecutar los ejemplos incluidos.

## Funcionalidades

- **Chat web:** interfaz conversacional con consultas sugeridas para explorar el catálogo.
- **Procesamiento de información:** extracción, validación y corrección de datos de restaurantes.
- **Búsqueda vectorial:** indexación y recuperación de descripciones con ChromaDB.
- **Fusión de resultados:** comparación de rankings provenientes de descripciones y captions.
- **Servidor MCP:** herramientas y recursos de ejemplo para consultar los datos.
- **Pruebas automatizadas:** casos unitarios y workflow de integración continua con GitHub Actions.

## Datos y generación de respuestas

La aplicación es ejecutable y autocontenida para pruebas locales. Utiliza un pequeño catálogo ficticio y un adaptador determinista llamado `DemoLLM`; no necesita claves de API ni descarga modelos de lenguaje o visión. Por eso las respuestas del chat son reproducibles y útiles para verificar el flujo de la aplicación, pero no son respuestas generadas por un servicio de IA externo.

El índice vectorial utiliza embeddings deterministas de demostración. La búsqueda y las herramientas MCP funcionan sobre los datos incluidos; no se conectan a inventarios, POS ni sistemas de pedidos reales.

## Capturas

La carpeta [`capturas/`](capturas/) contiene 12 imágenes PNG con código y salidas de los ejemplos ejecutados. Se conservan en el repositorio para mostrar visualmente los flujos y resultados incluidos en el proyecto. La vista del chat dentro de esas imágenes es ilustrativa; para usar la interfaz interactiva, ejecuta la aplicación como se describe a continuación.

## Requisitos

- Python 3.11
- Git
- Windows, macOS o Linux

Las versiones de dependencias directas están fijadas en los archivos de requisitos. `requirements.txt` instala las bibliotecas necesarias para todos los módulos; `requirements-web.txt` declara únicamente Gradio para ejecutar el chat en un entorno limpio.

### Instalación en Windows

Desde la carpeta del repositorio:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Instalación en macOS o Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Iniciar la interfaz web

Con el entorno virtual activado:

```bash
python -m restaurant_project.chatbot
```

Abre en el navegador la dirección local que Gradio muestra en la terminal. La interfaz incluye un chat, un campo para escribir consultas y botones con ejemplos rápidos.

Para instalar solo Gradio en un entorno nuevo, crea y activa el entorno virtual como arriba y ejecuta:

```bash
python -m pip install -r requirements-web.txt
python -m restaurant_project.chatbot
```

## Ejecutar los módulos

Con las dependencias completas instaladas:

```bash
python -m restaurant_project.module1
python -m restaurant_project.vector_index
python -m restaurant_project.module3
python -m restaurant_project.mcp_client
```

El cliente MCP inicia un servidor local mediante stdio y descubre sus herramientas y recursos. Para iniciar el servidor por separado:

```bash
python -m restaurant_project.mcp_server
```

En el transporte stdio, stdout se reserva para el protocolo MCP; los mensajes de depuración deben enviarse a stderr.

## Pruebas

Las pruebas unitarias usan la biblioteca estándar de Python:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions ejecuta estas pruebas en cada push y pull request. El workflow no instala las dependencias de la aplicación.

## Generar las capturas

Con todas las dependencias instaladas, puedes regenerar las imágenes en `capturas_demo/`:

```bash
python generate_screenshots.py
```

Para seleccionar otra carpeta de salida:

```bash
python generate_screenshots.py --output-dir ./mis_capturas
```

## Ejecución en hosting

La interfaz puede alojarse en un servicio compatible con aplicaciones Python/Gradio. Para ejecutar la demostración web, instala desde `requirements-web.txt` y configura el comando de inicio como:

```bash
python -m restaurant_project.chatbot
```

El despliegue de esta demo no incluye almacenamiento persistente, autenticación de administradores, procesamiento de pedidos, pagos ni integraciones con sistemas externos.
