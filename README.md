# Restaurant RAG Capstone Demo

Demo educativa local para practicar conceptos de procesamiento de datos, recuperación vectorial, herramientas MCP y una interfaz de chat. Incluye también dos propuestas de producto para futuros asistentes RAG:

- [Diseño de asistente para cafetería](docs/asistente-cafeteria.md)
- [Diseño de asistente para panadería](docs/asistente-panaderia.md)

Las propuestas son documentos de diseño: **ninguno de esos dos sistemas de pedidos está implementado todavía**. La aplicación existente es una demo de restaurantes ficticios; no es una solución de producción ni un RAG conectado a un LLM.

## Alcance actual

- `DemoLLM` genera respuestas/captions deterministas a partir de reglas y datos de muestra; no llama a un LLM ni a un modelo de visión.
- ChromaDB y embeddings simples y deterministas muestran los ejemplos de índice vectorial; no se descargan modelos de embeddings.
- El servidor/cliente de ejemplo usa el SDK MCP.
- Gradio ofrece una interfaz de chat funcional sobre datos locales ficticios.
- Las imágenes de `capturas_demo/` son evidencia visual marcada como demo, no capturas oficiales del curso.

## ¿Por qué el entorno local ocupa tanto?

La carpeta `.venv` no es el código fuente y **no se debe subir a GitHub**. En el entorno de desarrollo observado, la carpeta del proyecto ocupaba unos 612 MB, casi todo dentro de `.venv`. Bibliotecas como ChromaDB, Gradio y MCP traen dependencias transitivas y componentes binarios. Pillow se usa para generar las imágenes demostrativas.

No todos los despliegues necesitan todas esas bibliotecas:

- Para ejecutar **solo el chatbot Gradio**, instala `requirements-web.txt` en un entorno nuevo. Gradio puede instalar sus dependencias transitivas, pero no se instalan ChromaDB ni MCP como dependencias directas de esta app.
- Para ejecutar **todos los ejemplos** y generar las capturas, instala `requirements.txt`.
- El workflow de GitHub Actions corre pruebas unitarias con la biblioteca estándar de Python y no instala las dependencias de la demo.

El `.gitignore` evita que los entornos virtuales, credenciales y cachés se incluyan en el repositorio. Ignorar `.venv` no elimina esa carpeta del disco.

## Requisitos

- Python 3.11 (el entorno comprobado para esta configuración fue Python 3.11.5).
- Git para clonar o publicar el repositorio.
- Conexión a Internet solo para clonar el código e instalar paquetes.
- Windows PowerShell, macOS o Linux; los comandos de activación del entorno varían según el sistema.

Las versiones directas de paquetes en `requirements.txt` están fijadas a las usadas en el entorno de desarrollo. Las dependencias transitivas pueden variar según plataforma y fecha; este archivo no es un lockfile multiplataforma byte-a-byte.

## Instalación en Windows

Desde la carpeta del proyecto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para instalar únicamente lo necesario como dependencia directa para la interfaz Gradio en un entorno independiente:

```powershell
py -3.11 -m venv .venv-web
.\.venv-web\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-web.txt
```

Usar un entorno separado es importante: instalar `requirements-web.txt` dentro de un entorno que ya contiene el resto no desinstala las bibliotecas previamente instaladas.

## Instalación en macOS o Linux

Desde la carpeta del proyecto:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para la interfaz solamente, usa `.venv-web` y cambia el último comando por `python -m pip install -r requirements-web.txt`.

## Ejecutar la interfaz

Con el entorno que contiene Gradio activado:

```powershell
python -m restaurant_project.chatbot
```

Gradio mostrará en la terminal la dirección local para abrir en el navegador. La página permite conversar y usar tres consultas sugeridas. Las respuestas son demostrativas y usan el pequeño conjunto local de restaurantes.

## Ejecutar todos los ejemplos

Con las dependencias completas instaladas:

```powershell
python -m restaurant_project.module1
python -m restaurant_project.vector_index
python -m restaurant_project.module3
python -m restaurant_project.mcp_client
python -m restaurant_project.chatbot
```

El cliente MCP inicia el servidor localmente mediante stdio, enumera herramientas y recursos, y anuncia el root `file:///.../restaurant_project/data`. Para probar el servidor en un inspector MCP, ejecuta:

```powershell
python -m restaurant_project.mcp_server
```

Al usar stdio, no imprimas mensajes de depuración a stdout: ese canal transporta el protocolo MCP.

## Pruebas

Las pruebas unitarias usan la biblioteca estándar y no requieren instalar las dependencias de la aplicación:

```powershell
python -m unittest discover -s tests -v
```

El workflow `.github/workflows/tests.yml` ejecuta esta misma prueba en GitHub Actions para cada push y pull request.

## Preparar el repositorio para GitHub

Nombre sugerido para una futura plataforma común de cafetería y panadería: **`food-service-rag-assistant`**. El nombre describe mejor el producto futuro que el alcance de esta demo actual.

Antes de publicar:

1. Crea un repositorio nuevo en GitHub para este proyecto, si quieres mantenerlo separado de otros proyectos.
2. Sube el contenido de esta carpeta como raíz del repositorio, incluyendo `.github/workflows/`, `docs/`, los módulos, pruebas y archivos de requisitos.
3. No incluyas `.venv`, `.venv-web`, `.env`, claves de API, datos personales ni archivos de configuración privados. Revisa los archivos antes de hacer push.
4. Después de subirlo, confirma en GitHub que la acción **Tests** terminó correctamente.

Esta carpeta está dentro de un repositorio Git más amplio en el entorno de desarrollo. Si la intención es publicar solo este proyecto, no inicialices ni publiques accidentalmente el repositorio padre; crea un repositorio independiente con los archivos de esta carpeta. No se incluyen credenciales ni se configura un despliegue público automáticamente.

Para desplegar únicamente la interfaz de demostración, el hosting debe instalar desde `requirements-web.txt` y ejecutar `python -m restaurant_project.chatbot` (o configurar el comando equivalente de Gradio). Para el futuro asistente real de pedidos se necesitarán además una API, base de datos, autenticación, almacenamiento persistente, credenciales protegidas y una plataforma de despliegue apropiada.

## Generar las 12 imágenes demostrativas

Desde la raíz del proyecto y con un entorno que tenga instaladas todas las dependencias:

```powershell
python .\generate_screenshots.py
```

El script crea `capturas_demo` y guarda allí 12 archivos PNG. Cada imagen muestra el fragmento de código local y la salida real del ejemplo correspondiente; la vista del chatbot es ilustrativa. Todas llevan una marca visible de **DEMO LOCAL - NO OFICIAL**. Estas imágenes no son capturas de pantalla del navegador ni de los laboratorios de IBM y no sustituyen la evidencia original que solicita el curso.

Para elegir otra carpeta:

```powershell
python .\generate_screenshots.py --output-dir .\mis_capturas_demo
```

## Correspondencia con las preguntas del curso

| Pregunta | Implementación en la demo |
|---|---|
| Q1 | `module1.py`, `generate_and_validate_restaurants` |
| Q2 | `module1.py`, `caption_all_recipes` |
| Q3 | `module1.py`, `process_new_restaurant` y su ciclo de reparación |
| Q4 | `vector_index.py`, `build_multimodal_vector_index` |
| Q5 | `vector_index.py`, `run_similarity_retrieval` |
| Q6 | `vector_index.py`, `run_fusion_demo` |
| Q7 | `module3.py`, `food_style_expert` |
| Q8 | `module3.py`, `node_analyze_styles` |
| Q9 | `module3.py`, `test_extract_preferences` |
| Q10 | `mcp_server.py`, herramienta `search_restaurants` |
| Q11 | `mcp_client.py`, descubrimiento de tools/resources y roots |
| Q12 | `chatbot.py`, interfaz Gradio |

Para obtener las evidencias del curso, ejecuta esos mismos puntos en los notebooks/entorno oficiales y guarda las capturas con los nombres exactos del enunciado. En esta demo puedes capturar el código y salidas equivalentes, identificándolas como demo y no como resultados del laboratorio original.

### Nombres de las capturas del curso

- Q1 `M1L1_structure_for_loop.jpg` o `.png`
- Q2 `M1L2_caption_all_recipes.jpg` o `.png`
- Q3 `M1L3_new_data_entry_process.jpg` o `.png`
- Q4 `M2L1_multimodal_vector_index.jpg` o `.png`
- Q5 `M2L2_similarity_retrieval.jpg` o `.png`
- Q6 `M2L3_multimodal_fusion_results.jpg` o `.png`
- Q7 `M3L1_food_style_expert_goal.jpg` o `.png`
- Q8 `M3L2_node_analyze_styles.jpg` o `.png`
- Q9 `M3L3_preference_extraction_test.jpg` o `.png`
- Q10 `M4L1_Configure_Tools_Data_MCP_Server.jpg` o `.png`
- Q11 `M4L2_Build_Test_MCP_Client.jpg` o `.png`
- Q12 `M4L3_Design_LLM_MCP_Host.jpg` o `.png`
