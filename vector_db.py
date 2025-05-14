import base64
import io
import json
import os
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import chromadb
from chromadb.utils.embedding_functions.open_clip_embedding_function import OpenCLIPEmbeddingFunction
import numpy as np
from sqlalchemy.orm import Session
from storage.db_model import Product
from storage.databases import get_db
from storage.create_db import SAMPLE_DATA

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def describe_image(image_path):
    base64_image = encode_image_to_base64(image_path)
    response = openai_client.chat.completions.create(
        model="gpt-4.1",  # or "gpt-4-vision-preview"
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "I'm an online shop owner and I want a product description for this image. The product description should be a single paragraph for about 50 words"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()

vectore_db_client = chromadb.PersistentClient(path="data/my_chromadb")

text_collection = vectore_db_client.get_or_create_collection(
    name="product_catalog_text",
)

image_collection = vectore_db_client.get_or_create_collection(
    name="product_catalog_images",
    embedding_function=OpenCLIPEmbeddingFunction()
)

def add_images():
    image_folder = 'data/images/'
    ids = []
    metadatas = []
    images = []

    for idx, (filename, _) in enumerate(SAMPLE_DATA.items()):
        ids.append(f'{str(idx+1)}_img')
        with Image.open(os.path.join(image_folder, filename)) as img:
            images.append(np.array(img))
        metadatas.append({
            'item_id': str(idx),
            'img_category': SAMPLE_DATA[filename]['category'],
            'item_name': filename
        })

    image_collection.add(
        ids=ids,
        images=images,
        metadatas=metadatas
    )

    print(f"Total items in image collection: {image_collection.count()}")

def add_descriptions():
    ids = []
    documents = []
    metadatas = []

    for idx, (filename, _) in enumerate(SAMPLE_DATA.items()):
        ids.append(f'{str(idx+1)}_desc')
        documents.append(SAMPLE_DATA[filename]['desc'])
        metadatas.append({
            'item_id': str(idx),
            'img_category': SAMPLE_DATA[filename]['category'],
            'item_name': filename
        })

    text_collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Total items in text collection: {text_collection.count()}")


def find_product_from_db(product_id: int) -> Optional[dict]:
    engine = get_db()
    with Session(engine) as session:
        product = session.query(Product).filter(Product.id == product_id).first()
        if product:
            return product.as_dict()
        else:
            return None

def query_image(raw_image: bytes) -> dict:
    image = Image.open(io.BytesIO(raw_image)).convert("RGB")
    query_images = [np.array(image)]
    image_query_result = image_collection.query(
        query_images=query_images,
        n_results=1,
    )
    product_id = int(image_query_result['ids'][0][0].split('_')[0])
    return find_product_from_db(product_id)

def query_text(text: str) -> dict:
    query_texts = [text]
    text_query_result = text_collection.query(
        query_texts=query_texts,
        n_results=1,
    )
    product_id = int(text_query_result['ids'][0][0].split('_')[0])
    return find_product_from_db(product_id)


print(query_text('white tee'))