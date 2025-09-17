import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client() 
current_directory = os.getcwd()
prompts_path = os.path.join(current_directory, "config/prompt")

deal_notes_prompt_path = os.path.join(prompts_path, "deal_notes_generation.md")
with open(deal_notes_prompt_path, "r", encoding='utf-8') as file:
    deal_notes_prompt = file.read()

file_path = "C:\\Agent GCP\\all_extracted_data.json"

def read_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

startup_information = read_data(file_path)

def deal_notes_agent(deal_notes_prompt, startup_information):
    # Combine prompt and structured data for the model input
    full_input = (
        f"{deal_notes_prompt}\n\n"
        "Here is the extracted startup data in JSON format:\n"
        f"{json.dumps(startup_information, indent=2)}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [{"text": full_input}]
            }
        ]
    )
    return response.text

# Example usage:
summary = deal_notes_agent(deal_notes_prompt, startup_information)
print(summary)

