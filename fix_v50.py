import json

path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V49.json'
with open(path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] == 'If Video Polo':
        n['typeVersion'] = 1
        n['parameters']['conditions'] = {
            "boolean": [
                {
                    "value1": "={{ !!$json.output.url_video_enviar && $json.output.url_video_enviar.indexOf('http') !== -1 }}",
                    "value2": True
                }
            ]
        }

out_path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V50.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print('V50 created successfully.')
