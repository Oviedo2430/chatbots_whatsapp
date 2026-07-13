import shutil
import os

# 1. Copy JSON file
src_json = "/Users/carlosoviedo/Desktop/Agente CHL Store/My workflow 5.json"
dest_json = "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/Flujo_Maestro_Estable_Julio_13.json"
shutil.copyfile(src_json, dest_json)

# 2. Add notes to SKILL.md
skill_paths = [
    "/Users/carlosoviedo/Desktop/chatbots_whatsapp/whatsapp-n8n-bot-architect/SKILL.md",
    "/Users/carlosoviedo/.gemini/config/skills/whatsapp-n8n-bot-architect/SKILL.md"
]

append_text = """
### G. Versión Estable (13 de Julio)
**Flujo_Maestro_Estable_Julio_13.json:** Esta es la versión de producción estable confirmada al 13 de Julio de 2026. Contiene todas las correcciones en el Switch Node, el manejo de campos ocultos de Shopify (note_attributes), las reglas de reintento ante caídas de Gemini (Retry on Fail), y el formato exacto de variables y arrays para los envíos a Evolution API.
"""

for sp in skill_paths:
    with open(sp, "a", encoding="utf-8") as f:
        f.write("\n" + append_text)

print("Files updated successfully")
