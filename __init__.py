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
from .blender_llm_addin import register, unregister  # Assuming the script defines these

# If the original script doesn't have register/unregister, add minimal ones:
# (paste this if needed - adjust if script already has them)
import bpy

def register():
    # Call whatever registration the original does (e.g. panel, props)
    bpy.utils.register_class(YourPanelClass)  # Replace with actual from original script

def unregister():
    bpy.utils.unregister_class(YourPanelClass)

if __name__ == "__main__":
    register()
