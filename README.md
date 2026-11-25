# Asistente de Resúmenes

Aplicación web local, construida con [Gradio](https://www.gradio.app/), que resume textos usando modelos de lenguaje ejecutados en local con [Ollama](https://ollama.com/). No se envía ningún dato a servicios en la nube: todo el procesamiento ocurre en tu máquina.

## Características

- Interfaz web sencilla con dos paneles: **Texto original** y **Texto resumido**.
- Detección automática de los modelos instalados en Ollama (se muestran como opciones seleccionables).
- Control de la **temperatura** del modelo (0.1 – 1.0) para ajustar creatividad/fidelidad del resumen.
- Control de la **longitud de contexto** (`num_ctx`), configurable hasta el valor definido en `config.yml`.
- Validación de la entrada: si el texto está vacío o tiene menos de 100 caracteres, se muestra un error.
- Comprobación del resultado: si el modelo no consigue acortar el texto, se avisa en lugar de devolver una salida inválida.
- Mensajes de error claros si Ollama no está arrancado, tarda demasiado o no devuelve modelos.

## Requisitos

- **Python 3.13** (probado con 3.13.15).
- **Ollama** instalado y en ejecución en `http://127.0.0.1:11434`.
- Al menos un modelo descargado en Ollama, por ejemplo:

  ```bash
  ollama pull llama3.2:1b
  ```

### Dependencias de Python

| Paquete    | Versión usada |
| ---------- | ------------- |
| `gradio`   | 6.32.0        |
| `ollama`   | 0.6.3         |
| `requests` | 2.34.2        |
| `PyYAML`   | 6.0.4         |
| `httpx`    | 0.28.1        |

## Instalación

Todas las dependencias están fijadas en `requirements.txt`.

### Opción A: con `uv` (recomendada)

```bash
uv venv
uv pip install -r requirements.txt
```

### Opción B: con `venv` y `pip`

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux / macOS
pip install -r requirements.txt
```

## Configuración

El archivo `config.yml` contiene los valores por defecto de la interfaz:

```yaml
temperatura: 0.3
context_length: 3000
```

- `temperatura`: valor inicial del deslizador de temperatura (0.1 – 1.0).
- `context_length`: tamaño máximo de contexto (`num_ctx`) y límite superior del deslizador de longitud.

> El archivo debe estar en el mismo directorio desde el que se ejecuta la aplicación; de lo contrario se lanzará `FileNotFoundError`.

## Uso

1. Arranca Ollama (si no está corriendo ya):

   ```bash
   ollama serve
   ```

2. Inicia la aplicación:

   ```bash
   python main.py
   ```

3. Abre en el navegador la dirección que muestra la consola (por defecto `http://127.0.0.1:7860`).

4. Pega un texto de al menos 100 caracteres, elige el modelo, ajusta temperatura y longitud, y pulsa **Resumir**.

## Estructura del proyecto

```
asistente_de_resumenes/
├── main.py                     # Lógica de la app e interfaz Gradio
├── config.yml                  # Parámetros por defecto (temperatura, contexto)
├── requirements.txt            # Dependencias de Python
├── Proyecto_IA_Generativa.pdf  # Documentación/capturas del proyecto
└── README.md
```

## Cómo funciona

1. Al arrancar, `cargar_config()` lee `config.yml` y `get_ollama_models()` consulta `GET /api/tags` de Ollama para obtener los modelos disponibles.
2. La interfaz de Gradio se construye con esos valores: deslizadores de temperatura y longitud, y un selector de modelo.
3. Al pulsar **Resumir**, `resumir_texto()` valida la entrada y envía una conversación al modelo mediante `ollama.Client`:
   - **system**: instrucción para resumir el texto en menos caracteres que el original.
   - **user**: el texto a resumir.
4. Se aplican las opciones `temperature` y `num_ctx`, con un timeout de 300 segundos.
5. Si el resumen devuelto es más corto que el original se muestra; en caso contrario se informa de que no se pudo resumir.

## Limitaciones conocidas

- La aplicación requiere que Ollama esté accesible en `127.0.0.1:11434`; no está pensada para servidores remotos.
- Si no hay modelos instalados, la app no se lanza y se imprime el error en consola.
- El texto se envía completo al modelo; para documentos muy largos conviene aumentar `context_length` o dividir el texto en fragmentos.
- El criterio de éxito es únicamente que la salida sea más corta que la entrada, no una evaluación de calidad del resumen.

## Posibles mejoras

- Permitir elegir la URL de Ollama desde `config.yml`.
- Trocear textos largos (chunking) y resumir por partes.
- Exportar el resumen a archivo (`.txt` / `.md`).
