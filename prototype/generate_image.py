import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def generate_image(prompt):
  client = OpenAI()
  response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
  )

  image_url = response.data[0].url

  return image_url

def download_image(image_url):
  response = requests.get(image_url)
  img = Image.open(BytesIO(response.content))
  return img