import mediapipe as mp
import cv2
import json
import time
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import sys
EMAIL = sys.argv[1]

response = requests.get(
    "https://tomgestos.xyz/api/get-id",
    params={"email": EMAIL}
)


data = response.json()

# ========= CONFIGURAÇÕES =========
ARQUIVO_GESTOS = "gestos_config.json"
AMAZON_USER_ID = data["userId"]  
API_URL = "https://d1ivl6cbzb.execute-api.us-east-1.amazonaws.com/default/AlexaVirtualButtonsSkillPython"
API_AUTH_TOKEN = "sua-senha-api-padrao-aqui" 
LIMITE_CONTAGEM = 20

# ========= ESTADO =========
ultimo_gesto = ""
contador = {}
ativado = {}
gesto_ingles_para_nome = {}

# ========= FUNÇÕES AUXILIARES =========
class MapeamentoHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(ARQUIVO_GESTOS):
            print("Arquivo de mapeamento modificado. Recarregando...")
            carregar_mapeamento()



def iniciar_monitoramento_json():
    event_handler = MapeamentoHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()


def carregar_mapeamento():
    global gesto_ingles_para_nome, contador, ativado

    if not Path(ARQUIVO_GESTOS).exists():
        print("Arquivo de gestos não encontrado.")
        return

    with open(ARQUIVO_GESTOS, "r") as f:
        dados = json.load(f)


    gesto_ingles_para_nome = {v: k for k, v in dados.items()}


    for gesto in gesto_ingles_para_nome:
        contador[gesto] = 0
        ativado[gesto] = False



def ativar_gesto_amazon(amazon_user_id, nome_original):
    headers = {
        "Authorization": API_AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    print(nome_original)
    payload = {
        "command": "pushcontact",
        "userId": amazon_user_id,
        "param1": nome_original
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✅ Gesto '{nome_original}' ativado com sucesso!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao ativar gesto '{nome_original}':", e)



def callback(res, _, __):
    global ultimo_gesto, contador, ativado

    if not res.gestures:
        return

    gesto_detectado = res.gestures[0][0].category_name
    ultimo_gesto = gesto_detectado
    print(f"Detectado: {gesto_detectado}")


    for g in contador:
        if g != gesto_detectado:
            contador[g] = 0
            ativado[g] = False


    if gesto_detectado in contador:
        contador[gesto_detectado] += 1

        if contador[gesto_detectado] >= LIMITE_CONTAGEM and not ativado[gesto_detectado]:
            nome_original = gesto_ingles_para_nome.get(gesto_detectado)
            if nome_original:
                ativar_gesto_amazon(AMAZON_USER_ID, nome_original)
                ativado[gesto_detectado] = True
            else:
                print(f"Gesto '{gesto_detectado}' não está mapeado no arquivo JSON.")
    else:
        print(f"Gesto '{gesto_detectado}' não está no mapeamento.")



carregar_mapeamento()
iniciar_monitoramento_json()


gesture_recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(
    mp.tasks.vision.GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path='gesture_recognizer.task'),
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        result_callback=callback
    )
)

cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
    gesture_recognizer.recognize_async(mp_image, timestamp_ms=cv2.getTickCount())


    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
#cv2.destroyAllWindows()
