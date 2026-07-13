import json

path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V37.json"
with open(path, "r", encoding="utf-8") as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] == 'Upsert Lead BD':
        n['parameters'] = {
            "operation": "executeQuery",
            "query": "INSERT INTO leads_whatsapp (numero_telefono, nombre, producto_interes, estado, ultima_interaccion)\\nVALUES (\\n  '{{ $('Evaluar y Combinar').item.json.remoteJid }}',\\n  '{{ ($json.output.datos_extraidos.nombre || \"\").replace(/'/g, \"''\") }}',\\n  '{{ ($json.output.datos_extraidos.referencia || \"\").replace(/'/g, \"''\") }}',\\n  '{{ ($json.output.estado_embudo.toLowerCase().includes(\"4\") || $json.output.estado_embudo.toLowerCase().includes(\"cierre\") || $json.output.estado_embudo.toLowerCase().includes(\"venta\")) ? \"venta_concretada\" : \"activo\" }}',\\n  now()\\n)\\nON CONFLICT (numero_telefono)\\nDO UPDATE SET\\n  nombre = EXCLUDED.nombre,\\n  producto_interes = EXCLUDED.producto_interes,\\n  estado = EXCLUDED.estado,\\n  ultima_interaccion = EXCLUDED.ultima_interaccion;",
            "options": {}
        }

out_path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V38.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V38 created successfully.")
