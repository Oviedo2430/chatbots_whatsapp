import json

path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V39.json"
with open(path, "r", encoding="utf-8") as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] == 'Enviar Video Polo':
        n['parameters'] = {
            "method": "POST",
            "url": "https://ceo-evolution-api.ei9yfj.easypanel.host/message/sendMedia/CHL%20Store",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"number\": \"{{ $('Evaluar y Combinar').item.json.remoteJid }}\",\n  \"mediatype\": \"video\",\n  \"mimetype\": \"video/mp4\",\n  \"media\": \"{{ $json.output.url_video_enviar }}\",\n  \"caption\": \"Te comparto este v\u00eddeo sin edici\u00f3n para que tengas una mejor idea de lo que vas a recibir.\",\n  \"delay\": 1200\n}",
            "options": {}
        }
        n['credentials'] = {
            "httpHeaderAuth": {
                "id": "5AY9E3NtnI1W8wX4",
                "name": "evo_chl"
            }
        }

out_path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V40.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V40 created successfully.")
