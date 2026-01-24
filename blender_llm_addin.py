# title: Blender AI LLM Addin for Text to 3D Graphics Model
# version: 1.0.0
# date: 2025-1-26
# authors: Taewook Kang
# email: laputa99999@gmail.com
# description: this is a Blender AI LLM Addin for generating Blender Python code using AI models like ChatGPT, Gemma, Llama, etc.
import os, re, textwrap, ast
import bpy

# Determine the addon ID so that it always matches the module name Blender uses.
# Prefer __package__ (set when loaded as an addon), otherwise fall back to the
# filename stem instead of "__main__" to keep preferences registration consistent.
ADDON_ID = __package__ or os.path.splitext(os.path.basename(__file__))[0]
KEYRING_SERVICE = f"{ADDON_ID}.openai"

try:
	import keyring
	KEYRING_AVAILABLE = True
except Exception:
	keyring = None
	KEYRING_AVAILABLE = False


def get_addon_prefs():
	try:
		preferences = bpy.context.preferences
	except AttributeError:
		return None
	if not preferences:
		return None
	addon = preferences.addons.get(ADDON_ID)
	if not addon:
		return None
	return addon.preferences

def get_openai_api_key(prefs):
	if prefs and KEYRING_AVAILABLE:
		try:
			stored_key = keyring.get_password(KEYRING_SERVICE, "api_key")
			if stored_key:
				return stored_key
		except Exception as exc:
			print(f"[LLM Addon] Failed to read API key from keyring: {exc}")
	if prefs:
		pref_key = (prefs.openai_api_key or "").strip()
		if pref_key:
			return pref_key
	env_key = os.getenv("OPENAI_API_KEY")
	return (env_key or "").strip() or None


class LLMAddonPreferences(bpy.types.AddonPreferences):
	bl_idname = ADDON_ID

	def _store_openai_api_key(self, context):
		if not KEYRING_AVAILABLE:
			return
		api_key = (self.openai_api_key or "").strip()
		if not api_key:
			# Clearing the field should remove any previously stored key from the keyring.
			try:
				# Check if key exists before attempting deletion to avoid unnecessary exceptions
				existing_key = keyring.get_password(KEYRING_SERVICE, "api_key")
				if existing_key:
					keyring.delete_password(KEYRING_SERVICE, "api_key")
			except Exception as exc:
				print(f"[LLM Addon] Failed to delete API key from keyring: {exc}")
			return
		try:
			keyring.set_password(KEYRING_SERVICE, "api_key", api_key)
		except Exception as exc:
			print(f"[LLM Addon] Failed to store API key in keyring: {exc}")

	openai_api_key: bpy.props.StringProperty(
		name="OpenAI API Key",
		subtype='PASSWORD',
		description="Your OpenAI API key (stored in the system keyring when available)",
		options={'SKIP_SAVE'},
		update=_store_openai_api_key,
	)
	openai_model: bpy.props.StringProperty(
		name="OpenAI Model",
		default="gpt-4o",
	)

	def draw(self, context):
		layout = self.layout
		layout.label(text="OpenAI Settings")
		if KEYRING_AVAILABLE:
			layout.label(text="API key is stored in the system keyring", icon='INFO')
		else:
			layout.label(
				text="Keyring unavailable; API key will not be saved. Set OPENAI_API_KEY env var instead.",
				icon='ERROR',
			)
		layout.prop(self, "openai_api_key")
		layout.prop(self, "openai_model")

# Create Blender UI
class OBJECT_PT_CustomPanel(bpy.types.Panel):
	bl_label = "AI Model Selector"
	bl_idname = "OBJECT_PT_custom_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "LLM"

	def draw(self, context):
		layout = self.layout
		layout.label(text="Select Model:")
		layout.prop(context.scene, "ai_model", text="")
		layout.label(text="User Prompt:")
		layout.prop(context.scene, "user_prompt", text="")
		layout.operator("object.submit_prompt", text="Submit")

# Blender event operator
class OBJECT_OT_SubmitPrompt(bpy.types.Operator):
	bl_label = "Submit Prompt"
	bl_idname = "object.submit_prompt"

	def execute(self, context):
		option = context.scene.ai_model
		user_prompt = context.scene.user_prompt
		if not user_prompt.strip():
			self.report({'ERROR'}, "Please enter a prompt before submitting.")
			return {'CANCELLED'}
		if option == 'chatgpt':
			prefs = get_addon_prefs()
			if not prefs or not getattr(prefs, "openai_api_key", "").strip():
				self.report({'ERROR'}, "OpenAI API key is missing. Set it in Add-on Preferences.")
				return {'CANCELLED'}
		# Basic validation for non-ChatGPT model types that may require an Ollama server URL.
		# This avoids obvious misconfiguration before attempting to call gen_code and
		# automatically applies to any future non-ChatGPT models without needing to update a hardcoded list.
		elif option and option != 'chatgpt':
			ollama_host = os.getenv("OLLAMA_HOST")
			if not ollama_host:
				self.report(
					{'WARNING'},
					"Ollama server URL not set. If connection fails, set the OLLAMA_HOST environment variable."
				)
		try:
			success = gen_code(
				option,
				'coding Blender python program using bpy, basic grammar without Explanation, "#" inline comments, complicated grammar like lambda and function under user request. do not delete the previous objects. user request is',
				user_prompt,
			)
		except Exception as exc:
			# Handle unexpected failures from gen_code gracefully instead of raising unhandled exceptions.
			print(f"[LLM Addon] gen_code failed for model '{option}': {exc}")
			success = False
		if success:
			self.report({'INFO'}, "Prompt executed successfully.")
		else:
			self.report({'ERROR'}, "Prompt execution failed. Check the system console for details.")

		return {'FINISHED' if success else 'CANCELLED'}

# Blender widget registration
def register():
	bpy.utils.register_class(LLMAddonPreferences)
	bpy.utils.register_class(OBJECT_PT_CustomPanel)
	bpy.utils.register_class(OBJECT_OT_SubmitPrompt)

	bpy.types.Scene.ai_model = bpy.props.EnumProperty(
		name="AI Model",
		items=[
				('chatgpt', "ChatGPT", ""),
				('gemma2', "Gemma", ""),
				('llama3.2', "llama", ""),
				('codellama', "codellama", ""),
				('qwen2.5-coder:3b', "qwen2.5", ""),
				('vanilj/Phi-4', "Phi", ""),
			]
	)
	bpy.types.Scene.user_prompt = bpy.props.StringProperty(name="User Prompt")

def unregister():
	bpy.utils.unregister_class(OBJECT_OT_SubmitPrompt)
	bpy.utils.unregister_class(OBJECT_PT_CustomPanel)
	bpy.utils.unregister_class(LLMAddonPreferences)

	del bpy.types.Scene.ai_model
	del bpy.types.Scene.user_prompt

# Import AI, LLM libraries
import openai
from ollama import chat
from ollama import ChatResponse
from openai import OpenAI

# OpenAI model
def openai_agent(prompt, system_prompt="You are coder for Blender python program", model=None, api_key=None):
	prefs = get_addon_prefs()
	if prefs is None and (model is None or api_key is None):
		raise ValueError("OpenAI API key and model are not configured, and preferences are unavailable.")
	resolved_model = model or (prefs.openai_model if prefs else "gpt-4o")
	resolved_api_key = api_key or get_openai_api_key(prefs)
	if not resolved_api_key:
		raise ValueError("OpenAI API key is not configured.")
	client = OpenAI(api_key=resolved_api_key)
	response = client.chat.completions.create(
		model=resolved_model,
		messages=[
			{
				"role": "system",
				"content": system_prompt,
			},
			{
				"role": "user",
				"content": prompt,
			},
		],
		temperature=0.1,
		max_tokens=1024,
		top_p=1
	)
	return response.choices[0].message.content

# code agent function
def check_safe_eval(express):
	tokens = express.split()

	try:
		if tokens.index("import") < 0:
			return 
		unsafe_libs = ["os", "shutil", "subprocess", "ctypes", "pickle", "http", "socket", "eval", "exec"]
		unsafe = False
		for lib in unsafe_libs:
			try:
				if tokens.index(lib) >= 0:
					unsafe = True
					break
			except ValueError:
				pass

		if unsafe:
			raise Exception(f"{express} is not safe.")
	except ValueError:
		pass
	return 

def preprocess_code(text: str) -> str:
	try:
		match = re.search(r'```python\n(.*?)```', text, re.DOTALL) # extract code from text between ```python\n and ```
		code = match.group(1).strip()
		code = code.replace('\t', '    ')
		code = textwrap.dedent(code)
		check_safe_eval(code)
		ast.parse(code)
	except IndentationError as e:
		print(f"IndentationError detected: {e}")
		code = ''
	except SyntaxError as e:
		print(f"SyntaxError detected: {e}")
		code = ''
	except Exception as e:
		print(f"Error: {e}")
		code = ''
	return code

def llm_agent(option, prompt):
    response = chat(
        model=option,
        messages=[{"role": "user", "content": prompt}]
    )
    if response and isinstance(response, ChatResponse):
        return response.message.content
    else:
        raise Exception("Failed to get a valid response from the model")

def gen_code(option, instruct_cmd, user_prompt):
	print(f"Selected Option: {option}")
	print(f"User Prompt: {user_prompt}")

	print(f'Calling {option} API...')
	output = ''
	try:
		if option == 'chatgpt':
			output = openai_agent(instruct_cmd + ': ' + user_prompt)
		else:
			output = llm_agent(option, instruct_cmd + ': ' + user_prompt)
		print(output)
	except Exception as api_error:
		print(f"API call failed: {api_error}")
		return False

	for i in range(3):
		try:
			# Ensure the model actually returned something before preprocessing.
			if not output or not str(output).strip():
				raise ValueError("Model output is empty; cannot extract code.")
			code = preprocess_code(output)
			# Distinguish preprocessing failures from genuinely empty model output.
			if not code.strip():
				raise ValueError("Failed to extract code from non-empty model output; preprocessing returned empty code.")
			exec(code)
			print("Code executed successfully.")
			return True
		except Exception as e:
			print(f"Error: {e}")
			error_fix_prompt = f"Fix the error {e} in {code}"
			try:
				if option == 'chatgpt':
					output = openai_agent(error_fix_prompt)
				else:
					output = llm_agent(option, error_fix_prompt)
				print(output)
			except ValueError as ve:
				print(f"API key configuration error during error recovery: {ve}. Please verify your API key settings in the add-on preferences.")
				break
			except Exception as recovery_error:
				print(f"Error during recovery attempt: {recovery_error}")
				break
	return False

if __name__ == "__main__":
	register()
