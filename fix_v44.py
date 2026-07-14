import json

path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V43.json'
with open(path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Re-wire connections
conns = wf['connections']

# AI Agent goes to all three branches
conns['AI Agent'] = {
    "main": [
        [
            { "node": "Upsert Lead BD", "type": "main", "index": 0 },
            { "node": "If Video Polo", "type": "main", "index": 0 },
            { "node": "Switch", "type": "main", "index": 0 }
        ]
    ]
}

# Upsert Lead BD ends there
conns['Upsert Lead BD'] = {
    "main": [ [] ]
}

# If Video Polo goes to Enviar Video Polo on True, and nothing on False
conns['If Video Polo'] = {
    "main": [
        [ { "node": "Enviar Video Polo", "type": "main", "index": 0 } ],
        []
    ]
}

# Enviar Video Polo ends there
conns['Enviar Video Polo'] = {
    "main": [ [] ]
}

out_path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V44.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V44 created successfully.")
