import sys

import gradio as gr
import requests
from httpx import ConnectError, TimeoutException
from ollama import Client, ResponseError
import yaml

MIN_CARACTERES = 300
MAX_CARACTERES = 4000  # orientativo para context_length: 3000
LONGITUDES = {
    "Corto (20% - 30%)": (0.20, 0.30),
    "Medio (40% - 50%)": (0.40, 0.50),
    "Largo (60% - 75%)": (0.60, 0.75),
}

#cargar datos desde config.yml
def cargar_config():
    try:
        with open("config.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Archivo config.yml no encontrado")


#Cargar CONFIG_DATA antes que la carga de la interfaz
CONFIG_DATA = cargar_config() or {}


#Cargar los modelos disponibles de Ollama
def get_ollama_models():
    modelos_encontrados = []
    mensaje_error = None
    try:
        response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
        #Si Ollama responde con un error HTTP (500, por ejemplo), pasa a RequestException en vez de fallar luego al leer el JSON
        response.raise_for_status()
        json_data = response.json()
        models = json_data['models']
        for model in models:
            modelos_encontrados.append(model['name'])
    except requests.exceptions.ConnectionError as error:
        mensaje_error = f"No se puede conectar con Ollama. ¿Está encendido?: {error}"
    except requests.exceptions.Timeout as error:
        mensaje_error = f"Ollama ha tardado demasiado en responder: {error}"
    except requests.exceptions.RequestException as error:
        mensaje_error = f"Error al pedir los modelos: {error}"
    except KeyError:
        mensaje_error = "La respuesta de Ollama no incluye la lista de modelos."

    return modelos_encontrados, mensaje_error


#Hacer la llamada antes que la carga de la interfaz
modelos, error_modelos = get_ollama_models()


#Enviar el texto a Ollama para que nos devuelva el texto resumido
def resumir_texto(texto, temperatura, longitud, modelo):
    texto = texto.strip()
    len_texto = len(texto)
    if len_texto >= MIN_CARACTERES:
        if len_texto <= MAX_CARACTERES:
            if modelo:
                minimo, maximo = LONGITUDES[longitud]
                num_palabras = len(texto.split())
                palabras_min = max(1, round(num_palabras * minimo))
                palabras_max = max(palabras_min + 1, round(num_palabras * maximo))

                messages = [
                    {"role": "system", "content": f"Resume el texto en entre {palabras_min} y {palabras_max} palabras. Responde solo con el resumen."},
                    {"role": "user", "content": texto}
                ]

                client = Client(timeout=300)
                try:
                    response = client.chat(
                        model = modelo,
                        messages = messages,
                        options = {
                            "temperature": temperatura,
                            "num_ctx":  CONFIG_DATA.get('context_length', 3000)
                        },
                    )
                except ResponseError as error:
                    return f'Error de Ollama: {error}'
                except (ConnectError, ConnectionError) as error:
                    return f'Error de Connect/ConnectionError: {error}'
                except TimeoutException:
                    return "La petición ha superado el tiempo de espera"

                texto_resumido = response['message'].content.strip()
                if len(texto_resumido) < len_texto and texto_resumido != '':
                    return texto_resumido
                else:
                    return 'No ha podido resumir el texto'
            else:
                raise gr.Error("Selecciona un modelo antes de resumir.")
        raise gr.Error(f"El texto es demasiado largo (máximo {MAX_CARACTERES} caracteres).")
    else:
        raise gr.Error("No hay texto o poco texto")



#Interfaz de Gradio
demo = gr.Interface(
    fn=resumir_texto,
    inputs=[
        gr.Textbox(label=f"mínimo {MIN_CARACTERES} y máximo {MAX_CARACTERES} caracteres)", lines=12),
        gr.Slider(value=CONFIG_DATA.get('temperatura', 0.3), minimum=0.1, maximum=1, step=0.1, label="Temperatura"),
        gr.Dropdown(choices=list(LONGITUDES), value=list(LONGITUDES)[1], label="Longitud aproximada del resumen"),
        gr.Radio(choices=modelos,value=modelos[0] if modelos else None,label="Modelos"),
    ],
    outputs=[
        gr.Textbox(label="Texto resumido", lines=12),
    ],
    submit_btn="Resumir",
    clear_btn="Limpiar",
    flagging_mode="never",
    api_name="predict"
)


if __name__ == '__main__':
    if modelos:
        demo.launch()
    else:
        sys.exit(error_modelos or "No hay modelos instalados. Descarga uno con: ollama pull llama3.2:1b")
