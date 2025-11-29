<a id="readme-top"></a>

<div align="center">
  <h3 align="center">Artist Recomender</h3>
  <p align="center">
    Aplicación que recomienda artistas según tus géneros o estilos de arte favoritos.<br/><br/>
    <a href="https://github.com/maximberchun/ArtistRecomender/issues/new?labels=bug&template=bug-report---.md">Reportar un error</a>
    ·
    <a href="https://github.com/maximberchun/ArtistRecomender/issues/new?labels=enhancement&template=feature-request---.md">Solicitar una mejora</a>
  </p>
</div>

<details>
  <summary>Índice</summary>
  <ol>
    <li>
      <a href="#acerca-del-proyecto">Acerca del proyecto</a>
      <ul>
        <li><a href="#construido-con">Construido con</a></li>
      </ul>
    </li>
    <li>
      <a href="#primeros-pasos">Primeros pasos</a>
      <ul>
        <li><a href="#requisitos-previos">Requisitos previos</a></li>
        <li><a href="#obtener-la-api-key-de-groq">Obtener la API key de Groq</a></li>
        <li><a href="#instalacion">Instalación</a></li>
      </ul>
    </li>
    <li><a href="#uso">Uso</a></li>
    <li><a href="#hoja-de-ruta">Hoja de ruta</a></li>
    <li><a href="#contribuir">Contribuir</a></li>
    <li><a href="#licencia">Licencia</a></li>
    <li><a href="#contacto">Contacto</a></li>
    <li><a href="#agradecimientos">Agradecimientos</a></li>
  </ol>
</details>

## Acerca del proyecto

Artist Recomender es un sistema de recomendación de artistas y corrientes artísticas basado en tus gustos. Te permite descubrir nuevos pintores y estilos pictóricos a partir de un estilo, género o artista que te interese. El objetivo principal es facilitar el encuentro de artistas similares a los que ya te gustan, aprovechando técnicas de inteligencia artificial para ofrecer sugerencias personalizadas.

Algunas ventajas y características del proyecto son:

- **Recomendaciones personalizadas:** Encuentra artistas similares según tus preferencias en géneros o estilos artísticos, o incluso sugiere estilos relacionados en base a un artista que te interese.
- **Descubrimiento simplificado:** Te ayuda a descubrir nuevas corrientes artísticas de forma automatizada, sin tener que buscar manualmente entre miles de obras.
- **Tecnología híbrida IA + BD gráfica:** Combina un modelo de lenguaje (LLM) con una base de datos de grafos con soporte vectorial para analizar descripciones de obras de arte y encontrar similitudes más allá de coincidencias exactas.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

### Construido con

En este proyecto se integran varias tecnologías y herramientas destacadas para lograr su funcionalidad:

- **Streamlit** – Framework web para crear la interfaz de usuario de forma sencilla.
- **LlamaIndex** – Biblioteca para indexar datos y conectarlos con modelos de lenguaje (gestiona el índice vectorial sobre Neo4j).
- **Neo4j** – Base de datos de grafos utilizada como *vector store* para almacenar las representaciones vectoriales de las obras de arte.
- **GroqCloud** – Plataforma para ejecutar modelos de lenguaje grandes en la nube (LLM) de forma rápida y con baja latencia.
- **Hugging Face Embeddings** – Modelo de *embeddings* multilingüe (`intfloat/multilingual-e5-small`) para representar descripciones y consultas como vectores.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Primeros pasos

Esta sección te guiará en cómo configurar y ejecutar el proyecto en tu máquina local. Sigue estos pasos para obtener una copia local en funcionamiento.

### Requisitos previos

Asegúrate de tener instaladas las siguientes herramientas o software en tu sistema:

- **Python 3.x** – Lenguaje principal en el que está implementado el proyecto.
- **Docker y Docker Compose** – Para ejecutar fácilmente Neo4j y la aplicación en contenedores.
- **Cuenta en GroqCloud** – Necesaria para obtener la API key y usar el LLM en la nube.
- **Bibliotecas Python** – Las dependencias se indican en `requirements.txt` (incluye LlamaIndex, pandas, python-dotenv, etc.). Se recomienda instalarlas mediante `pip` una vez clonado el repositorio.

> **Nota:** Los *embeddings* se generan con un modelo de Hugging Face (`intfloat/multilingual-e5-small`) y el LLM se ejecuta a través de GroqCloud.

### Obtener la API key de Groq

1. Crea una cuenta y ve a la consola de GroqCloud → **API Keys**: https://console.groq.com/keys
2. Pulsa **Create API Key**.
3. Guárdala como variable de entorno o en un archivo `.env` local (git-ignorado).

### Instalación

#### 1. Clonar el repositorio

```bash
git clone https://github.com/maximberchun/ArtistRecomender.git
cd ArtistRecomender
```

#### 2. Crear archivo `.env`

Para el funcionamiento de la aplicación es necesario crear un `.env` en la ruta principal de la carpeta del proyecto con al menos el siguiente contenido:

```bash
# LLM (Groq)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
# GROQ_API_KEY= tu llave de groq

# Embeddings (Hugging Face)
EMBED_PROVIDER=hf
HF_EMBED_MODEL=intfloat/multilingual-e5-small
EMBEDDING_DIM=384

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j 

# Autentificación
APP_ADMIN_NAME=Admin
APP_ADMIN_USER=admin
# APP_ADMIN_PASSWORD_HASH= tu contraseña hasheada (ejecutar create_hash.py)
APP_COOKIE_NAME=artist_recommender_auth
# APP_COOKIE_KEY= llave de cookie
APP_COOKIE_DAYS=1
```

> Si ejecutas Neo4j fuera de Docker, ajusta `NEO4J_URI` a `bolt://localhost:7687`.

#### 3. Instalar dependencias (LOCAL)

Si prefieres ejecutar la aplicación directamente con Python:

```bash
pip install -r requirements.txt
```

Esto instalará las librerías necesarias, como LlamaIndex, Streamlit, Neo4j driver, etc. Los modelos de Hugging Face se descargarán automáticamente la primera vez que se utilicen.

#### 4. Iniciar Neo4j con Docker Compose

Primero se crea la imagen de Docker:

```bash
docker compose build
```

La forma recomendada de iniciar Neo4j (y la aplicación) es usando Docker Compose desde la raíz del proyecto:

```bash
docker compose up
```

Esto levantará:

- Un contenedor **Neo4j** escuchando en `bolt://neo4j:7687`.
- Un contenedor **app** con la aplicación Streamlit en `http://localhost:8501`.

Si solo quieres levantar Neo4j (por ejemplo, para usarlo con Python local), puedes adaptar el `docker-compose.yml` o usar una instancia de Neo4j instalada en tu sistema.

#### 5. Construir el índice vectorial

Una vez Neo4j esté en ejecución y la configuración sea correcta, debes poblar la base de datos con los *embeddings* del dataset. Ejecuta el script:

```bash
python -m src.build_index
```

Este script leerá el fichero CSV (`data/processed/wikiart_clean.csv`) y creará documentos con sus descripciones. Luego generará *embeddings* para cada documento usando el modelo de Hugging Face configurado y los almacenará en Neo4j como vectores. Por defecto, se toma una muestra aleatoria de 2000 obras para indexar, con el fin de agilizar el proceso.

#### 6. Ejecutar la aplicación web

Finalmente, inicia la interfaz de usuario basada en Streamlit:

```bash
streamlit run src/chatbot.py
```

Si estás utilizando Docker Compose, la app ya quedará expuesta en `http://localhost:8501` al ejecutar `docker compose up`.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

#### 7. Ejecuciones opcionales

- **Descarga/Prepara el conjunto de datos:**  
    El proyecto usa el dataset **WikiArt** (metadatos de obras de arte) disponible en Hugging Face. Si lo deseas, puedes generar un nuevo CSV con los datos ejecutando el script:

    ```bash
    python src/load_dataset.py
    ```

    Este paso puede tardar bastante y consumir hasta ~60 GB de espacio en caché, ya que descarga todos los metadatos de WikiArt. No es obligatorio ejecutarlo si ya dispones de un archivo CSV preprocesado. En caso de tener un `wikiart_metadata.csv` generado previamente, simplemente colócalo en `data/processed/` dentro del proyecto.

- **Carga de los URLs en el dataset:**  
    Se puede añadir los URLs de las imagenes y generar URLs de **Wikiart** que redirigen a la página del artista:

    ```bash
    python src/load_url.py
    ```

    Este paso puede tardar aproximadamente 20-30 minutos en buscar y generar todos los enlaces necesarios. En caso de tener un `wikiart_metadata.csv` generado previamente, simplemente colócalo en `data/processed/` dentro del proyecto.

- **Generar contraseña hash:**
    No es tan opcional ya que la aplicación requiere la contraseña hasheada pero en nuestro caso tenemos un archivo con la función que nos genera el hash a partir de la contraseña introducida:

    ```bash
    python src/create_hash.py
    ```

    El hash generado hace falta meterlo dentro de .env .

## Uso

Una vez que la aplicación Streamlit esté en funcionamiento, podrás utilizar **Artist Recomender** de la siguiente manera:

1. En la página principal, verás un campo de texto con la indicación: *"Describe qué estilo de dibujo o pintura te interesa"*. Aquí puedes escribir una breve descripción de tus gustos artísticos. Por ejemplo: *"Me gusta el impresionismo con paisajes"* o *"Obras similares a las de Van Gogh"*.
2. Pulsa el botón **"Recomendar"**. La aplicación consultará el índice vectorial en Neo4j para recuperar obras relacionadas con tu descripción y, con ayuda del modelo de lenguaje en Groq, generará una respuesta.
3. Como resultado, verás una recomendación con una lista de uno o varios artistas o corrientes artísticas que encajan con tu entrada, acompañada de una breve explicación en español de por qué se sugiere cada uno.

Cada respuesta variará según el texto proporcionado, ya que la IA formulará recomendaciones basadas en las obras más cercanas a tu descripción dentro del conjunto de datos.

Si encuentras un error o la respuesta tarda demasiado, revisa la consola donde lanzaste la aplicación (o los logs del contenedor) para detectar posibles excepciones (por ejemplo, problemas de conexión con Neo4j o con la API de Groq).

> **Sugerencia:** Puedes modificar la cantidad de resultados similares (`similarity_top_k`) en el código si deseas que el motor considere más o menos obras al elaborar la recomendación (por defecto son 8). También es posible ajustar o traducir el mensaje *prompt* en `src/query_engine.py` si quisieras obtener respuestas en otro idioma o con otro estilo.

Mira los [issues abiertos](https://github.com/maximberchun/ArtistRecomender/issues) para ver la lista completa de funciones propuestas y problemas conocidos pendientes.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Contribuir

¡Las contribuciones son lo que hace que la comunidad de código abierto sea un lugar increíble para aprender, inspirarse y crear! Cualquier aportación que quieras hacer será muy apreciada.

Si tienes alguna idea o sugerencia para mejorar el proyecto, por favor realiza un *fork* del repositorio y crea una rama para tu funcionalidad:

```bash
git checkout -b feature/NuevaFuncionalidad
```

Realiza los commits de tus cambios:

```bash
git commit -m "Agrega nueva funcionalidad"
```

Empuja la rama al repositorio remoto:

```bash
git push origin feature/NuevaFuncionalidad
```

Finalmente, abre un **Pull Request** para que se revise tu aporte.

También puedes simplemente abrir un *issue* con la etiqueta `enhancement` (mejora) para describir tu propuesta. ¡No olvides darle una estrella al proyecto si te gusta! ¡Gracias por tu apoyo!

### Contribuidores principales

<a href="https://github.com/maximberchun/ArtistRecomender/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=maximberchun/ArtistRecomender" alt="Contribuyentes del proyecto" />
</a>

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Contacto

Maxim Berchun – @maximberchun – mberch00@estudiantes.unileon.es · maximberchun@hotmail.com

Enlace del proyecto: https://github.com/maximberchun/ArtistRecomender

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Agradecimientos

Recursos y bibliotecas que han contribuido indirectamente a este proyecto:

- **Hugging Face** – Dataset WikiArt, por proveer una base de datos amplia de obras de arte con la que alimentar el sistema de recomendaciones.
- **LlamaIndex (Hugging Face Index)** – Por facilitar la construcción de índices de información para LLMs, permitiendo integrar Neo4j como almacenamiento vectorial.
- **Neo4j Community** – Por la base de datos de grafos y su soporte para índices vectoriales, clave en la implementación eficiente de las búsquedas de similitud.
- **Groq (GroqCloud)** – Plataforma de inferencia de baja latencia con API compatible con OpenAI y Llama, utilizada como proveedor LLM para generar respuestas de manera rápida y fiable.
- **Mixedbread AI** – Por los modelos de *embeddings* que han servido de referencia en las primeras fases del proyecto.
- **Streamlit Docs** – Documentación oficial de Streamlit, que ayudó a construir rápidamente la interfaz web interactiva.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Copyright

Todas las licencias de este repositorio están protegidas por derechos de autor de sus respectivos autores.
Todo lo demás se publica bajo CC0. Consulta el archivo `LICENSE` para más detalles.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

> © 2025, Maxim Berchun – Universidad de León  