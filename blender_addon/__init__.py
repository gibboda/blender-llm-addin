bl_info = {
    "name": "BlenderLLMAddin",
    "description": "A utility add-on for Blender that performs specific tasks using LLM.",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Tool Shelf > LLM Add-in",
    "category": "Object",
}

import bpy
import blender_llm_addin


def register():
    blender_llm_addin.register()


def unregister():
    blender_llm_addin.unregister()


if __name__ == "__main__":
    register()
