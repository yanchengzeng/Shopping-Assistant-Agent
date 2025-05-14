import base64
import json
import os
from openai import OpenAI
import requests
from dotenv import load_dotenv

from vector_db import query_image, query_text

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

product_json_schema = """{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "description": {"type": "string"},
    "brand": {"type": "string"},
    "category": {"type": "string"},
    "price": {"type": "integer"},
    "image_url": {"type": "string"},
    }
  },
  "required": ["name", "description", "brand", "category", "price"]
}"""

output_json_schema = """{
  "type": "object",
  "properties": {
    "type": {"type": "string"},
    "content": {"type": "string"},
    }
  },
  "required": ["type", "content"]
}"""

SYSTEM_PROMPT = (
    f"Your name is Mona. You are a helpful shopping assistant for an online shop. "
    f"You help users find products offered by this online shop. "
    f"After searching for the product, check if the found product information "
    f"matches what the user asks for. If the found product is not really relevant, explain to the customer nicely. "
    f"Display the product result in json format with the following schema {product_json_schema}"
    f"Your final output should always be in json format with the following schema {output_json_schema}. "
    f"If a product result needs to be shown, it should be shown within the content field in the final output; "
    f"otherwise the output message should go into the content field. "
    f"The type field should be 'text' or 'json' depending on the content."
)

uploaded_image_store = {}

def search_product_by_text(text: str):
    return query_text(text)

def search_product_by_image(image_id: str):
    image_encoded = uploaded_image_store.get(image_id)
    img_raw = base64.b64decode(image_encoded)
    return query_image(img_raw)


def call_function(name, args):
    if name == 'search_product_by_text':
        return search_product_by_text(**args)
    elif name == 'search_product_by_image':
        return search_product_by_image(**args)
    else:
        return ''


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_product_by_text",
            "description": "Search a product by text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                },
                "required": ["text"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_product_by_image",
            "description": "Search a product by image. Provide image ID shown in the user query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_id": {"type": "string"},
                },
                "required": ["image_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
]

def call_llm(chat_history) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=chat_history,
        tools=tools,
    )
    chat_history.append(response.choices[0].message)
    # keep calling tools till LLM finishes tool_calls responses
    while response.choices[0].finish_reason == 'tool_calls':
        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            result = call_function(name, args)
            chat_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=chat_history,
            tools=tools,
        )
        chat_history.append(response.choices[0].message)

    return response.choices[0].message.content

# retrieve response from LLM and append message to chat history
def handle_prompt_with_image(prompt: str, base_64_img: str, chat_history: list[dict]) -> str:
    image_id = f"img_{len(uploaded_image_store)}"
    uploaded_image_store[image_id] = base_64_img
    chat_history.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"{prompt} (image_id: {image_id})"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base_64_img}"}},
            ]
         }
    )
    return call_llm(chat_history)

def handle_prompt(prompt: str, chat_history: list[dict]) -> str:
    chat_history.append(
        {"role": "user", "content": prompt}
    )
    return call_llm(chat_history)

# command line interface for local testing
def chat_command_line():
    chat_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    user_message = input("Say something: ")
    assistant_message = handle_prompt(user_message, chat_messages)
    print(f'Assistant: {assistant_message}')
    while True:
        user_message = input("Follow up: ")
        assistant_message = handle_prompt(user_message, chat_messages)
        print(f'Assistant: {assistant_message}')