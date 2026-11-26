# Asistente de resúmenes

Aplicación en Python que resume un texto usando un modelo de lenguaje local con [Ollama](https://ollama.com). La interfaz web está hecha con [Gradio](https://www.gradio.app).

Pegas un texto, eliges el tamaño aproximado del resumen (como porcentaje del original), la temperatura y el modelo, y la aplicación devuelve una versión resumida.

## Requisitos

- Python 3.10 o superior.
- Ollama instalado y **en ejecución** antes de arrancar la aplicación.
- Al menos un modelo descargado en Ollama, por ejemplo:

```bash
ollama pull llama3.2:1b
```

Puedes ver los modelos instalados con `ollama list`.

## Instalación

1. Descarga o clona el proyecto y entra en su carpeta.
2. (Recomendado) Crea y activa un entorno virtual:

```bash
python -m venv .venv
```

   - Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
   - macOS / Linux: `source .venv/bin/activate`

3. Instala las dependencias:

```bash
python -m pip install gradio ollama requests pyyaml
```

## Configuración

Los valores iniciales se leen del archivo `config.yml`:

```yaml
temperatura: 0.3
context_length: 3000
```

| Clave | Para qué sirve |
|---|---|
| `temperatura` | Valor inicial del deslizador de temperatura. Más bajo, respuestas más predecibles; más alto, más variadas. |
| `context_length` | Tamaño de contexto en tokens (`num_ctx` de Ollama): cuánto texto puede tener en cuenta el modelo, contando el texto original y el resumen. No se cambia desde la interfaz. Si falta, se usa 3000. |

Los cambios que hagas en la interfaz no se guardan en `config.yml`. Para cambiar los valores iniciales, edita el archivo y reinicia la aplicación.

## Uso

Desde la carpeta del proyecto, con Ollama encendido:

```bash
python main.py
```

Abre en el navegador la dirección que aparece en la terminal (normalmente `http://127.0.0.1:7860`).

1. Pega el texto en **Texto original** (entre 300 y 4000 caracteres).
2. Elige la **Longitud del resumen**, que indica el tamaño aproximado respecto al texto original:

| Opción | Tamaño del resumen |
|---|---|
| Corto (20% - 30%) | Entre el 20 % y el 30 % de las palabras del original |
| Medio (40% - 50%) | Entre el 40 % y el 50 % de las palabras del original |
| Largo (60% - 75%) | Entre el 60 % y el 75 % de las palabras del original |

3. Ajusta la **Temperatura** si quieres.
4. Elige un modelo en **Modelos**.
5. Pulsa **Resumir**. El resultado aparece en **Texto resumido**.
6. Pulsa **Limpiar** para vaciar los campos.

## Cómo funciona

1. Al arrancar, se carga `config.yml`.
2. Se piden a Ollama los modelos instalados (`http://127.0.0.1:11434/api/tags`) y se muestran en la lista de modelos.
3. Si no se pueden obtener, o no hay ninguno instalado, se muestra el motivo por la terminal y la aplicación se cierra sin abrir la interfaz.
4. Al pulsar **Resumir**, la función `resumir_texto` valida la entrada y cuenta las palabras del texto. Con el porcentaje elegido calcula un rango de palabras (por ejemplo, entre 30 y 45) y se lo pide al modelo en un mensaje de sistema. Después devuelve la respuesta.

Se traduce el porcentaje a un número de palabras porque a un modelo pequeño le resulta más fácil cumplir "entre 30 y 45 palabras" que "el 30 % del texto".

## Validaciones y errores

- El texto debe tener entre 300 y 4000 caracteres (el máximo está en la constante `MAX_CARACTERES` de `main.py`).
- Hay que seleccionar un modelo.
- Si Ollama no responde, el modelo no existe o se supera el tiempo de espera (300 segundos), se muestra un mensaje de error en el cuadro de resultado.
- Si el modelo devuelve una respuesta vacía, o un texto igual de largo o más largo que el original, se muestra "No ha podido resumir el texto".

## Estructura del proyecto

```text
.
├── main.py       # Lógica y interfaz de Gradio
├── config.yml    # Valores iniciales (temperatura y contexto)
└── README.md
```

## Limitaciones

- Ollama tiene que estar encendido **antes** de arrancar. La lista de modelos se carga una sola vez, al iniciar: si instalas un modelo nuevo, reinicia la aplicación.
- Hay que ejecutarla desde la carpeta del proyecto, porque `config.yml` se busca en la ruta actual.
- El tamaño del resumen es aproximado: un modelo pequeño puede quedarse algo por debajo o por encima del rango pedido.
- El máximo de 4000 caracteres es orientativo para un contexto de 3000 tokens, porque el texto y el resumen comparten ese contexto. Si aumentas `context_length` en `config.yml`, aumenta también `MAX_CARACTERES`.
- La lista muestra todos los modelos instalados, incluidos los que no sirven para chatear (por ejemplo, los de embeddings).
- Un modelo pequeño puede cometer errores o inventar datos, por lo que conviene revisar el resumen.
