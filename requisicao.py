import requests
import time
import json
import sys

EMAIL = sys.argv[1]

response = requests.get(
    "https://tomgestos.xyz/api/get-id",
    params={"email": EMAIL}
)


data = response.json()


AMAZON_USER_ID = data["id"]
ARQUIVO_GESTOS = "gestos_config.json"


MAPEAMENTO_GESTOS = {
    "Aberta": "Open_Palm",
    "fechado": "Closed_Fist",
    "amor": "ILoveYou",
    "Apontando": "Pointing_Up",
    "Joia": "Thumb_Up",
    "dislike": "Thumb_Down",
    "Vitoria": "Victory"
}

while True:
    try:
        response = requests.get(
            "https://tomgestos.xyz/api/get-config/",
            params={"amazon_user_id": AMAZON_USER_ID}
        )
        data = response.json()
        print("Gestos configurados:", data)

        gestos_raw = data.get("gestures", {})


        gestos_convertidos = {
            nome_original: MAPEAMENTO_GESTOS[nome_original]
            for nome_original in gestos_raw
            if nome_original in MAPEAMENTO_GESTOS
        }

        with open(ARQUIVO_GESTOS, "w", encoding="utf-8") as f:
            json.dump(gestos_convertidos, f, ensure_ascii=False, indent=2)

        print("Gestos salvos no JSON:", gestos_convertidos)

    except Exception as e:
        print("Erro:", e)

    time.sleep(10)
