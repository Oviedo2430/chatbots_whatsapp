---
name: whatsapp-n8n-bot-architect
description: Builds advanced WhatsApp chatbots using n8n, Evolution API, Supabase, and Shopify. It understands n8n Switch node item pairing quirks, Evolution API payload strictness (labels, trailing spaces, array unwrapping), and Supabase bot pausing systems.
---

# Instrucciones de la Habilidad: Arquitecto de Bots WhatsApp (n8n + Evolution API + Supabase + Shopify)

Utiliza esta habilidad cuando el usuario solicite crear o modificar un flujo de n8n para un chatbot de WhatsApp utilizando Evolution API, con integraciones de base de datos (Supabase) y tiendas e-commerce (Shopify).

## 1. Arquitectura del Flujo (Plantilla Maestra)
La arquitectura estándar consta de:
- **Webhook de Entrada**: Recibe mensajes entrantes de Evolution API (`messages.upsert` o `labels.association`).
- **Validación de Pausa (Supabase)**: Nodo Postgres que consulta si el número (`remoteJid`) está en la tabla `contactos_pausados`. Si está, el flujo se detiene (usando un Switch).
- **IA (Gemini/OpenAI)**: Procesa el mensaje. Es crucial usar un nodo `Wait` o lógica de `debounce` antes de la IA si los usuarios mandan mensajes fragmentados, para agruparlos en un solo bloque y evitar respuestas duplicadas.
- **Creación de Orden (Shopify)**: Nodo HTTP Request para crear la orden usando los datos extraídos por la IA.
- **Manejo de Etiquetas (Evolution API)**: Nodos HTTP para leer (`findLabels`) y asignar (`handleLabel`) etiquetas.
- **Base de Datos (Supabase)**: Inserción del contacto en `contactos_pausados` tras generar la orden para evitar que el bot responda automáticamente cuando se está confirmando el pago.

## 2. Lecciones Críticas y Quirks (Errores a evitar)

### A. n8n: El "Switch Node" y la pérdida de Pairing
**Problema:** Al pasar datos a través de un nodo `Switch`, n8n rompe la vinculación (item pairing) con nodos anteriores. Si intentas usar `$('AI Agent').item.json.variable` en un nodo HTTP posterior al Switch, n8n arrojará un error y el JSON Body se corromperá.
**Solución:** Extrae los datos y pásalos hacia adelante (haciendo que el Switch envíe todos los datos necesarios en su `output`). Luego, en el nodo HTTP, usa directamente `$json.variable` en lugar de referenciar al nodo original de IA.

### B. Shopify: Variables y Endpoint
**Endpoint Exacto:** Verifica SIEMPRE que la URL HTTP de Shopify sea exactamente la de la tienda real, por ejemplo: `https://[NOMBRE_TIENDA].myshopify.com/admin/api/[VERSION]/orders.json`. Si usas un nombre de tienda de ejemplo (ej. `chl-store`), la API arrojará `404 Not Found`.
**Tipos Numéricos y JSON Parsing:** Las variables dinámicas en el JSON Body para IDs (como `product_id` o `variant_id`) deben ser números sin comillas. Para evitar errores de validación JSON en la interfaz de n8n, **siempre configura el campo JSON Body en "Expression Mode" (añadiendo un `=` al principio del campo)** o usa el modo "Using Fields" en el nodo HTTP Request.

### C. Evolution API: URLs y Etiquetas (labelId)
**Espacios en la URL (404 Error):** Nunca dejes espacios en blanco al final de la variable `instance` en la URL. `CHL%20Store%20` o `CHL Store ` causará un error `404 - The instance does not exist`. La URL debe terminar exactamente en el nombre de la instancia (ej. `.../findLabels/CHL%20Store`).
**Payload de handleLabel:** El endpoint `handleLabel` requiere **obligatoriamente** 3 propiedades en la raíz del JSON:
- `number`: (String) El número de teléfono, ej. `{{ $json.body.data.key.remoteJid }}`. **No uses `remoteJid` como el nombre de la variable, debes enviarla bajo el nombre `number`.**
- `labelId`: (String/Number) El ID numérico de la etiqueta.
- `action`: (String) Debe ser `"add"` o `"remove"`.

**Obtención de labelId (findLabels):**
El endpoint `findLabels` devuelve un array de etiquetas. En n8n, este array se divide automáticamente en múltiples "ítems" individuales.
Para encontrar el ID de una etiqueta específica (ej. "Pausa BOT") entre los múltiples ítems devueltos, no uses `.json.filter` (fallará con error `undefined`). Usa la función `.all()` para buscar en todo el historial del nodo:
`{{ $('HTTP Request (Get Labels)').all().find(item => item.json.name === 'Pausa BOT').json.id }}`

**Multi-ejecución y Execute Once:** Debido a que `findLabels` devuelve múltiples ítems, el siguiente nodo (`handleLabel`) se ejecutará tantas veces como etiquetas haya (ej. 7 veces). Para evitar inundar la API o la base de datos, **debes activar la opción "Execute Once" (Ejecutar una vez)** en los ajustes (Settings) del nodo `handleLabel`.


### D. Evolution API: sendText y el error 400 Bad Request
**Estructura del Payload:** Al usar el endpoint `message/sendText/`, algunas versiones de la API rechazan el uso de `jsonBody` con `textMessage: { text: ... }` arrojando el error `instance requires property "text"`. Para solucionarlo, usa la opción **"Using Fields"** (o `bodyParameters`) y envía la variable `text` directamente en la raíz junto con `number` y `options`.
**Sintaxis de Expresiones en n8n:** Al escribir expresiones a mano en un campo, n8n evalúa el contenido de `{{ }}`. Si escribes un `=` antes de las llaves (`={{ }}`) de forma manual en un campo de texto en n8n, el sistema lo interpretará literalmente y concatenará el `=` al resultado (por ejemplo, `=573000000000@s.whatsapp.net`), lo que causará que la API de Evolution devuelva un error de que el número no existe. El `=` es solo un indicador visual de la interfaz de n8n.

### E. Shopify: Extracción de Datos y URLs
**Atributos Ocultos (note_attributes):** En muchas tiendas de Shopify, si el formulario de pago está modificado o usa aplicaciones de terceros, campos críticos como el teléfono o el nombre no vienen en `$json.shipping_address.phone`, sino dentro de un array llamado `note_attributes`. Es necesario usar un nodo de código JavaScript para iterar sobre `note_attributes` y extraer el valor correcto usando `.find(a => a.name === 'Celular con Whatsapp')`.
**Error 404 en Creación de Orden:** Si el nodo HTTP Request para crear una orden (`/orders.json`) devuelve un `404 Not Found`, hay dos causas principales:
1. La URL tiene un dominio inventado o incorrecto (ej. `chl-store.myshopify.com` vs `chlstore-colombia.myshopify.com`). Verifica el dominio real.
2. El `variant_id` o `product_id` extraído por la IA no existe en la tienda. Verifica qué números exactos devolvió la IA.

### F. Ingeniería de Prompts (FAQ y Enlaces)
**Manejo de Preguntas Frecuentes:** Si los clientes piden catálogos o guías de tallas repetidamente, es altamente recomendable añadir una sección de "PREGUNTAS FRECUENTES Y ENLACES" en el prompt del sistema de la IA (antes del Embudo de Ventas) dándole reglas estrictas para enviar URLs exactas cuando detecte estas intenciones, separadas por `|||` para enviarse en globos distintos.
