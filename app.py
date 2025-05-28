from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

class LLMInterface:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.system_message = """
You are an AI that generates high-quality React.js frontend code based on the given user instructions.

The input can be containing the following properties with user wishes and instructions:

  objectif
  layout
  theme // can be personalised with some colores usue them as palettes in a modern a beautiful way 
  composants // list of components to include
  style
  framework

  you have to follow it all and generate code based on it.
  If the user instruction list is empty or incomplete, generate a modern UI that best fits the available information and use MUI.

strict Rules !!! :
- Use all the instructions strictly to create a modern UI.
- Always output a complete React component code.
- Do not return lists, explanations, or anything except the complete React component code.
- Do not start with ```jsx or any code fences or texts ; output only the raw code.
- If the user instruction list is empty or incomplete, generate a modern UI that best fits the available information and use MUI.
- Use MUI components if no framework is defined.
- Ensure the code is production-ready, clean, and functional.
- do not import images cosider that we dont have any image in the project but u can bring from internet.
- Always use the sx prop or the styled API from MUI v5+ instead of makeStyles or withStyles, which are from the legacy @mui/styles package and incompatible with the default theme without extra setup.
- Avoid using framer-motion unless explicitly instructed, as it adds an extra dependency and may cause module resolution issues. Stick to MUI's built-in transitions or basic CSS for animations by default.
- Ensure all code is compatible with MUI v5, using ES6+ features and avoiding legacy MUI patterns.

Do not assume external dependencies are installed; prefer solutions with built-in React or MUI features unless the user confirms they want external libraries.
Output only the complete React component code implementing the requested page.
 
"""
        self.model = "Qwen/Qwen2.5-Coder-7B-Instruct"


    def query(self, prompt: str) -> str:
        payload = {
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "model": self.model
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}, {response.text}"

@app.route('/')
def home():
    return "Welcome to the SECOND AI Code Generator API (PORT 5005)!"

@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    api_url = "https://router.huggingface.co/nscale/v1/chat/completions"
    api_key = os.getenv("HF_API_KEY")

    if not api_key:
        return jsonify({"error": "API key is missing. Set it in the .env file."}), 500

    llm = LLMInterface(api_url, api_key)
    response = llm.query(prompt)

    cleaned_code = re.sub(r'^```[a-z]*\n([\s\S]*?)\n```$', r'\1', response.strip(), flags=re.MULTILINE)

    return jsonify({"code": cleaned_code})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
