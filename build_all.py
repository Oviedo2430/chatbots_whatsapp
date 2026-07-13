import json

# ==========================================
# 1. Update Flujo_Maestro
# ==========================================
path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_Estable_Julio_13.json"
with open(path, "r", encoding="utf-8") as f:
    wf = json.load(f)

# Update Prompt
new_prompt = """Eres un experto en calzado de nuestra tienda CHL Store. Tu objetivo es asesorar a los clientes, resolver sus dudas sobre los zapatos y cerrar ventas de manera amable, profesional y persuasiva.

REGLAS ESTRICTAS DE COMPORTAMIENTO:
1. Límites de conocimiento: SOLO puedes responder basándote en la información de la "TABLA DE CATÁLOGO" a continuación. Si el cliente pregunta por un modelo, color o talla que NO ESTÁ en la tabla, DEBES decirle que no está disponible.
2. Métodos de Pago: Nuestra prioridad absoluta es el pago Contra Entrega. El envío es GRATIS.
3. Precios Exactos (REGLA CRÍTICA): El precio real de cada zapato está en la columna PRECIO de la tabla. DEBES decir EXACTAMENTE ese precio. Extrae el precio en la variable precio_unitario.

PREGUNTAS FRECUENTES Y ENLACES (IMPORTANTE):
1. Solicitud de Catálogo: Si el cliente quiere ver el catálogo completo o más opciones, indícale amablemente que en nuestra tienda virtual están disponibles todos nuestros modelos y envíale EXACTAMENTE este enlace: https://chlstore.com/collections/calzado-ropa
2. Dudas sobre Tallas: Si el cliente consulta por tallas, no está seguro de cuál pedir o pregunta si le quedará bueno el calzado, indícale que tenemos un procedimiento exacto para medir su pie y envíale EXACTAMENTE este enlace con la guía de tallas: https://chlstore.com/pages/guia-de-tallas
3. Material y Fabricación: Si preguntan si es de cuero, o por el material, DEBES responder categóricamente que NO es de cuero. Explica que es de material sintético importado, la suela es de goma inyectada y los acabados son cosidos para mayor duración.
4. Solicitud de Fotos/Videos del Polo Club: Si el cliente pide fotos, videos o ver cómo es el modelo Polo Club en la vida real, responde afirmativamente y ASEGÚRATE de devolver la variable "enviar_video_polo" como true en el JSON final. El sistema adjuntará el video automáticamente.

EL EMBUDO DE VENTAS (Tus Etapas):
- Etapa 1: Exploración. Das detalles del producto y preguntas ciudad.
- Etapa 2: Toma de Datos. Pides: Nombre, Dirección, Teléfono, Talla y Color.
- Etapa 3: Confirmación. Envías resumen estructurado. Pides confirmación final.
- Etapa 4: Cierre. Agradeces y despides.

FORMATO DE SALIDA (JSON ESTRICTO):
Tu respuesta DEBE ser siempre un único objeto JSON válido.
REGLA CRÍTICA: Todos los campos extraídos exigen texto (string). Si el cliente no te ha dado un dato, DEBES escribir comillas vacías "". NUNCA uses null ni la palabra "empty".
REGLA WHATSAPP: Nunca uses salto de linea literal en el mensaje_whatsapp. Usa comas para listar.

REGLA DE MENSAJES CORTOS: Tus respuestas NO deben ser un solo bloque de texto. Separa cada idea o párrafo usando el separador exacto '|||'. Ejemplo: '¡Hola! ||| ¿Qué talla buscas?'. n8n enviará cada bloque como un globo de WhatsApp distinto.

REGLA DE IDs (CRÍTICO PARA SHOPIFY): En la Etapa 3 y Etapa 4, es OBLIGATORIO que incluyas el 'id_producto' y el 'id_variante'. Búscalos en la tabla de catálogo (columnas ID_PRODUCTO e ID_VARIANTE) usando la talla y color exactos que eligió el cliente. NUNCA los dejes vacíos.

TABLA DE CATÁLOGO (Stock Actual):
{{ $json.catalogo_markdown }}"""

for n in wf["nodes"]:
    if n["name"] == "Edit Fields (Prompt Builder)":
        n["parameters"]["assignments"]["assignments"][0]["value"] = new_prompt
    if "outputParserStructured" in n["type"]:
        schema = json.loads(n["parameters"]["inputSchema"])
        schema["properties"]["enviar_video_polo"] = {"type": "boolean", "description": "Ponlo en true si el cliente quiere ver un video o foto del modelo Polo Club."}
        n["parameters"]["inputSchema"] = json.dumps(schema, indent=2)

# Insert new nodes:
upsert_node = {
  "parameters": {
    "operation": "upsert",
    "schema": "public",
    "table": "leads_whatsapp",
    "columns": "numero_telefono,nombre,producto_interes,estado,ultima_interaccion",
    "values": "={{ $('Evaluar y Combinar').item.json.remoteJid }},{{ $json.output.datos_extraidos.nombre || '' }},{{ $json.output.datos_extraidos.referencia || '' }},{{ ($json.output.estado_embudo.toLowerCase().includes('4') || $json.output.estado_embudo.toLowerCase().includes('cierre') || $json.output.estado_embudo.toLowerCase().includes('venta')) ? 'venta_concretada' : 'activo' }},now()",
    "upsertUpdateColumns": "nombre,producto_interes,estado,ultima_interaccion"
  },
  "id": "node-upsert-lead",
  "name": "Upsert Lead BD",
  "type": "n8n-nodes-base.postgres",
  "typeVersion": 2.3,
  "position": [1000, 200], 
  "credentials": {
    "postgres": {
      "id": "ouooyDBAMbCOLds6",
      "name": "DB_CHLStore"
    }
  }
}

if_video_node = {
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": True,
        "leftValue": "",
        "typeValidation": "strict"
      },
      "conditions": [
        {
          "id": "condition-1",
          "leftValue": "={{ $json.output.enviar_video_polo }}",
          "rightValue": True,
          "operator": {
            "type": "boolean",
            "operation": "true",
            "singleValue": True
          }
        }
      ],
      "combinator": "and"
    },
    "options": {}
  },
  "id": "node-if-video",
  "name": "If Video Polo",
  "type": "n8n-nodes-base.if",
  "typeVersion": 3,
  "position": [1200, 200]
}

send_video_node = {
  "parameters": {
    "method": "POST",
    "url": "={{ $('Webhook').item.json.headers.host.includes('evolution') ? 'https://' + $('Webhook').item.json.headers.host + '/message/sendMedia/' + $('Webhook').item.json.instance : 'http://YOUR_EVOLUTION_URL/message/sendMedia/' + $('Webhook').item.json.instance }}",
    "sendHeaders": True,
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "={{ $('Webhook').item.json.apikey || 'B6D711FCDE4D4FD5936544120E713976' }}"
        }
      ]
    },
    "sendBody": True,
    "specifyBody": "json",
    "jsonBody": "={\n  \"number\": \"{{ $('Evaluar y Combinar').item.json.remoteJid }}\",\n  \"mediatype\": \"video\",\n  \"mimetype\": \"video/mp4\",\n  \"media\": \"https://storage.googleapis.com/ciider/Blanco_Azul.mp4\",\n  \"caption\": \"Te comparto este vídeo de nuestros Polo, sin edición, para que tengas una mejor ídea de lo que vas a recibir\",\n  \"delay\": 1200\n}",
    "options": {}
  },
  "id": "node-send-video",
  "name": "Enviar Video Polo",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.1,
  "position": [1400, 100]
}

wf["nodes"].extend([upsert_node, if_video_node, send_video_node])

if "AI Agent" in wf["connections"]:
    wf["connections"]["AI Agent"] = {
        "main": [
            [
                {"node": "Upsert Lead BD", "type": "main", "index": 0}
            ]
        ]
    }

wf["connections"]["Upsert Lead BD"] = {
    "main": [
        [{"node": "If Video Polo", "type": "main", "index": 0}]
    ]
}

wf["connections"]["If Video Polo"] = {
    "main": [
        [{"node": "Enviar Video Polo", "type": "main", "index": 0}], 
        [{"node": "Switch", "type": "main", "index": 0}] 
    ]
}

wf["connections"]["Enviar Video Polo"] = {
    "main": [
        [{"node": "Switch", "type": "main", "index": 0}]
    ]
}

out_path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V35.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)


# ==========================================
# 2. Build Reminder Flow 24h
# ==========================================
reminder_wf = {
  "name": "Recordatorio 24h WhatsApp",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours"
            }
          ]
        }
      },
      "id": "node-schedule",
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [0, 0]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT numero_telefono, nombre, producto_interes FROM leads_whatsapp WHERE estado != 'venta_concretada' AND recordatorio_enviado = false AND ultima_interaccion >= (NOW() - INTERVAL '25 hours') AND ultima_interaccion <= (NOW() - INTERVAL '24 hours');"
      },
      "id": "node-get-leads",
      "name": "Get Leads 24h",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.3,
      "position": [200, 0],
      "credentials": {
        "postgres": {
          "id": "ouooyDBAMbCOLds6",
          "name": "DB_CHLStore"
        }
      }
    },
    {
      "parameters": {
        "batchSize": 1,
        "options": {}
      },
      "id": "node-loop",
      "name": "Loop Mensajes",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [400, 0]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://TU_EVOLUTION_API_URL/message/sendText/TU_INSTANCIA",
        "sendHeaders": True,
        "headerParameters": {
          "parameters": [
            {
              "name": "apikey",
              "value": "TU_API_KEY"
            }
          ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={\n  \"number\": \"{{ $json.numero_telefono }}\",\n  \"options\": {\n    \"delay\": 1200,\n    \"presence\": \"composing\"\n  },\n  \"text\": \"Hola {{ $json.nombre ? $json.nombre : '' }}, ayer preguntaste por {{ $json.producto_interes ? $json.producto_interes : 'nuestro calzado' }}, estamos acá para resolver tus dudas, ¿continuamos con la conversación?\"\n}",
        "options": {}
      },
      "id": "node-send-reminder",
      "name": "Enviar Recordatorio",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [600, 0]
    },
    {
      "parameters": {
        "operation": "update",
        "schema": "public",
        "table": "leads_whatsapp",
        "updateKey": "numero_telefono",
        "columns": "recordatorio_enviado",
        "values": "={{ $json.numero_telefono }},true"
      },
      "id": "node-update-lead",
      "name": "Marcar Enviado BD",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.3,
      "position": [800, 0],
      "credentials": {
        "postgres": {
          "id": "ouooyDBAMbCOLds6",
          "name": "DB_CHLStore"
        }
      }
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [{"node": "Get Leads 24h", "type": "main", "index": 0}]
      ]
    },
    "Get Leads 24h": {
      "main": [
        [{"node": "Loop Mensajes", "type": "main", "index": 0}]
      ]
    },
    "Loop Mensajes": {
      "main": [
        [{"node": "Enviar Recordatorio", "type": "main", "index": 0}]
      ]
    },
    "Enviar Recordatorio": {
      "main": [
        [{"node": "Marcar Enviado BD", "type": "main", "index": 0}]
      ]
    },
    "Marcar Enviado BD": {
      "main": [
        [{"node": "Loop Mensajes", "type": "main", "index": 0}]
      ]
    }
  }
}

rem_path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Recordatorio_24h.json"
with open(rem_path, "w", encoding="utf-8") as f:
    json.dump(reminder_wf, f, indent=2, ensure_ascii=False)

print("Created V35 and Reminder flows successfully.")
