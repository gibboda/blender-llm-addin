---
agent: ask
model: GPT-5.2-Codex
description: Instructions for creating a Blender add-on with proper __init__.py file for Blender 5.x.x and later.
---
# Blender Add-on Creation for Blender 5.x.x and Later

You are an expert in Blender add-on development. Create a new Blender add-on with the following specifications:
- Name: BlenderLLMAddin
- Description: A utility add-on for Blender that performs specific tasks using LLM.
- Version: 1.0
- Author: Your Name
- Blender Version: 5.x.x and later

Ensure the `__init__.py` file includes:
```python
bl_info = {
    "name": "BlenderLLMAddin",
    "description": "A utility add-on for Blender that performs specific tasks using LLM.",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (5, 0, 0),  # Use a base version that is compatible with 5.x.x and later
    "location": "View3D > Tool Shelf > LLM Add-in",
    "category": "Object"
}

import bpy

def register():
    # Register all necessary components here
    pass

def unregister():
    # Unregister all necessary components here
    pass

if __name__ == "__main__":
    register()