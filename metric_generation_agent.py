import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

current_directory = os.getcwd()
prompts_path = os.path.join(current_directory, "config/prompt")

# Load the metric extraction prompt
metric_prompt_path = os.path.join(prompts_path, "metric_generation.md")
with open(metric_prompt_path, "r", encoding='utf-8') as file:
    metric_extraction_prompt = file.read()

file_path = "C:\\Agent GCP\\all_extracted_data.json"

def read_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

startup_information = read_data(file_path)

def metric_extraction_agent(metric_extraction_prompt, startup_information):
    # Combine prompt and structured data for the model input
    full_input = (
        f"{metric_extraction_prompt}\n\n"
        "Here is the startup summary data in JSON format:\n"
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
metrics_json_str = metric_extraction_agent(metric_extraction_prompt, startup_information)
print(metrics_json_str)

# Save metrics to a JSON file
metrics_output_path = os.path.join(current_directory, "generated_metrics.json")
try:
    # The model output should be a JSON array/object; try to parse it before saving
    metrics_json_obj = json.loads(metrics_json_str)
except json.JSONDecodeError:
    print("Warning: Model output could not be parsed as JSON. Saving raw string output.")
    metrics_json_obj = metrics_json_str

with open(metrics_output_path, "w", encoding='utf-8') as f:
    json.dump(metrics_json_obj, f, indent=2, ensure_ascii=False)

print(f"Metrics saved to {metrics_output_path}")