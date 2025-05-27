import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)   
print(client.models.list())
print(f"Url:{client.base_url}")


