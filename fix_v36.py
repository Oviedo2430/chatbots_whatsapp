import json

path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V36.json"
with open(path, "r", encoding="utf-8") as f:
    wf = json.load(f)

for n in wf['nodes']:
    # Shift existing nodes right
    if n['position'][0] >= 8352 and n['name'] not in ['Upsert Lead BD', 'If Video Polo', 'Enviar Video Polo']:
        n['position'][0] += 600
        
    if n['name'] == 'Upsert Lead BD':
        n['position'] = [8150, 2288]
        
    elif n['name'] == 'If Video Polo':
        n['position'] = [8350, 2288]
        n['typeVersion'] = 2.3
        n['parameters'] = {
            "conditions": {
                "string": [
                    {
                        "value1": "={{ $json.output.url_video_enviar }}",
                        "operation": "notEmpty"
                    }
                ]
            }
        }
        
    elif n['name'] == 'Enviar Video Polo':
        n['position'] = [8550, 2150]

out_path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V37.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V37 created successfully.")
