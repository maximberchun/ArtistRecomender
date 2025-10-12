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
        <li><a href="#instalación">Instalación</a></li>
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
- **Tecnología híbrida IA + BD Gráfica:** Combina un modelo de lenguaje (LLM) con una base de datos gráfica de vectores para analizar descripciones de obras de arte y encontrar similitudes más allá de coincidencias exactas.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

### Construido con

En este proyecto se integran varias tecnologías y herramientas destacadas para lograr su funcionalidad:

- Framework web para crear la interfaz de usuario de forma sencilla.
- Biblioteca para indexar datos y conectarlos con modelos de lenguaje (usada para gestionar el índice vectorial).
- Base de datos de grafos utilizada como *vector store* para almacenar las representaciones vectoriales de las obras de arte.
- Plataforma para ejecutar modelos de lenguaje grandes localmente (se utiliza para generar *embeddings* y respuestas con un modelo LLM local).

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Primeros pasos

Esta sección te guiará en cómo configurar y ejecutar el proyecto en tu máquina local. Sigue estos pasos para obtener una copia local en funcionamiento.

### Requisitos previos

Asegúrate de tener instaladas las siguientes herramientas o software en tu sistema:

- **Python 3.x** – Lenguaje principal en el que está implementado el proyecto.
- **Docker y Docker Compose** – Para ejecutar fácilmente la base de datos Neo4j en un contenedor.
- **Neo4j** – Si prefieres instalar Neo4j directamente en lugar de usar Docker.
- **Ollama** – Necesario para cargar y ejecutar los modelos de lenguaje localmente.
- **Bibliotecas Python** – Las dependencias Python se indican en `requirements.txt` (incluye llama-index, pandas, python-dotenv, etc.). Se recomienda instalarlas mediante pip una vez clonado el repositorio.

> **Nota:** Ollama debe tener disponibles los modelos adecuados para este proyecto. Por defecto, en el archivo `.env` se especifica un modelo de *embeddings* (`mxbai-embed-large`) y un modelo de lenguaje (`llama3`). Asegúrate de descargarlos en Ollama (`ollama pull <nombre_del_modelo>`) o modifica `.env` para usar modelos que tengas disponibles. El modelo de *embeddings* **mxbai-embed-large** y un modelo LLM basado en Llama 2 son recomendados para resultados óptimos.

### Instalación

Sigue estos pasos para instalar y poner en marcha la aplicación:

1. **Clona el repositorio:**

    ```bash
    git clone https://github.com/maximberchun/ArtistRecomender.git
    ```

2. **Instala las dependencias de Python:**  
    Navega al directorio del proyecto y ejecuta: 

    ```bash
    pip install -r requirements.txt
    ```

    Esto instalará las librerías necesarias, como LlamaIndex. Ten en cuenta que esto no incluye la descarga de los modelos de Ollama (ver nota arriba).

3. **Descarga/Prepara el conjunto de datos (opcional):**  
    El proyecto usa el dataset **WikiArt** (metadatos de obras de arte) disponible en Hugging Face. Si lo deseas, puedes generar un nuevo CSV con los datos ejecutando el script:

    ```bash
    python src/load_dataset.py
    ```

    Este paso puede tardar bastante y consumir hasta ~60 GB de espacio en caché, ya que descarga todos los metadatos de WikiArt. No es obligatorio ejecutarlo si ya dispones de un archivo CSV preprocesado. En caso de tener un `wikiart_clean.csv` generado previamente, simplemente colócalo en `data/processed/` dentro del proyecto.

4. **Inicia la base de datos Neo4j:**  
    La forma más sencilla es usar Docker Compose. Desde la carpeta `neo4j/` del repositorio, ejecuta:

    ```bash
    docker-compose up -d
    ```

    Esto levantará un contenedor Neo4j escuchando en `bolt://localhost:7687` con las credenciales predeterminadas (neo4j/password). Se aplicará automáticamente un script de inicialización (`init.cypher`) para crear los índices y *constraints* necesarios en la base de datos.

5. **Configura las variables de entorno:**  
    El proyecto utiliza un archivo `.env` para configurar la conexión a Neo4j y los modelos de Ollama. Asegúrate de que el archivo `.env` existe (debería venir incluido) y revisa que los datos sean correctos (URI de Neo4j, usuario, contraseña, nombres de modelos de Ollama). Si necesitas cambios (por ejemplo, usar una contraseña distinta o modelos diferentes), edita este archivo en consecuencia.

6. **Construye el índice vectorial:**  
    Una vez Neo4j esté en ejecución y configurado, puedes poblar la base de datos con los *embeddings* del dataset. Ejecuta el script:

    ```bash
    python src/build_index.py
    ```

    Este script leerá el fichero CSV (`data/processed/wikiart_clean.csv`) y creará documentos con sus descripciones. Luego generará *embeddings* para cada documento usando el modelo de *embeddings* de Ollama y los almacenará en Neo4j como vectores. Por defecto, se toma una muestra aleatoria de 2000 obras para indexar, con el fin de agilizar el proceso. Verás mensajes en la consola indicando el progreso.

7. **Ejecuta la aplicación web:**  
    Finalmente, inicia la interfaz de usuario basada en Streamlit con:

    ```bash
    streamlit run src/chatbot.py
    ```

    Esto abrirá (o podrás abrir manualmente) un navegador web apuntando a `http://localhost:8501`. Allí encontrarás una interfaz sencilla donde puedes introducir texto para obtener recomendaciones.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Uso

Una vez que la aplicación Streamlit esté en funcionamiento, podrás utilizar **Artist Recomender** de la siguiente manera:

1. En la página principal, verás un campo de texto con la indicación: *"Describe qué estilo de dibujo o pintura te interesa:"*. Aquí puedes escribir una breve descripción de tus gustos artísticos. Por ejemplo: *"Me gusta el impresionismo con paisajes"* o *"Obras similares a las de Van Gogh"*.
2. Pulsa el botón **"Recomendar"**. La aplicación consultará el índice vectorial para recuperar obras relacionadas con tu descripción y, con ayuda del modelo de lenguaje, generará una respuesta.
3. Como resultado, verás una recomendación con una lista de uno o varios artistas o corrientes artísticas que encajan con tu entrada, acompañada de una breve explicación en español de por qué se sugiere cada uno.

Por ejemplo, ante una consulta sobre *"impresionismo"*, el sistema podría responder con algo como:

*"Te recomiendo explorar a Claude Monet, ya que fue un pintor destacado del Impresionismo que compartía tus intereses por los paisajes y el uso de la luz. También podrías ver obras de Camille Pissarro, otro impresionista cuyos cuadros presentan características similares."*

Cada respuesta variará según el texto proporcionado, ya que la IA formulará recomendaciones basadas en las obras más cercanas a tu descripción dentro del conjunto de datos.

Si encuentras un error o la respuesta tarda demasiado, revisa la consola donde lanzaste Streamlit para detectar posibles excepciones (por ejemplo, problemas de conexión con Neo4j u Ollama). Asegúrate de que tanto Neo4j como Ollama estén en ejecución y con los modelos cargados.

> **Sugerencia:** Puedes modificar la cantidad de resultados similares (`similarity_top_k`) en el código si deseas que el motor considere más o menos obras al elaborar la recomendación (por defecto son 5). También es posible ajustar o traducir el mensaje *prompt* en `src/query_engine.py` si quisieras obtener respuestas en otro idioma o con otro estilo.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Hoja de ruta

- Implementación básica del motor de recomendaciones (índice vectorial con Neo4j y consultas con LLM en español).
- Interfaz web simple con Streamlit para ingresar consultas y mostrar resultados.
- Indexar la totalidad del dataset WikiArt (actualmente se usa una muestra de 2000 registros por cuestiones de rendimiento).
- Permitir búsqueda inversa (por nombre de artista específico para recomendar estilos relacionados, si no se logra ya con la descripción libre).
- Soporte para consultas multilingües (por ejemplo, entender entradas en inglés y responder acorde, además del español).
- Incorporar visualización de imágenes de las obras o artistas sugeridos para enriquecer la experiencia de usuario.
- Optimizar el rendimiento y uso de memoria (ej. eliminar necesidad de caché masivo al generar el CSV, cargar *embeddings* de forma más eficiente, etc.).

Mira los [issues abiertos](https://github.com/maximberchun/ArtistRecomender/issues) para ver la lista completa de funciones propuestas y problemas conocidos pendientes.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Contribuir

¡Las contribuciones son lo que hace que la comunidad de código abierto sea un lugar increíble para aprender, inspirarse y crear! Cualquier aportación que quieras hacer será muy apreciada.

Si tienes alguna idea o sugerencia para mejorar el proyecto, por favor realiza un *fork* del repositorio y crea una rama para tu funcionalidad (`git checkout -b feature/NuevaFuncionalidad`). Luego realiza tus *commits* en esa rama (`git commit -m 'Agrega nueva funcionalidad'`) y envía tus cambios (`git push origin feature/NuevaFuncionalidad`). Finalmente, abre un **Pull Request** para que revisemos tu aporte.

También puedes simplemente abrir un *issue* con la etiqueta "enhancement" (mejora) para describir tu propuesta. ¡No olvides darle una estrella al proyecto si te gusta! ¡Gracias por tu apoyo!

Pasos para contribuir al proyecto:

1. Haz un **fork** del proyecto.
2. Crea una rama para tu contribución:  
   ```bash
   git checkout -b feature/LoQueVasAAgregar

    Realiza el commit de tus cambios:

git commit -m "Agrega X cosa"

Empuja la rama al repositorio remoto:

    git push origin feature/LoQueVasAAgregar

    Abre un Pull Request para que se revise tu cambio.

## Contribuidores principales:
<a href="https://github.com/maximberchun/ArtistRecomender/graphs/contributors">
<img src="https://contrib.rocks/image?repo=maximberchun/ArtistRecomender" alt="Contribuyentes del proyecto" />
</a> <p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Licencia

Este proyecto no cuenta con una licencia específica. El código fuente se proporciona con fines educativos y demostrativos. Todos los derechos reservados a menos que se especifique lo contrario en el futuro. <p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Contacto

Maxim Berchun – @maximberchun – mberch00@estudiantes.unileon.es , maximberchun@hotmail.com
Enlace del proyecto: https://github.com/maximberchun/ArtistRecomender <p align="right">(<a href="#readme-top">volver arriba</a>)</p>


## Recursos y bibliotecas que han contribuido indirectamente a este proyecto:

    Hugging Face – Dataset WikiArt – Por proveer una base de datos amplia de obras de arte con la que alimentar el sistema de recomendaciones.

    LlamaIndex (GPT Index) – Por facilitar la construcción de índices de información para LLMs, lo que permitió integrar Neo4j como almacenamiento vectorial.

    Neo4j Community – Por la base de datos de grafos y su soporte para índices vectoriales, clave en la implementación eficiente de las búsquedas de similitud.

    Ollama – Proyecto de código abierto que hace posible ejecutar modelos de lenguaje de manera local de forma sencilla.

    Mixedbread AI – Creadores del modelo de embeddings mxbai-embed-large, utilizado para representar las descripciones de las obras de arte en este proyecto.

    Streamlit Docs – Documentación oficial de Streamlit, que ayudó a construir rápidamente la interfaz web interactiva.

<p align="right">(<a href="#readme-top">volver arriba</a>)</p> ```