# __init__.py - Makes this a Blender add-on

bl_info = {
    "name": "LLM Add-in (Text-to-3D with Ollama/OpenAI)",
    "author": "mac999 + your tweaks",
    "version": (1, 0),
    "blender": (4, 0, 0),  # Works on 5.0 too
    "location": "View3D > Sidebar > LLM",
    "description": "Text-to-3D via Ollama or OpenAI in Blender",
    "category": "3D View",
}

# Import the main logic
from .blender_llm_addin import register, unregister

if __name__ == "__main__":
    register()
