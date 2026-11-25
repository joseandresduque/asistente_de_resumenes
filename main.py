import gradio as gr
import requests
from httpx import ConnectError, TimeoutException
from ollama import Client, ResponseError
import yaml


CONFIG_DATA = {}

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
        error_modelos = str(error.args[0].reason).split(":")
        mensaje_error = error_modelos[1] + ',' + error_modelos[2]
    except requests.exceptions.Timeout as error:
        mensaje_error = f"Ollama ha tardado demasiado en responder: {error}"
    except requests.exceptions.RequestException as error:
        mensaje_error = f"Error al pedir los modelos: {error}"
    except KeyError:
        mensaje_error = "La respuesta de Ollama no incluye la lista de modelos."

    return modelos_encontrados, mensaje_error


#Hacer la llamada antes que la carga de la interfaz
modelos, error_modelos = get_ollama_models()
if error_modelos:
    print(error_modelos)

#Enviar el texto a Ollama para que nos devuelva el texto resumido
def resumir_texto(texto, temperatura, longitud, modelo):
    len_texto = len(texto.strip())
    if texto.strip() == '' or len_texto < 100:
        raise gr.Error("No hay texto o poco texto")
    if not modelo:
        raise gr.Error("Selecciona un modelo antes de resumir.")

    messages = [
        {"role": "system", "content": f'Realiza un resumen del texto dado con menos de {len_texto}'},
        {"role": "user", "content": texto}
    ]

    client = Client(timeout=300)
    try:
        response = client.chat(
            model = modelo,
            messages = messages,
            options = {
                "temperature": temperatura,
                "num_ctx": longitud
            },
        )
    except ResponseError as error:
        return f'Error de Ollama: {error}'
    except ConnectError as error:
        return f'Error de Connect: {error}'
    except TimeoutException:
        return "La petición ha superado el tiempo de espera"

    texto_resumido = response['message'].content
    if len(texto_resumido.strip()) < len_texto:
        return texto_resumido
    else:
        return 'No ha podido resumir el texto'


#Interfaz de Gradio
demo = gr.Interface(
    fn=resumir_texto,
    inputs=[
        gr.Textbox(label="Texto original", lines=12),
        gr.Slider(value=CONFIG_DATA['temperatura'], minimum=0.1, maximum=1, step=0.1, label="Temperatura"),
        gr.Slider(value=CONFIG_DATA['context_length'], minimum=500, maximum=CONFIG_DATA['context_length'], step=500, label="Longitud"),
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(modelos) > 0:
        demo.launch()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
