import json

path41 = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V41.json'
path13 = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_Estable_Julio_13.json'

with open(path41, 'r', encoding='utf-8') as f:
    wf = json.load(f)

with open(path13, 'r', encoding='utf-8') as f:
    wf13 = json.load(f)

old_prompt = ""
old_schema = {}

for n in wf13['nodes']:
    if n['name'] == 'Edit Fields (Prompt Builder)':
        old_prompt = n['parameters']['assignments']['assignments'][0]['value']
    if n['name'] == 'Structured Output Parser':
        old_schema = json.loads(n['parameters']['inputSchema'])

# Add video to prompt
old_prompt = old_prompt.replace(
    '2. Dudas sobre Tallas: Si el cliente consulta por tallas, no está seguro de cuál pedir o pregunta si le quedará bueno el calzado, indícale que tenemos un procedimiento exacto para medir su pie y envíale EXACTAMENTE este enlace con la guía de tallas: https://chlstore.com/pages/guia-de-tallas',
    '2. Dudas sobre Tallas: Si el cliente consulta por tallas, no está seguro de cuál pedir o pregunta si le quedará bueno el calzado, indícale que tenemos un procedimiento exacto para medir su pie y envíale EXACTAMENTE este enlace con la guía de tallas: https://chlstore.com/pages/guia-de-tallas\\n3. Solicitud de Videos: Si el cliente pide explícitamente un video del producto, busca el enlace en la sección "ENLACES DE VIDEO POR MODELO" y cópialo en la variable url_video_enviar.'
)

# Add video to schema
old_schema['properties']['url_video_enviar'] = {
    "type": "string",
    "description": "Si el cliente pide explícitamente un video, copia aquí la URL correspondiente. De lo contrario, deja comillas vacías \"\"."
}

# Apply to V42
for n in wf['nodes']:
    if n['name'] == 'Edit Fields (Prompt Builder)':
        n['parameters']['assignments']['assignments'][0]['value'] = old_prompt
        
    if n['name'] == 'Structured Output Parser':
        n['parameters']['inputSchema'] = json.dumps(old_schema, indent=2)

    if n['name'] == 'Code in JavaScript':
        n['parameters']['jsCode'] = '''let md = "MODELO | VARIANTE (Talla/Color) | PRECIO | ID_PRODUCTO | ID_VARIANTE\\n---|---|---|---|---\\n";
let edges = [];
try {
  edges = $input.first().json.data.products.edges;
} catch(e) {
  edges = [];
}

let videos_md = "\\n\\nENLACES DE VIDEO POR MODELO:\\n";
let has_videos = false;

for (let edge of edges) {
  let p = edge.node;
  let p_id = p.id.split('/').pop();
  let video_url = p.metafield ? p.metafield.value : "";
  
  if (video_url) {
      videos_md += `- ${p.title}: ${video_url}\\n`;
      has_videos = true;
  }
  
  for (let vEdge of p.variants.edges) {
    let v = vEdge.node;
    let v_id = v.id.split('/').pop();
    let price_str = String(v.price).replace('.00', '');
    
    md += `${p.title} | ${v.title} | ${price_str} | ${p_id} | ${v_id}\\n`;
  }
}

if (has_videos) {
    md += videos_md;
}

return [{ json: { catalogo_markdown: md } }];'''

    if n['name'] == 'If Video Polo':
        n['parameters']['conditions'] = {
            "string": [
                {
                    "value1": "={{ $json.output.url_video_enviar }}",
                    "operation": "notEmpty"
                }
            ]
        }

out_path = '/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_V42.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("V42 created successfully.")
