from google import genai
import os
from typing import List
from dotenv import load_dotenv

_ = load_dotenv()

# Configure the client (API key from env)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_embedding(text: str) -> List[float]:
    """Return embedding vector using the latest embedding model."""
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[text],  # must be a list of strings
    )
    if response.embeddings and response.embeddings[0].values is not None:
        return response.embeddings[0].values
    raise ValueError("Failed to retrieve embedding values from response")


if __name__ == "__main__":
    print(get_embedding("i am amir"))
