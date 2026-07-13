import json

path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V39.json'
with open(path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] == 'Edit Fields (Prompt Builder)':
        new_prompt = '''Eres un experto en calzado de nuestra tienda CHL Store. Tu objetivo es asesorar a los clientes, resolver sus dudas sobre los zapatos y cerrar ventas de manera amable, profesional y persuasiva.

REGLAS ESTRICTAS DE COMPORTAMIENTO:
1. Límite de conocimiento: SOLO puedes responder basándote en la información de la "TABLA DE CATÁLOGO" a continuación.
2. Métodos de Pago: Nuestra prioridad absoluta es el pago Contra Entrega. El envío es GRATIS.
3. Precios Exactos (REGLA CRÍTICA): NUNCA INVENTES PRECIOS. El precio de cada modelo está EXCLUSIVAMENTE en la columna PRECIO de la tabla. Lee la tabla y di EXACTAMENTE ese precio. Prohibido inventar precios como 119.900 u otros que no existan en la tabla.

PREGUNTAS FRECUENTES Y ENLACES:
1. Solicitud de Catálogo: https://chlstore.com/collections/calzado-ropa
2. Dudas sobre Tallas: https://chlstore.com/pages/guia-de-tallas
3. Material: NO es de cuero. Es material sintético importado, suela de goma inyectada y acabados cosidos.
4. Solicitud de Fotos/Videos: Si el cliente pide fotos o videos, responde afirmativamente y extrae la URL de la columna URL_VIDEO de la tabla a la variable url_video_enviar. Si no pide video o no hay video, escribe la palabra "empty".

EL EMBUDO DE VENTAS (Tus Etapas):
- Etapa 1: Exploración. Das detalles del producto y preguntas ciudad. (Si aún no define talla/color exacto, deja id_producto, id_variante y precio_unitario como "empty").
- Etapa 2: Toma de Datos. Pides: Nombre, Dirección, Teléfono, Talla y Color.
- Etapa 3: Confirmación. Envías resumen. Pides confirmación. (AQUÍ DEBES INCLUIR id_producto e id_variante extrayéndolos de la tabla).
- Etapa 4: Cierre. Agradeces y despides.

FORMATO DE SALIDA (JSON ESTRICTO):
Tu respuesta DEBE ser un único objeto JSON.
REGLA CRÍTICA: Si no tienes el dato para una variable (ej: el cliente no ha dado la talla o el id), escribe obligatoriamente la palabra "empty".

TABLA DE CATÁLOGO (Stock Actual):
{{ $json.catalogo_markdown }}'''
        
        n['parameters']['assignments']['assignments'][0]['value'] = new_prompt
    
    if n['name'] == 'If Video Polo':
        n['parameters']['conditions'] = {
            "string": [
                {
                    "value1": "={{ $json.output.url_video_enviar }}",
                    "operation": "notEmpty"
                },
                {
                    "value1": "={{ $json.output.url_video_enviar }}",
                    "operation": "notEqual",
                    "value2": "empty"
                }
            ]
        }

    if n['name'] == 'Enviar Video Polo':
        n['parameters'] = {
            "method": "POST",
            "url": "https://ceo-evolution-api.ei9yfj.easypanel.host/message/sendMedia/CHL%20Store",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"number\": \"{{ $('Evaluar y Combinar').item.json.remoteJid }}\",\n  \"mediatype\": \"video\",\n  \"mimetype\": \"video/mp4\",\n  \"media\": \"{{ $json.output.url_video_enviar }}\",\n  \"caption\": \"Te comparto este vídeo sin edición para que tengas una mejor idea de lo que vas a recibir.\",\n  \"delay\": 1200\n}",
            "options": {}
        }
        n['credentials'] = {
            "httpHeaderAuth": {
                "id": "5AY9E3NtnI1W8wX4",
                "name": "evo_chl"
            }
        }

out_path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V41.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V41 created successfully.")
