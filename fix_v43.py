import json

path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V42.json'
with open(path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] == 'If Video Polo':
        n['parameters']['conditions'] = {
            "string": [
                {
                    "value1": "={{ $json.output.url_video_enviar }}",
                    "operation": "startsWith",
                    "value2": "http"
                }
            ]
        }
        
    if n['name'] == 'Enviar Video Polo':
        n['parameters']['jsonBody'] = "={\n  \"number\": \"{{ $('Webhook').item.json.body.data.key.remoteJid }}\",\n  \"mediatype\": \"video\",\n  \"mimetype\": \"video/mp4\",\n  \"media\": \"{{ $json.output.url_video_enviar }}\",\n  \"caption\": \"Te comparto este vídeo sin edición para que tengas una mejor idea de lo que vas a recibir.\",\n  \"delay\": 1200\n}"

out_path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V43.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V43 created successfully.")
