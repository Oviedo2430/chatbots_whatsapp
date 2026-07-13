import json
import re

path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V35.json"
with open(path, "r", encoding="utf-8") as f:
    wf = json.load(f)

graphql_node = {
  "parameters": {
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "shopifyOAuth2Api",
    "method": "POST",
    "url": "https://chlstore-colombia.myshopify.com/admin/api/2023-10/graphql.json",
    "sendBody": True,
    "specifyBody": "json",
    "jsonBody": "={\n  \"query\": \"{ products(first: 50, query: \\\"product_type:'Calzado'\\\") { edges { node { id title metafield(namespace: \\\"custom\\\", key: \\\"video_whatsapp\\\") { value } variants(first: 20) { edges { node { id title price } } } } } } }\"\n}",
    "options": {}
  },
  "id": "node-graphql-shopify",
  "name": "GraphQL Shopify",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.1,
  "position": [7216, 2288],
  "credentials": {
    "shopifyOAuth2Api": {
      "id": "PTC2dsmLSULOXKiA",
      "name": "Shopify CHL Store"
    }
  }
}

new_js = """let md = "MODELO | VARIANTE (Talla/Color) | PRECIO | URL_VIDEO | ID_PRODUCTO | ID_VARIANTE\\n---|---|---|---|---|---\\n";
let edges = [];
try {
  edges = $input.first().json.data.products.edges;
} catch(e) {
  edges = [];
}

for (let edge of edges) {
  let p = edge.node;
  let p_id = p.id.split('/').pop();
  let video_url = p.metafield ? p.metafield.value : "";
  
  for (let vEdge of p.variants.edges) {
    let v = vEdge.node;
    let v_id = v.id.split('/').pop();
    let price_str = String(v.price).replace('.00', '');
    
    md += `${p.title} | ${v.title} | ${price_str} | ${video_url} | ${p_id} | ${v_id}\\n`;
  }
}
return [{ json: { catalogo_markdown: md } }];
"""

new_prompt = """Eres un experto en calzado de nuestra tienda CHL Store. Tu objetivo es asesorar a los clientes, resolver sus dudas sobre los zapatos y cerrar ventas de manera amable, profesional y persuasiva.

REGLAS ESTRICTAS DE COMPORTAMIENTO:
1. Límites de conocimiento: SOLO puedes responder basándote en la información de la "TABLA DE CATÁLOGO" a continuación. Si el cliente pregunta por un modelo, color o talla que NO ESTÁ en la tabla, DEBES decirle que no está disponible.
2. Métodos de Pago: Nuestra prioridad absoluta es el pago Contra Entrega. El envío es GRATIS.
3. Precios Exactos (REGLA CRÍTICA): El precio real de cada zapato está en la columna PRECIO de la tabla. DEBES decir EXACTAMENTE ese precio. Extrae el precio en la variable precio_unitario.

PREGUNTAS FRECUENTES Y ENLACES (IMPORTANTE):
1. Solicitud de Catálogo: Si el cliente quiere ver el catálogo completo o más opciones, indícale amablemente que en nuestra tienda virtual están disponibles todos nuestros modelos y envíale EXACTAMENTE este enlace: https://chlstore.com/collections/calzado-ropa
2. Dudas sobre Tallas: Si el cliente consulta por tallas, indícale que tenemos un procedimiento exacto para medir su pie y envíale EXACTAMENTE este enlace: https://chlstore.com/pages/guia-de-tallas
3. Material y Fabricación: Si preguntan si es de cuero, o por el material, DEBES responder categóricamente que NO es de cuero. Explica que es de material sintético importado, la suela es de goma inyectada y los acabados son cosidos para mayor duración.
4. Solicitud de Fotos/Videos: Si el cliente pide fotos, videos o ver cómo es el calzado en la vida real, responde afirmativamente y ASEGÚRATE de extraer la URL de la columna URL_VIDEO de ese producto en específico y devolverla en la variable "url_video_enviar". El sistema adjuntará el video automáticamente. Si la columna URL_VIDEO está vacía para ese zapato, dile amablemente que por el momento no cuentas con un video de ese modelo.

EL EMBUDO DE VENTAS (Tus Etapas):
- Etapa 1: Exploración. Das detalles del producto y preguntas ciudad.
- Etapa 2: Toma de Datos. Pides: Nombre, Dirección, Teléfono, Talla y Color.
- Etapa 3: Confirmación. Envías resumen estructurado. Pides confirmación final.
- Etapa 4: Cierre. Agradeces y despides.

FORMATO DE SALIDA (JSON ESTRICTO):
Tu respuesta DEBE ser siempre un único objeto JSON válido.
REGLA CRÍTICA: Todos los campos extraídos exigen texto (string). Si el cliente no te ha dado un dato, DEBES escribir comillas vacías "". NUNCA uses null ni la palabra "empty".
REGLA WHATSAPP: Nunca uses salto de linea literal en el mensaje_whatsapp. Usa comas para listar.

REGLA DE MENSAJES CORTOS: Tus respuestas NO deben ser un solo bloque de texto. Separa cada idea o párrafo usando el separador exacto '|||'.

REGLA DE IDs (CRÍTICO PARA SHOPIFY): En la Etapa 3 y Etapa 4, es OBLIGATORIO que incluyas el 'id_producto' y el 'id_variante'. Búscalos en la tabla de catálogo (columnas ID_PRODUCTO e ID_VARIANTE) usando la talla y color exactos que eligió el cliente.

TABLA DE CATÁLOGO (Stock Actual):
{{ $json.catalogo_markdown }}"""

for i, n in enumerate(wf["nodes"]):
    if n["name"] == "Get many products":
        wf["nodes"][i] = graphql_node
    elif n["name"] == "Code in JavaScript":
        n["parameters"]["jsCode"] = new_js
    elif n["name"] == "Edit Fields (Prompt Builder)":
        n["parameters"]["assignments"]["assignments"][0]["value"] = new_prompt
    elif "outputParserStructured" in n["type"]:
        schema = json.loads(n["parameters"]["inputSchema"])
        if "enviar_video_polo" in schema["properties"]:
            del schema["properties"]["enviar_video_polo"]
        schema["properties"]["url_video_enviar"] = {"type": "string", "description": "Si el cliente pide video, pega aquí la URL_VIDEO exacta de la tabla. Si no hay o no pide, déjalo vacío \"\"."}
        n["parameters"]["inputSchema"] = json.dumps(schema, indent=2)
    elif n["name"] == "If Video Polo":
        n["parameters"]["conditions"]["conditions"][0] = {
            "id": "condition-1",
            "leftValue": "={{ $json.output.url_video_enviar }}",
            "rightValue": "",
            "operator": {
                "type": "string",
                "operation": "notEmpty",
                "singleValue": True
            }
        }
    elif n["name"] == "Enviar Video Polo":
        n["parameters"]["jsonBody"] = "={\n  \"number\": \"{{ $('Evaluar y Combinar').item.json.remoteJid }}\",\n  \"mediatype\": \"video\",\n  \"mimetype\": \"video/mp4\",\n  \"media\": \"{{ $json.output.url_video_enviar }}\",\n  \"caption\": \"Te comparto este vídeo sin edición para que tengas una mejor idea de lo que vas a recibir.\",\n  \"delay\": 1200\n}"

if "Get many products" in wf["connections"]:
    wf["connections"]["GraphQL Shopify"] = wf["connections"]["Get many products"]
    del wf["connections"]["Get many products"]

for k, targets in wf["connections"].items():
    for mode, links in targets.items():
        for link in links:
            if link["node"] == "Get many products":
                link["node"] = "GraphQL Shopify"


out_path = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V36.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V36 created successfully.")
